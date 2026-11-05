"""Activity 8 SOLUTION: ask-your-data assistant.

Run from the kit root:   streamlit run session4/activity8_assistant/solution_app.py
Works without an API key (mock backend). To use a real model, put
ANTHROPIC_API_KEY = "..." in .streamlit/secrets.toml.
"""
import streamlit as st

from llm_client import backend_name, explain, question_to_sql
from tools import UnsafeQuery, run_sql

st.set_page_config(page_title="Ask your data", layout="wide")
st.title("Ask your data")
st.sidebar.caption(f"Backend: {backend_name()}")
st.sidebar.markdown("Try: *top 5 SKUs by revenue*, *revenue by region*, *inventory below reorder point*.")

if "msgs" not in st.session_state:
    st.session_state.msgs = []


def render(m):
    with st.chat_message(m["role"]):
        st.write(m["text"])
        if m.get("sql"):
            with st.expander("Generated SQL"):
                st.code(m["sql"], language="sql")
        if m.get("df") is not None:
            st.dataframe(m["df"], width="stretch", hide_index=True)


def answer(question: str) -> dict:
    try:
        sql = question_to_sql(question)
    except Exception:
        return {"role": "assistant", "text": "The language model is unavailable right now. Please try again."}
    if sql.upper().startswith("REFUSE"):
        return {"role": "assistant", "text": sql.split(":", 1)[-1].strip() or "I can't help with that."}
    try:
        df = run_sql(sql)
    except UnsafeQuery as e:
        return {"role": "assistant", "text": f"I blocked that query: {e}", "sql": sql}
    except Exception:
        return {"role": "assistant", "text": "That query did not run. Try rephrasing the question.", "sql": sql}
    return {"role": "assistant", "text": explain(question, df), "sql": sql, "df": df}


for m in st.session_state.msgs:
    render(m)

if q := st.chat_input("Ask about sales, orders or inventory"):
    st.session_state.msgs.append({"role": "user", "text": q})
    with st.spinner("Thinking..."):
        st.session_state.msgs.append(answer(q))
    st.rerun()
