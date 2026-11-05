from pathlib import Path

import pandas as pd
import streamlit as st

DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "sales_daily.csv"


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    out = df.drop_duplicates().copy()
    out = out[out["units"] >= 0]
    out["revenue"] = (out["units"] * out["unit_price"]).round(2)
    return out.reset_index(drop=True)


@st.cache_data(show_spinner="Loading sales...")
def load_sales(path: str | Path = DEFAULT_PATH) -> pd.DataFrame:
    return clean_sales(pd.read_csv(path, parse_dates=["date"]))
