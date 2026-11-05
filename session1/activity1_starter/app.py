"""Activity 1 starter: a deliberately notebook-style Streamlit app.

Goal (30 min): run it, finish the TODOs, push it to GitHub and deploy it
on Streamlit Community Cloud. Everything is in ONE file on purpose:
Activity 2 refactors it into modules.

Run from the kit root:   streamlit run session1/activity1_starter/app.py

When you move this app to YOUR OWN repo: copy data/sales_daily.csv next to
app.py and change DATA to Path(__file__).parent / "sales_daily.csv".
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[2] / "data" / "sales_daily.csv"

st.set_page_config(page_title="Sales Explorer", layout="wide")
st.title("Sales Explorer")

df = pd.read_csv(DATA, parse_dates=["date"])

all_regions = sorted(df["region"].unique())
all_categories = sorted(df["category"].unique())

with st.sidebar:
    regions = st.multiselect("Region", all_regions, default=all_regions)
    categories = st.multiselect("Category", all_categories, default=all_categories)

view = df[df["region"].isin(regions) & df["category"].isin(categories)]

if view.empty:
    st.warning("No data for this selection. Pick at least one region and one category.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Total units", f"{view['units'].sum():,}")
c2.metric("Revenue", f"${view['revenue'].sum():,.0f}")
c3.metric("SKUs", view["sku"].nunique())

daily = view.groupby("date", as_index=False)["units"].sum()
fig = px.line(daily, x="date", y="units", title="Daily units")
st.plotly_chart(fig, width="stretch")

top_skus = (
    view.groupby("sku", as_index=False)["revenue"]
    .sum()
    .nlargest(10, "revenue")
    .sort_values("revenue")
)
top_fig = px.bar(
    top_skus,
    x="revenue",
    y="sku",
    orientation="h",
    title="Top 10 SKUs by revenue",
)
st.plotly_chart(top_fig, width="stretch")

with st.expander("Show filtered rows"):
    st.dataframe(view, width="stretch")
