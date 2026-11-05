import streamlit as st

from components.charts import daily_units_chart, top_skus_chart
from data.loaders import load_sales

st.set_page_config(page_title="Sales Explorer", layout="wide")
st.title("Sales Explorer")

df = load_sales()

all_regions = sorted(df["region"].unique())
all_categories = sorted(df["category"].unique())

with st.sidebar:
    regions = st.multiselect("Region", all_regions, default=all_regions, key="regions")
    categories = st.multiselect("Category", all_categories, default=all_categories, key="categories")

view = df[df["region"].isin(regions) & df["category"].isin(categories)]

if view.empty:
    st.warning("No data for this selection. Pick at least one region and one category.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Total units", f"{view['units'].sum():,}")
c2.metric("Revenue", f"${view['revenue'].sum():,.0f}")
c3.metric("SKUs", view["sku"].nunique())

st.plotly_chart(daily_units_chart(view), width="stretch")
st.plotly_chart(top_skus_chart(view), width="stretch")

with st.expander("Show filtered rows"):
    st.dataframe(view, width="stretch")
