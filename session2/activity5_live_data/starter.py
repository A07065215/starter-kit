"""Activity 5 starter: live data with graceful failure.

Run from the kit root:   streamlit run session2/activity5_live_data/starter.py

Part A: read the inventory table from the SQLite database through st.connection.
Part B: call a public API (USD->MXN rate), cache it, and handle failures.
"""
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

DB = Path(__file__).resolve().parents[2] / "data" / "supply.db"
FX_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=MXN"  # check it in a browser first

st.set_page_config(page_title="Live data", layout="wide")
st.title("Live data, graceful failure")

# ---------------- Part A: database ----------------
st.header("A. Inventory from the database")
conn = st.connection("supply", type="sql", url=f"sqlite:///{DB}")

# TODO 1: query inventory rows below their reorder point:
#   SELECT sku, warehouse, on_hand, reorder_point FROM inventory WHERE on_hand < reorder_point
#   Use conn.query(sql, ttl=600). Show the result with st.dataframe.
# TODO 2: wrap it in try/except and show st.error("...") + st.stop() on failure.

# ---------------- Part B: API ----------------
st.header("B. Exchange rate from a public API")

# TODO 3: write fetch_rate() decorated with @st.cache_data(ttl=3600)
#   - requests.get(FX_URL, timeout=5); resp.raise_for_status(); return resp.json()["rates"]["MXN"]
# TODO 4: catch requests.RequestException and show st.warning("Rate unavailable, try again later.")
# TODO 5: turn off your WiFi and confirm the page still renders without a traceback.

# TODO 6: if an API needs a key, read it with st.secrets["NAME"] (put it in
#   .streamlit/secrets.toml). NEVER hard-code it in this file.
