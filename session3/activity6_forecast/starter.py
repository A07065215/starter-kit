"""Activity 6 starter: demand forecast dashboard.

Run from the kit root:   streamlit run session3/activity6_forecast/starter.py

You get: data loading, a SKU selector and a naive forecast.
You build: seasonal naive, ETS, a rolling backtest scorecard, an interval,
a horizon control and a one-sentence takeaway.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing

KIT = Path(__file__).resolve().parents[2]
SEASON = 52

st.set_page_config(page_title="Demand forecast", layout="wide")
st.title("Demand forecast")


@st.cache_data
def load_weekly() -> pd.DataFrame:
    return pd.read_csv(KIT / "data" / "weekly_demand.csv", parse_dates=["week_start"])


# ---- models: (history: np.ndarray, horizon: int) -> np.ndarray of length horizon ----
def naive(y, h):
    return np.repeat(y[-1], h)


def seasonal_naive(y, h):
    # TODO 1: the next h weeks equal the same weeks one season (52 weeks) ago.
    #   Hint: y[-SEASON:] holds the last 52 weeks; the first h of them line up.
    raise NotImplementedError


def ets(y, h):
    # TODO 2: Holt-Winters with additive trend and seasonality:
    #   fit = ExponentialSmoothing(y.astype(float), trend="add", seasonal="add",
    #                              seasonal_periods=SEASON, initialization_method="estimated").fit()
    #   return np.asarray(fit.forecast(h))
    raise NotImplementedError


def wape(actual, pred):
    return float(np.abs(actual - pred).sum() / actual.sum())


def bias(actual, pred):
    return float((pred - actual).sum() / actual.sum())


def backtest(y, horizon, folds, models):
    # TODO 3: rolling origin. For fold k in range(folds):
    #   cut = len(y) - horizon * (folds - k); train = y[:cut]; test = y[cut:cut + horizon]
    #   for each model: pred = fn(train, horizon); record fold, model, wape, bias
    #   return a DataFrame
    raise NotImplementedError


weekly = load_weekly()
sku = st.sidebar.selectbox("SKU", sorted(weekly["sku"].unique()))
# TODO 4: add a horizon slider (4..12 weeks, default 8) in the sidebar
horizon = 8

hist = weekly[weekly["sku"] == sku].sort_values("week_start")
y = hist["units"].to_numpy(float)
future_dates = pd.date_range(hist["week_start"].iloc[-1] + pd.Timedelta(weeks=1), periods=horizon, freq="W-MON")

fc = naive(y, horizon)
fig = go.Figure()
fig.add_scatter(x=hist["week_start"].tail(104), y=y[-104:], name="History")
fig.add_scatter(x=future_dates, y=fc, name="Naive forecast")
# TODO 5: add the ETS forecast and a prediction interval.
#   Hint: fit.simulate(horizon, repetitions=500, error="add", anchor="end", rng=0)  # older statsmodels: random_state=0
#   returns shape (horizon, 500); np.percentile(sims, [10, 90], axis=1) gives the band.
fig.update_layout(title=f"{sku}: weekly demand and forecast", hovermode="x unified")
st.plotly_chart(fig, width="stretch")

st.subheader("Backtest scorecard")
st.info("TODO 3: show mean WAPE and bias per model vs. the baselines.")

# TODO 6: write the one-sentence takeaway a planner could act on, e.g.
#   st.success(f"Order for ~{total:,.0f} units over the next {horizon} weeks (80% range ...)")
