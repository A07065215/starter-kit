"""Generate every dataset used by the activities.

Usage:  python make_data.py        (writes ./data/*, takes ~15 seconds)

Everything is seeded, so every student gets identical files.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

N_SKUS = 12
N_CUSTOMERS = 500
N_ORDERS = 500_000
SKUS = [f"SKU-{i:02d}" for i in range(1, N_SKUS + 1)]
CATEGORIES = ["Beverages", "Snacks", "Dairy", "Bakery"]
REGIONS = {"North": 0.35, "South": 0.25, "East": 0.22, "West": 0.18}
WAREHOUSES = ["MTY", "GDL", "CDMX"]


def make_skus() -> pd.DataFrame:
    cost = rng.uniform(8, 60, N_SKUS).round(2)
    return pd.DataFrame({
        "sku": SKUS,
        "category": [CATEGORIES[i % 4] for i in range(N_SKUS)],
        "unit_cost": cost,
        "unit_price": (cost * rng.uniform(1.25, 1.7, N_SKUS)).round(2),
        "unit_volume_m3": rng.uniform(0.01, 0.08, N_SKUS).round(3),
        "min_order_qty": rng.choice([24, 48, 100], N_SKUS),
        "lead_time_days": rng.integers(3, 15, N_SKUS),
        "on_hand": rng.integers(200, 1500, N_SKUS),
        "base_daily_demand": rng.uniform(20, 90, N_SKUS).round(1),  # internal, not exported
    })


def make_sales_daily(skus: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    t = np.arange(len(dates))
    dow = np.array([0.9, 0.95, 1.0, 1.0, 1.1, 1.25, 0.8])[np.asarray(dates.dayofweek)]
    season = 1 + 0.2 * np.sin(2 * np.pi * (t - 60) / 365.25)
    trend = 1 + 0.0004 * t
    frames = []
    for s in skus.itertuples():
        for region, w in REGIONS.items():
            lam = s.base_daily_demand * w * dow * season * trend
            units = rng.poisson(lam * rng.gamma(25, 1 / 25, len(dates)))
            frames.append(pd.DataFrame({
                "date": dates, "sku": s.sku, "category": s.category,
                "region": region, "units": units, "unit_price": s.unit_price,
            }))
    df = pd.concat(frames, ignore_index=True)
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    return df.sort_values(["date", "sku", "region"]).reset_index(drop=True)


def make_weekly_demand(skus: pd.DataFrame, n_skus: int = 8) -> pd.DataFrame:
    weeks = pd.date_range("2023-01-02", periods=156, freq="W-MON")
    t = np.arange(len(weeks))
    frames = []
    for s in skus.head(n_skus).itertuples():
        level = s.base_daily_demand * 7 * (1 + 0.003 * t)
        seasonal = 1 + 0.25 * np.sin(2 * np.pi * (t - 10) / 52) + 0.08 * np.sin(4 * np.pi * t / 52)
        promo = (rng.random(len(t)) < 0.08).astype(int)
        noise = rng.normal(1, 0.07, len(t))
        units = np.round(level * seasonal * (1 + 0.4 * promo) * noise).astype(int)
        frames.append(pd.DataFrame({
            "week_start": weeks, "sku": s.sku, "units": units, "promo": promo,
            "price": np.where(promo == 1, s.unit_price * 0.85, s.unit_price).round(2),
        }))
    return pd.concat(frames, ignore_index=True)


def make_orders(skus: pd.DataFrame) -> pd.DataFrame:
    sku_idx = rng.integers(0, N_SKUS, N_ORDERS)
    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 731, N_ORDERS), unit="D")
    cust = rng.integers(1, N_CUSTOMERS + 1, N_ORDERS)
    return pd.DataFrame({
        "order_id": np.arange(1, N_ORDERS + 1),
        "order_date": dates.strftime("%Y-%m-%d"),
        "customer_id": "C" + pd.Series(cust).astype(str).str.zfill(4),
        "sku": np.array(SKUS)[sku_idx],
        "region": rng.choice(list(REGIONS), N_ORDERS, p=list(REGIONS.values())),
        "warehouse": rng.choice(WAREHOUSES, N_ORDERS),
        "qty": np.minimum(rng.geometric(0.08, N_ORDERS), 120),
        "unit_price": (skus["unit_price"].to_numpy()[sku_idx] * rng.uniform(0.95, 1.05, N_ORDERS)).round(2),
        "status": rng.choice(["delivered", "shipped", "cancelled", "returned"], N_ORDERS,
                             p=[0.86, 0.06, 0.05, 0.03]),
        "ship_days": rng.integers(1, 9, N_ORDERS),
    })


def make_inventory(skus: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for s in skus.itertuples():
        for wh in WAREHOUSES:
            rop = int(rng.integers(100, 400))
            rows.append({"sku": s.sku, "warehouse": wh,
                         "on_hand": int(rng.integers(30, 700)), "reorder_point": rop,
                         "updated_at": "2025-12-31"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    skus = make_skus()
    public_skus = skus.drop(columns=["base_daily_demand"])
    public_skus.to_csv(OUT / "sku_params.csv", index=False)
    make_sales_daily(skus).to_csv(OUT / "sales_daily.csv", index=False)
    make_weekly_demand(skus).to_csv(OUT / "weekly_demand.csv", index=False)
    orders = make_orders(skus)
    orders.to_csv(OUT / "orders_large.csv", index=False)

    db = OUT / "supply.db"
    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as con:
        public_skus.drop(columns=["on_hand"]).to_sql("skus", con, index=False)
        orders.head(30_000).to_sql("orders", con, index=False)
        make_inventory(skus).to_sql("inventory", con, index=False)

    for f in sorted(OUT.iterdir()):
        print(f"{f.name:22s} {f.stat().st_size / 1e6:8.2f} MB")
