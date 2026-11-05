"""Tiny helper to time each stage of a Streamlit script.

    reset_timings()                 # once, at the top of the script
    with stage("1 load csv"):       # wrap each step you want to measure
        df = pd.read_csv(...)
    show_timings()                  # once, at the bottom (renders in the sidebar)
"""
import time
from contextlib import contextmanager

import pandas as pd
import streamlit as st


def reset_timings() -> None:
    st.session_state["timings"] = {}


@contextmanager
def stage(name: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        st.session_state.setdefault("timings", {})[name] = time.perf_counter() - t0


def show_timings() -> None:
    timings = st.session_state.get("timings", {})
    if not timings:
        return
    st.sidebar.subheader("Stage timings (seconds)")
    st.sidebar.dataframe(pd.Series(timings, name="seconds").round(3), width="stretch")
    st.sidebar.metric("Total", f"{sum(timings.values()):.2f} s")
