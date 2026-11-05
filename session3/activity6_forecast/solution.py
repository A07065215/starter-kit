"""Activity 6 SOLUTION: demand forecast dashboard with a backtest scorecard.

Run from the kit root:   streamlit run session3/activity6_forecast/solution.py
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
    return np.tile(y[-SEASON:], int(np.ceil(h / SEASON)))[:h]


def _fit_ets(y):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ExponentialSmoothing(
            y.astype(float), trend="add", seasonal="add",
            seasonal_periods=SEASON, initialization_method="estimated",
        ).fit()


def _simulate(fit, h):
    """Simulate future paths; the seed keyword was renamed in newer statsmodels."""
    kw = dict(repetitions=500, error="add", anchor="end")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return np.asarray(fit.simulate(h, rng=0, **kw))
        except TypeError:
            return np.asarray(fit.simulate(h, random_state=0, **kw))


def ets(y, h):
    return np.asarray(_fit_ets(y).forecast(h))


MODELS = {"Naive": naive, "Seasonal naive": seasonal_naive, "ETS (Holt-Winters)": ets}


def wape(actual, pred):
    return float(np.abs(actual - pred).sum() / actual.sum())


def bias(actual, pred):
    return float((pred - actual).sum() / actual.sum())


def backtest(y, horizon, folds, models) -> pd.DataFrame:
    rows = []
    for k in range(folds):
        cut = len(y) - horizon * (folds - k)
        train, test = y[:cut], y[cut:cut + horizon]
        for name, fn in models.items():
            pred = fn(train, horizon)
            rows.append({"fold": k + 1, "model": name, "WAPE": wape(test, pred), "Bias": bias(test, pred)})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner="Backtesting models...")
def run_backtest(sku: str, horizon: int, folds: int = 4) -> pd.DataFrame:
    y = _series(sku)[1]
    return backtest(y, horizon, folds, MODELS)


@st.cache_data(show_spinner="Simulating prediction interval...")
def ets_interval(sku: str, horizon: int):
    y = _series(sku)[1]
    sims = _simulate(_fit_ets(y), horizon)
    lo, hi = np.percentile(sims, [10, 90], axis=1)
    total_lo, total_hi = np.percentile(sims.sum(axis=0), [10, 90])
    return lo, hi, float(total_lo), float(total_hi)


def _series(sku: str):
    hist = load_weekly().query("sku == @sku").sort_values("week_start")
    return hist, hist["units"].to_numpy(float)


# ---------------- UI ----------------
weekly = load_weekly()
sku = st.sidebar.selectbox("SKU", sorted(weekly["sku"].unique()), key="sku")
horizon = st.sidebar.slider("Forecast horizon (weeks)", 4, 12, 8, key="horizon")
model_name = st.sidebar.selectbox("Model to plot", list(MODELS), index=2, key="model")

hist, y = _series(sku)
future = pd.date_range(hist["week_start"].iloc[-1] + pd.Timedelta(weeks=1), periods=horizon, freq="W-MON")
lo, hi, total_lo, total_hi = ets_interval(sku, horizon)

fig = go.Figure()
fig.add_scatter(x=hist["week_start"].tail(104), y=y[-104:], name="History")
fig.add_scatter(x=future, y=MODELS[model_name](y, horizon), name=f"{model_name} forecast")
fig.add_scatter(x=future, y=hi, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
fig.add_scatter(x=future, y=lo, mode="lines", line=dict(width=0), fill="tonexty",
                name="ETS 80% interval", fillcolor="rgba(20,184,166,0.25)")
fig.update_layout(title=f"{sku}: weekly demand and forecast", hovermode="x unified")
st.plotly_chart(fig, width="stretch")

st.subheader("Backtest scorecard (4 rolling folds)")
bt = run_backtest(sku, horizon)
score = bt.groupby("model", as_index=False)[["WAPE", "Bias"]].mean().sort_values("WAPE")
shown = score.assign(**{"WAPE (%)": (score["WAPE"] * 100).round(1), "Bias (%)": (score["Bias"] * 100).round(1)})
st.dataframe(shown[["model", "WAPE (%)", "Bias (%)"]], hide_index=True, width="stretch")

best = score.iloc[0]
baseline = score.loc[score["model"] == "Seasonal naive", "WAPE"].iloc[0]
total = MODELS[model_name](y, horizon).sum()
st.success(
    f"{sku}: best backtest model is {best['model']} (WAPE {best['WAPE']:.1%}). "
    f"Plan for about {total:,.0f} units over the next {horizon} weeks "
    f"(80% range {total_lo:,.0f} to {total_hi:,.0f})."
)
if best["model"] == "Naive" or best["WAPE"] >= baseline:
    st.warning("The model does not beat the seasonal-naive baseline. Prefer the simpler one.")
