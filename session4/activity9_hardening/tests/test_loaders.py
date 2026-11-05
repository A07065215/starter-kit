"""Unit tests for pure functions: fast, no browser, no Streamlit runtime needed."""
import pandas as pd
import plotly.graph_objects as go

from components.charts import daily_units_chart, top_skus_chart
from data.loaders import clean_sales


def make_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-01-02", "2025-01-03"]),
        "sku": ["A", "A", "B", "B"],
        "category": ["x", "x", "y", "y"],
        "region": ["North"] * 4,
        "units": [10, 10, -5, 4],
        "unit_price": [2.0, 2.0, 3.0, 3.0],
    })


def test_clean_sales_drops_duplicates_and_negative_units():
    out = clean_sales(make_df())
    assert len(out) == 2
    assert (out["units"] >= 0).all()


def test_clean_sales_computes_revenue():
    out = clean_sales(make_df())
    assert out.loc[out["sku"] == "A", "revenue"].iloc[0] == 20.0


def test_charts_return_figures_with_data():
    out = clean_sales(make_df())
    for fig in (daily_units_chart(out), top_skus_chart(out)):
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
