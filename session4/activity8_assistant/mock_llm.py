"""A fake 'LLM' so the activity works without API keys or internet.

question_to_sql(question) returns either a SQL string or 'REFUSE: <reason>'.
It is keyword-based on purpose: students replace it with a real model (see
llm_client.py) and compare what breaks.
"""
import re

RULES = [
    (r"revenue.*(region)|(region).*revenue",
     "SELECT region, ROUND(SUM(qty * unit_price), 2) AS revenue FROM orders "
     "WHERE status IN ('delivered', 'shipped') GROUP BY region ORDER BY revenue DESC"),
    (r"top.*sku|best.?sell|sku.*revenue",
     "SELECT sku, ROUND(SUM(qty * unit_price), 2) AS revenue FROM orders "
     "WHERE status IN ('delivered', 'shipped') GROUP BY sku ORDER BY revenue DESC LIMIT 5"),
    (r"cancel",
     "SELECT COUNT(*) AS cancelled_orders FROM orders WHERE status = 'cancelled'"),
    (r"late",
     "SELECT region, COUNT(*) AS late_orders FROM orders WHERE ship_days > 5 "
     "GROUP BY region ORDER BY late_orders DESC"),
    (r"inventory|stock|reorder",
     "SELECT sku, warehouse, on_hand, reorder_point FROM inventory "
     "WHERE on_hand < reorder_point ORDER BY reorder_point - on_hand DESC"),
    (r"month",
     "SELECT substr(order_date, 1, 7) AS month, COUNT(*) AS orders FROM orders "
     "GROUP BY month ORDER BY month"),
]
BLOCKED = r"drop|delete|update|insert|ignore (all|your|previous)|system prompt|password|address"


def question_to_sql(question: str) -> str:
    q = question.lower()
    if re.search(BLOCKED, q):
        return "REFUSE: I can only run read-only questions about the supply chain data."
    for pattern, sql in RULES:
        if re.search(pattern, q):
            return sql
    return "REFUSE: I can't answer that from the supply chain tables."
