"""Reusable chart builders. Each takes a DataFrame and returns a Plotly figure."""
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def daily_units_chart(df: pd.DataFrame) -> Figure:
    daily = df.groupby("date", as_index=False)["units"].sum()
    return px.line(daily, x="date", y="units", title="Daily units")


def top_skus_chart(df: pd.DataFrame, n: int = 10) -> Figure:
    top = df.groupby("sku", as_index=False)["revenue"].sum().nlargest(n, "revenue")
    return px.bar(top, x="sku", y="revenue", title=f"Top {n} SKUs by revenue")
