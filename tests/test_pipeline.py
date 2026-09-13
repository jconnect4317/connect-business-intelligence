from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics import headline_metrics
from etl import clean_orders

import pandas as pd


def test_clean_orders_removes_duplicates_and_invalid_rows():
    df = pd.DataFrame({
        "order_id": [1, 1, 2],
        "customer_id": [1, 1, 2],
        "product_id": [1, 1, 2],
        "order_date": ["2025-01-01", "2025-01-01", "2025-01-02"],
        "quantity": [2, 2, -1],
        "unit_price": [10, 10, 10],
        "discount_pct": [0, 0, 0],
        "revenue": [20, 20, -10],
    })
    cleaned = clean_orders(df)
    assert cleaned["order_id"].tolist() == [1]


def test_headline_metrics():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, revenue REAL, status TEXT)")
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [
        (1, 1, 100.0, "Completed"),
        (2, 2, 200.0, "Completed"),
        (3, 1, 999.0, "Cancelled"),
    ])
    metrics = headline_metrics(conn)
    assert metrics["revenue"] == 300.0
    assert metrics["orders"] == 2
    assert metrics["customers"] == 2
    conn.close()
