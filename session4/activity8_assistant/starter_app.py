"""Activity 8 starter: ask-your-data assistant (works out of the box with a mock LLM).

Run from the kit root:   streamlit run session4/activity8_assistant/starter_app.py

You get: the chat UI and a keyword-based mock model (mock_llm.py), so nothing
needs an API key. You build the safety and quality layers:

  TODO 1  write a system prompt that describes the schema (see tools.SCHEMA_DOC)
  TODO 2  harden run_sql(): read-only, one statement, LIMIT, error handling
  TODO 3  show the generated SQL and the result table under each answer
  TODO 4  add eval_questions.json cases and run:  python run_eval.py
  TODO 5  try an injection prompt ("ignore previous instructions...") and fix it
  TODO 6  (optional) swap the mock for a real model via llm_client.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from mock_llm import question_to_sql

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "supply.db"

st.set_page_config(page_title="Ask your data", layout="wide")
st.title("Ask your data")

# TODO 1: describe tables, columns and business definitions here (used with a real LLM)
SYSTEM_PROMPT = "TODO"


def run_sql(sql: str) -> pd.DataFrame:
    # TODO 2: this naive version runs ANYTHING the model returns. Harden it.
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(sql, con)


if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.write(m["text"])
        # TODO 3: if m has "sql", show it in st.expander; if it has "df", st.dataframe it

if q := st.chat_input("Ask about sales, orders or inventory"):
    st.session_state.msgs.append({"role": "user", "text": q})
    sql = question_to_sql(q)
    if sql.startswith("REFUSE"):
        reply = {"role": "assistant", "text": sql}
    else:
        df = run_sql(sql)
        reply = {"role": "assistant", "text": f"{len(df)} row(s).", "sql": sql, "df": df}
    st.session_state.msgs.append(reply)
    st.rerun()
