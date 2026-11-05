"""Tools the assistant may call. The model never touches the database directly:
everything goes through run_sql(), which enforces read-only access, one statement,
a row limit and a time limit.
"""
import re
import sqlite3
import time
from contextlib import closing
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "supply.db"
MAX_ROWS = 200
MAX_SECONDS = 3

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|truncate)\b",
    re.IGNORECASE,
)

SCHEMA_DOC = """\
SQLite database with three tables.

skus(sku TEXT, category TEXT, unit_cost REAL, unit_price REAL, unit_volume_m3 REAL,
     min_order_qty INT, lead_time_days INT)
  - one row per product. category is one of Beverages, Snacks, Dairy, Bakery.

orders(order_id INT, order_date TEXT 'YYYY-MM-DD', customer_id TEXT, sku TEXT, region TEXT,
       warehouse TEXT, qty INT, unit_price REAL, status TEXT, ship_days INT)
  - one row per order line, 2024-01-01 to 2025-12-31 (sample of 30,000 rows).
  - region is North, South, East or West; warehouse is MTY, GDL or CDMX.
  - status is delivered, shipped, cancelled or returned.

inventory(sku TEXT, warehouse TEXT, on_hand INT, reorder_point INT, updated_at TEXT)
  - current stock per SKU and warehouse. Below reorder point means on_hand < reorder_point.

Business definitions:
  - revenue = qty * unit_price, counting only status 'delivered' or 'shipped'.
  - a late order is one with ship_days > 5.
  - join orders to skus on sku; join inventory to skus on sku.
"""


class UnsafeQuery(ValueError):
    """Raised when a query is not a single read-only SELECT."""


def validate_sql(sql: str) -> str:
    stmt = sql.strip().rstrip(";").strip()
    if not stmt:
        raise UnsafeQuery("Empty query.")
    if ";" in stmt:
        raise UnsafeQuery("Only one statement is allowed.")
    if not re.match(r"^(select|with)\b", stmt, re.IGNORECASE):
        raise UnsafeQuery("Only SELECT queries are allowed.")
    if FORBIDDEN.search(stmt):
        raise UnsafeQuery("The query contains a forbidden keyword.")
    return stmt


def run_sql(sql: str, limit: int = MAX_ROWS, db_path: Path = DB_PATH) -> pd.DataFrame:
    stmt = validate_sql(sql)
    start = time.time()
    with closing(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)) as con:
        con.set_progress_handler(lambda: 1 if time.time() - start > MAX_SECONDS else 0, 10_000)
        return pd.read_sql_query(f"SELECT * FROM ({stmt}) LIMIT {int(limit)}", con)
