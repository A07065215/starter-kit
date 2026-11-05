"""Activity 3 SOLUTION: What-if inventory simulator.

Run from the kit root:   streamlit run session2/activity3_simulator/solution.py
"""
from math import sqrt
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_daily.csv"

st.set_page_config(page_title="Inventory what-if", layout="wide")
st.title("Inventory what-if simulator")


@st.cache_data
def load_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["date"])
    daily = df.groupby(["sku", "date"], as_index=False)["units"].sum()
    return daily.groupby("sku")["units"].agg(mean_daily="mean", std_daily="std").reset_index()


def policy(mean_d: float, std_d: float, lead: int, review: int, service: float) -> dict:
    z = NormalDist().inv_cdf(service)
    protection = lead + review
    safety = z * std_d * sqrt(protection)
    return {"z": z, "safety_stock": safety, "reorder_point": mean_d * protection + safety}


def simulate_stockouts(mean_d, std_d, rop, order_qty, lead, days=90, seed=0):
    """(s, Q) policy: when inventory position <= rop, order order_qty (arrives after `lead` days)."""
    rng = np.random.default_rng(seed)
    on_hand, pipeline = rop + order_qty, {}
    stockout_days = short = total = 0
    for day in range(days):
        on_hand += pipeline.pop(day, 0)
        demand = max(0, int(round(rng.normal(mean_d, std_d))))
        served = min(on_hand, demand)
        total += demand
        short += demand - served
        stockout_days += demand > on_hand
        on_hand -= served
        if on_hand + sum(pipeline.values()) <= rop:
            pipeline[day + lead] = pipeline.get(day + lead, 0) + order_qty
    return stockout_days, (1 - short / total) if total else 1.0


stats = load_stats().set_index("sku")

if "scenarios" not in st.session_state:
    st.session_state.scenarios = []


def current_policy() -> dict:
    s = st.session_state
    p = policy(stats.loc[s.sku, "mean_daily"], stats.loc[s.sku, "std_daily"], s.lead, s.review, s.service)
    return {"SKU": s.sku, "Lead": s.lead, "Review": s.review, "Service": s.service,
            "Safety stock": round(p["safety_stock"]), "Reorder point": round(p["reorder_point"])}


def save_scenario():
    st.session_state.scenarios.append(current_policy())


def reset_scenarios():
    st.session_state.scenarios = []


with st.form("params"):
    sku = st.selectbox("SKU", stats.index, key="sku")
    lead = st.number_input("Lead time (days)", 1, 60, 7, key="lead")
    review = st.number_input("Review period (days)", 0, 30, 7, key="review")
    service = st.slider("Service level", 0.80, 0.999, 0.95, 0.005, key="service")
    st.form_submit_button("Save scenario", on_click=save_scenario)

mean_d, std_d = stats.loc[sku, "mean_daily"], stats.loc[sku, "std_daily"]
p = policy(mean_d, std_d, lead, review, service)

c1, c2, c3 = st.columns(3)
c1.metric("z-score", f"{p['z']:.2f}")
c2.metric("Safety stock (units)", f"{p['safety_stock']:,.0f}")
c3.metric("Reorder point (units)", f"{p['reorder_point']:,.0f}")

st.subheader("Saved scenarios")
if st.session_state.scenarios:
    st.dataframe(pd.DataFrame(st.session_state.scenarios), width="stretch", hide_index=True)
else:
    st.caption("Press 'Save scenario' to compare settings side by side.")
st.button("Reset", on_click=reset_scenarios)

with st.expander("Stretch: simulate 90 days of random demand"):
    order_qty = st.number_input("Order quantity", 10, 5000, int(mean_d * 14), key="order_qty")
    stockouts, fill = simulate_stockouts(mean_d, std_d, p["reorder_point"], order_qty, int(lead))
    m1, m2 = st.columns(2)
    m1.metric("Stockout days (of 90)", int(stockouts))
    m2.metric("Fill rate", f"{fill:.1%}")
