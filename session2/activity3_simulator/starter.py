"""Activity 3 starter: What-if inventory simulator.

Run from the kit root:   streamlit run session2/activity3_simulator/starter.py

Formulas (protection period T = lead time + review period):
    z             = NormalDist().inv_cdf(service_level)
    safety_stock  = z * sigma_daily * sqrt(T)
    reorder_point = mean_daily * T + safety_stock
"""
from math import sqrt
from pathlib import Path
from statistics import NormalDist

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


stats = load_stats().set_index("sku")

if "scenarios" not in st.session_state:
    st.session_state.scenarios = []


def reset_scenarios():
    st.session_state.scenarios = []


# TODO 5: write save_scenario() that appends a dict (sku, lead, review, service,
#         safety stock, reorder point) to st.session_state.scenarios.
#         Then pass it to the form button:  on_click=save_scenario


with st.form("params"):
    sku = st.selectbox("SKU", stats.index, key="sku")
    lead = st.number_input("Lead time (days)", 1, 60, 7, key="lead")
    review = st.number_input("Review period (days)", 0, 30, 7, key="review")
    service = st.slider("Service level", 0.80, 0.999, 0.95, 0.005, key="service")
    st.form_submit_button("Simulate")

mean_d = stats.loc[sku, "mean_daily"]
std_d = stats.loc[sku, "std_daily"]

# TODO 1: z = NormalDist().inv_cdf(service)
# TODO 2: safety_stock = z * std_d * sqrt(lead + review)
# TODO 3: reorder_point = mean_d * (lead + review) + safety_stock
z = safety_stock = reorder_point = 0.0  # replace these three lines

c1, c2, c3 = st.columns(3)
c1.metric("z-score", f"{z:.2f}")
c2.metric("Safety stock (units)", f"{safety_stock:,.0f}")
c3.metric("Reorder point (units)", f"{reorder_point:,.0f}")

st.subheader("Saved scenarios")
# TODO 4: show st.session_state.scenarios as a DataFrame (st.dataframe)
st.button("Reset", on_click=reset_scenarios)

# TODO 6 (stretch): simulate 90 days of random demand and count stockout days.
#   Hint: rng.normal(mean_d, std_d) per day, orders arrive `lead` days after
#   inventory position <= reorder_point.
