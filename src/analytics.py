from __future__ import annotations

import sqlite3
import pandas as pd


def monthly_kpis(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT
        strftime('%Y-%m', order_date) AS month,
        ROUND(SUM(revenue), 2) AS revenue,
        SUM(quantity) AS units,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(DISTINCT customer_id) AS customers
    FROM orders
    WHERE status = 'Completed'
    GROUP BY 1
    ORDER BY 1
    """
    df = pd.read_sql_query(query, conn)
    if not df.empty:
        df["avg_order_value"] = (df["revenue"] / df["orders"]).round(2)
        df["mom_growth_pct"] = df["revenue"].pct_change().mul(100).round(2)
    return df


def top_products(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    query = """
    SELECT p.product_name, p.category,
           ROUND(SUM(o.revenue), 2) AS revenue,
           SUM(o.quantity) AS units
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'Completed'
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY revenue DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=[int(limit)])


def customer_segments(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT c.segment,
           COUNT(DISTINCT c.customer_id) AS customers,
           ROUND(COALESCE(SUM(o.revenue), 0), 2) AS revenue
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
    GROUP BY c.segment
    ORDER BY revenue DESC
    """
    return pd.read_sql_query(query, conn)


def inventory_risk(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT product_name, current_stock, reorder_point, lead_time_days,
           CASE WHEN current_stock <= reorder_point THEN 'At Risk' ELSE 'Healthy' END AS risk_status
    FROM inventory
    ORDER BY (current_stock - reorder_point) ASC
    """
    return pd.read_sql_query(query, conn)


def headline_metrics(conn: sqlite3.Connection) -> dict[str, float]:
    row = conn.execute(
        """
        SELECT
            ROUND(SUM(CASE WHEN status = 'Completed' THEN revenue ELSE 0 END), 2) AS revenue,
            COUNT(DISTINCT CASE WHEN status = 'Completed' THEN order_id END) AS orders,
            COUNT(DISTINCT CASE WHEN status = 'Completed' THEN customer_id END) AS customers
        FROM orders
        """
    ).fetchone()
    revenue, orders, customers = row
    return {
        "revenue": float(revenue or 0),
        "orders": int(orders or 0),
        "customers": int(customers or 0),
        "avg_order_value": float(revenue / orders) if orders else 0.0,
    }


def data_quality_summary(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
        "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "inventory_items": conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
    }
