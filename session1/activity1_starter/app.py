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

# TODO 1: add a region filter (st.selectbox or st.multiselect) and filter df
# TODO 2: add a category filter the same way

daily = df.groupby("date", as_index=False)["units"].sum()
fig = px.line(daily, x="date", y="units", title="Daily units")
st.plotly_chart(fig, width="stretch")

# TODO 3: add KPI cards with st.columns + st.metric (total units, revenue, # SKUs)
# TODO 4: add a second chart: top 10 SKUs by revenue (px.bar)
# TODO 5 (stretch): show the filtered rows in st.dataframe inside an st.expander
