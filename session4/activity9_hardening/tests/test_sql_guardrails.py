"""Security tests for the assistant's SQL guard. Failure paths matter as much as happy paths."""
import pytest

from tools import UnsafeQuery, run_sql, validate_sql


def test_select_is_allowed_and_limited():
    df = run_sql("SELECT sku, COUNT(*) AS n FROM orders GROUP BY sku", limit=3)
    assert len(df) == 3


@pytest.mark.parametrize("bad", [
    "DROP TABLE orders",
    "DELETE FROM orders",
    "UPDATE orders SET qty = 0",
    "SELECT 1; DROP TABLE orders",
    "PRAGMA table_info(orders)",
    "ATTACH DATABASE 'x.db' AS x",
    "",
])
def test_unsafe_queries_are_blocked(bad):
    with pytest.raises(UnsafeQuery):
        validate_sql(bad)


def test_columns_that_look_like_keywords_are_fine():
    assert validate_sql("SELECT updated_at FROM inventory")
