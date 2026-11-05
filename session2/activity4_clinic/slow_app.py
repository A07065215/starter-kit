"""Activity 4 starter: the Orders Explorer, SLOW ON PURPOSE.

Run from the kit root:   streamlit run session2/activity4_clinic/slow_app.py

Your job: use the stage timings in the sidebar to find the bottlenecks and fix
them one at a time. Record the total after each fix.
Do NOT peek at fast_app.py until your team has a diagnosis.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from timing import reset_timings, show_timings, stage

KIT = Path(__file__).resolve().parents[2]

st.set_page_config(page_title="Orders Explorer (slow)", layout="wide")
st.title("Orders Explorer (slow on purpose)")
reset_timings()

with stage("1 load csv"):
    df = pd.read_csv(KIT / "data" / "orders_large.csv")

with stage("2 parse dates"):
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.strftime("%Y-%m")

with stage("3 revenue (row by row)"):
    df["revenue"] = df.apply(lambda r: r["qty"] * r["unit_price"], axis=1)

with stage("4 join sku table"):
    skus = pd.read_csv(KIT / "data" / "sku_params.csv")
    df = df.merge(skus[["sku", "category"]], on="sku", how="left")

region = st.sidebar.selectbox("Region", ["All"] + sorted(df["region"].unique()))
status = st.sidebar.selectbox("Status", ["All"] + sorted(df["status"].unique()))

with stage("5 filter"):
    view = df.copy()
    if region != "All":
        view = view[view["region"] == region]
    if status != "All":
        view = view[view["status"] == status]

with stage("6 monthly totals (loop)"):
    rows = []
    for m in sorted(view["month"].unique()):
        rows.append({"month": m, "revenue": view[view["month"] == m]["revenue"].sum()})
    monthly = pd.DataFrame(rows)

with stage("7 top customers (loop)"):
    totals = {}
    for cid in view["customer_id"].unique():
        totals[cid] = view[view["customer_id"] == cid]["revenue"].sum()
    top = pd.Series(totals, name="revenue").nlargest(10).rename_axis("customer_id").reset_index()

with stage("8 charts"):
    st.plotly_chart(px.line(monthly, x="month", y="revenue", title="Monthly revenue"), width="stretch")
    st.plotly_chart(px.bar(top, x="customer_id", y="revenue", title="Top 10 customers"), width="stretch")

st.caption(f"{len(view):,} orders in view")
show_timings()
