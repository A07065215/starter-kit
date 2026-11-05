"""Activity 5 SOLUTION: live data with graceful failure.

Run from the kit root:   streamlit run session2/activity5_live_data/solution.py
"""
from pathlib import Path

import requests
import streamlit as st

DB = Path(__file__).resolve().parents[2] / "data" / "supply.db"
FX_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=MXN"

st.set_page_config(page_title="Live data", layout="wide")
st.title("Live data, graceful failure")


def get_secret(name: str, default=None):
    """st.secrets raises if there is no secrets.toml; fall back gracefully."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


# ---------------- Part A: database ----------------
st.header("A. Inventory below reorder point")
SQL = """
SELECT sku, warehouse, on_hand, reorder_point, reorder_point - on_hand AS gap
FROM inventory
WHERE on_hand < reorder_point
ORDER BY gap DESC
"""
try:
    conn = st.connection("supply", type="sql", url=f"sqlite:///{DB}")
    low = conn.query(SQL, ttl=600)
    st.metric("Items below reorder point", len(low))
    st.dataframe(low, width="stretch", hide_index=True)
except Exception:
    st.error("The inventory database is unavailable right now. Please try again later.")
    st.stop()

# ---------------- Part B: API ----------------
st.header("B. USD to MXN rate (public API)")


@st.cache_data(ttl=3600, show_spinner="Fetching exchange rate...")
def fetch_rate() -> float:
    resp = requests.get(FX_URL, timeout=5)
    resp.raise_for_status()
    return float(resp.json()["rates"]["MXN"])


try:
    rate = fetch_rate()
    st.metric("USD/MXN", f"{rate:.2f}")
    inv_value = (low["gap"].sum() * 25.0) * rate  # illustrative: gap units at $25 each
    st.caption(f"Illustrative replenishment value of the gap: ${inv_value:,.0f} MXN")
except (requests.RequestException, KeyError, ValueError):
    st.warning("Exchange rate unavailable right now. Showing inventory only.")

api_key = get_secret("API_KEY")
st.caption("API key configured." if api_key else "No API key configured (not needed for this API).")
