"""Activity 4 SOLUTION: the same Orders Explorer, far faster.

Run from the kit root:   streamlit run session2/activity4_clinic/fast_app.py

What changed (each fix is worth timing on its own):
  1. cache_data on loading           -> the CSV is read once per server, not per click
  2. CSV -> parquet + category dtypes -> 10x faster, much less memory
  3. vectorized revenue               -> no row-by-row apply
  4. groupby instead of Python loops  -> monthly totals and top customers in ms
  5. cache_data on the filtered aggregates -> same filter twice = instant
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from timing import reset_timings, show_timings, stage

KIT = Path(__file__).resolve().parents[2]
CSV = KIT / "data" / "orders_large.csv"
PARQUET = KIT / "data" / "orders_large.parquet"

st.set_page_config(page_title="Orders Explorer (fast)", layout="wide")
st.title("Orders Explorer (fast)")
reset_timings()


@st.cache_data(show_spinner="Loading orders...")
def load_orders() -> pd.DataFrame:
    if not PARQUET.exists():  # one-time conversion; commit the parquet in a real project
        cats = {c: "category" for c in ["customer_id", "sku", "region", "warehouse", "status"]}
        pd.read_csv(CSV, parse_dates=["order_date"], dtype=cats).to_parquet(PARQUET)
    df = pd.read_parquet(PARQUET)
    df["revenue"] = df["qty"] * df["unit_price"]
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df


@st.cache_data
def aggregates(region: str, status: str):
    df = load_orders()
    if region != "All":
        df = df[df["region"] == region]
    if status != "All":
        df = df[df["status"] == status]
    monthly = df.groupby("month", as_index=False, observed=True)["revenue"].sum()
    top = (df.groupby("customer_id", observed=True)["revenue"].sum()
             .nlargest(10).reset_index())
    return monthly, top, len(df)


with stage("1 load (cached)"):
    df = load_orders()

region = st.sidebar.selectbox("Region", ["All"] + sorted(df["region"].unique()))
status = st.sidebar.selectbox("Status", ["All"] + sorted(df["status"].unique()))

with stage("2 aggregate (cached)"):
    monthly, top, n = aggregates(region, status)

with stage("3 charts"):
    st.plotly_chart(px.line(monthly, x="month", y="revenue", title="Monthly revenue"), width="stretch")
    st.plotly_chart(px.bar(top, x="customer_id", y="revenue", title="Top 10 customers"), width="stretch")

st.caption(f"{n:,} orders in view")
show_timings()
