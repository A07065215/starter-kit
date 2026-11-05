"""Activity 7 SOLUTION: replenishment optimizer (LP with PuLP).

Run from the kit root:   streamlit run session3/activity7_optimizer/solution.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import pulp as pl
import streamlit as st

KIT = Path(__file__).resolve().parents[2]

st.set_page_config(page_title="Replenishment optimizer", layout="wide")
st.title("Replenishment optimizer")


@st.cache_data
def load_inputs(horizon: int) -> pd.DataFrame:
    weekly = pd.read_csv(KIT / "data" / "weekly_demand.csv", parse_dates=["week_start"])
    params = pd.read_csv(KIT / "data" / "sku_params.csv").set_index("sku")
    rows = []
    for sku, g in weekly.groupby("sku"):
        y = g.sort_values("week_start")["units"].to_numpy(float)
        rows.append({"sku": sku, "forecast": y[-52:][:horizon].sum()})  # seasonal naive stand-in
    df = pd.DataFrame(rows).set_index("sku").join(params)
    df["need"] = (df["forecast"] - df["on_hand"]).clip(lower=0).round()
    df["penalty"] = df["unit_price"] * 1.5
    return df.reset_index()


def optimize(df: pd.DataFrame, budget: float, capacity: float, service_floor: float):
    """Return a plan DataFrame, or None if the problem is infeasible."""
    prob = pl.LpProblem("replenishment", pl.LpMinimize)
    q = {s: pl.LpVariable("q_" + s.replace("-", "_"), 0) for s in df["sku"]}
    u = {s: pl.LpVariable("u_" + s.replace("-", "_"), 0) for s in df["sku"]}
    rows = list(df.itertuples())

    prob += pl.lpSum(r.unit_cost * q[r.sku] + r.penalty * u[r.sku] for r in rows)
    for r in rows:
        prob += u[r.sku] >= r.need - q[r.sku]
        prob += q[r.sku] >= service_floor * r.need
    prob += pl.lpSum(r.unit_cost * q[r.sku] for r in rows) <= budget, "budget"
    prob += pl.lpSum(r.unit_volume_m3 * q[r.sku] for r in rows) <= capacity, "capacity"

    prob.solve(pl.PULP_CBC_CMD(msg=False))
    if pl.LpStatus[prob.status] != "Optimal":
        return None
    out = df[["sku", "need", "unit_cost"]].copy()
    out["order_qty"] = [round(q[s].value() or 0) for s in out["sku"]]
    out["shortage"] = [round(u[s].value() or 0) for s in out["sku"]]
    out["spend"] = out["order_qty"] * out["unit_cost"]
    return out.drop(columns="unit_cost")


horizon = st.sidebar.slider("Horizon (weeks)", 4, 12, 8)
df = load_inputs(horizon)
full_cost = float((df["need"] * df["unit_cost"]).sum())
full_volume = float((df["need"] * df["unit_volume_m3"]).sum())

budget_pct = st.sidebar.slider("Budget (% of full-need cost)", 20, 120, 60, key="budget_pct")
cap_pct = st.sidebar.slider("Capacity (% of full-need volume)", 20, 120, 80, key="cap_pct")
service = st.sidebar.slider("Minimum service per SKU", 0.0, 1.0, 0.0, 0.05, key="service")

budget, capacity = full_cost * budget_pct / 100, full_volume * cap_pct / 100
st.caption(f"Full need costs ${full_cost:,.0f} and takes {full_volume:,.1f} m3. "
           f"Budget ${budget:,.0f}, capacity {capacity:,.1f} m3.")

plan = optimize(df, budget, capacity, service)
if plan is None:
    st.error("No feasible plan: the minimum service is too high for this budget or capacity. "
             "Lower the service floor or raise the budget.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Total spend", f"${plan['spend'].sum():,.0f}")
c2.metric("Units ordered", f"{plan['order_qty'].sum():,.0f}")
c3.metric("Units short", f"{plan['shortage'].sum():,.0f}")
st.dataframe(plan, hide_index=True, width="stretch")


@st.cache_data
def tradeoff(horizon: int, cap_pct: int) -> pd.DataFrame:
    d = load_inputs(horizon)
    fc = float((d["need"] * d["unit_cost"]).sum())
    cap = float((d["need"] * d["unit_volume_m3"]).sum()) * cap_pct / 100
    rows = []
    for pct in range(20, 121, 10):
        res = optimize(d, fc * pct / 100, cap, 0.0)
        rows.append({"Budget (% of full need)": pct, "Units short": res["shortage"].sum()})
    return pd.DataFrame(rows)


st.subheader("Cost vs. service trade-off")
st.plotly_chart(px.line(tradeoff(horizon, cap_pct), x="Budget (% of full need)", y="Units short", markers=True),
                width="stretch")
st.caption("Where the curve flattens, extra budget stops buying service: capacity is the binding constraint.")
