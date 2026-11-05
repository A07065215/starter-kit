"""Data loading and cleaning. No UI code except the cache decorator."""
import os
from pathlib import Path

import pandas as pd
import streamlit as st

# In your own repo, point this at the CSV that lives next to your app.
DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "sales_daily.csv"


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function (easy to unit-test): drop duplicates and negative units."""
    out = df.drop_duplicates().copy()
    out = out[out["units"] >= 0]
    out["revenue"] = (out["units"] * out["unit_price"]).round(2)
    return out.reset_index(drop=True)


@st.cache_data(show_spinner="Loading sales...")
def load_sales(path: str | None = None) -> pd.DataFrame:
    p = Path(path or os.environ.get("SALES_CSV", DEFAULT_PATH))
    return clean_sales(pd.read_csv(p, parse_dates=["date"]))
