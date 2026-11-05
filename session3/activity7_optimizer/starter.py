"""Activity 7 starter: replenishment optimizer.

Run from the kit root:   streamlit run session3/activity7_optimizer/starter.py

You get: next-N-weeks demand per SKU (seasonal-naive stand-in for your Activity 6
forecast), sliders and the LP variables. You build: objective, constraints,
infeasibility message and the cost-vs-service chart.

Model:  decide q[s] (order qty) and u[s] (shortage)
    minimize   sum(unit_cost[s] * q[s] + penalty[s] * u[s])
    subject to u[s] >= need[s] - q[s]               (shortage definition)
               q[s] >= service_floor * need[s]      (minimum service)
               sum(unit_cost[s] * q[s]) <= budget
               sum(unit_volume_m3[s] * q[s]) <= capacity
"""
from pathlib import Path

import numpy as np
import pandas as pd
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
        rows.append({"sku": sku, "forecast": y[-52:][:horizon].sum()})  # seasonal naive
    df = pd.DataFrame(rows).set_index("sku").join(params)
    df["need"] = (df["forecast"] - df["on_hand"]).clip(lower=0).round()
    df["penalty"] = df["unit_price"] * 1.5  # lost-sale cost per missing unit
    return df.reset_index()


def optimize(df: pd.DataFrame, budget: float, capacity: float, service_floor: float):
    prob = pl.LpProblem("replenishment", pl.LpMinimize)
    q = {s: pl.LpVariable("q_" + s.replace("-", "_"), 0) for s in df["sku"]}
    u = {s: pl.LpVariable("u_" + s.replace("-", "_"), 0) for s in df["sku"]}
    # TODO 1: objective:  prob += pl.lpSum(...)
    # TODO 2: for each row add the two per-SKU constraints (shortage, service floor)
    # TODO 3: add the budget and capacity constraints
    # TODO 4: prob.solve(pl.PULP_CBC_CMD(msg=False)); return None unless
    #         pl.LpStatus[prob.status] == "Optimal"; otherwise return a DataFrame
    #         with sku, need, order_qty, shortage, spend
    raise NotImplementedError


horizon = st.sidebar.slider("Horizon (weeks)", 4, 12, 8)
df = load_inputs(horizon)
full_cost = float((df["need"] * df["unit_cost"]).sum())
full_volume = float((df["need"] * df["unit_volume_m3"]).sum())

budget_pct = st.sidebar.slider("Budget (% of full-need cost)", 20, 120, 60)
cap_pct = st.sidebar.slider("Capacity (% of full-need volume)", 20, 120, 80)
service = st.sidebar.slider("Minimum service per SKU", 0.0, 1.0, 0.0, 0.05)

budget, capacity = full_cost * budget_pct / 100, full_volume * cap_pct / 100
st.caption(f"Full need costs ${full_cost:,.0f} and takes {full_volume:,.1f} m3. "
           f"Budget ${budget:,.0f}, capacity {capacity:,.1f} m3.")

try:
    plan = optimize(df, budget, capacity, service)
except NotImplementedError:
    st.info("Implement optimize() (TODOs 1-4) to see the recommended plan.")
    st.stop()

if plan is None:
    st.error("No feasible plan: the minimum service is too high for this budget or capacity. "
             "Lower the service floor or raise the budget.")
    st.stop()

# TODO 5: show metrics (total spend, units short) and the plan table
# TODO 6: chart the cost-vs-service trade-off: loop over budget % from 20 to 120,
#         re-solve (service floor 0) and plot units short vs. budget
