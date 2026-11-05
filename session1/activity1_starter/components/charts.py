import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def daily_units_chart(df: pd.DataFrame) -> Figure:
    daily = df.groupby("date", as_index=False)["units"].sum()
    return px.line(daily, x="date", y="units", title="Daily units")


def top_skus_chart(df: pd.DataFrame) -> Figure:
    top_skus = (
        df.groupby("sku", as_index=False)["revenue"]
        .sum()
        .nlargest(10, "revenue")
        .sort_values("revenue")
    )
    return px.bar(
        top_skus,
        x="revenue",
        y="sku",
        orientation="h",
        title="Top 10 SKUs by revenue",
    )
