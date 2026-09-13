from pathlib import Path
import sqlite3
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics import headline_metrics, monthly_kpis, top_products
from etl import clean_orders


def test_clean_orders_removes_duplicates_and_invalid_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 1, 2],
            "customer_id": [1, 1, 2],
            "product_id": [1, 1, 2],
            "order_date": ["2025-01-01", "2025-01-01", "2025-01-02"],
            "quantity": [2, 2, -1],
            "unit_price": [10, 10, 10],
            "discount_pct": [0, 0, 0],
            "revenue": [20, 20, -10],
        }
    )
    cleaned = clean_orders(df)
    assert cleaned["order_id"].tolist() == [1]
    assert cleaned.iloc[0]["revenue"] == 20


def test_headline_metrics_ignores_cancelled_orders():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, revenue REAL, status TEXT)")
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [(1, 1, 100.0, "Completed"), (2, 2, 200.0, "Completed"), (3, 1, 999.0, "Cancelled")],
    )
    metrics = headline_metrics(conn)
    assert metrics["revenue"] == 300.0
    assert metrics["orders"] == 2
    assert metrics["customers"] == 2
    conn.close()


def test_monthly_kpis_calculates_average_order_value():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, order_date TEXT, revenue REAL, quantity INTEGER, status TEXT)"
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        [(1, 1, "2025-01-01", 100.0, 2, "Completed"), (2, 2, "2025-01-10", 300.0, 1, "Completed")],
    )
    result = monthly_kpis(conn)
    assert result.iloc[0]["revenue"] == 400.0
    assert result.iloc[0]["avg_order_value"] == 200.0
    conn.close()


def test_top_products_uses_parameterized_limit():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE products (product_id INTEGER, product_name TEXT, category TEXT)")
    conn.execute(
        "CREATE TABLE orders (order_id INTEGER, product_id INTEGER, customer_id INTEGER, revenue REAL, quantity INTEGER, status TEXT)"
    )
    conn.executemany("INSERT INTO products VALUES (?, ?, ?)", [(1, "A", "X"), (2, "B", "Y")])
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        [(1, 1, 1, 100.0, 2, "Completed"), (2, 2, 1, 50.0, 1, "Completed")],
    )
    result = top_products(conn, limit=1)
    assert len(result) == 1
    assert result.iloc[0]["product_name"] == "A"
    conn.close()
