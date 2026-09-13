from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DB = ROOT / "data" / "business.db"


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    df = orders.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").fillna(0)
    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "customer_id", "product_id", "order_date"])
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])).round(2)
    return df


def run_etl() -> sqlite3.Connection:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DB.parent.mkdir(parents=True, exist_ok=True)

    customers = pd.read_csv(RAW / "customers.csv")
    products = pd.read_csv(RAW / "products.csv")
    orders = clean_orders(pd.read_csv(RAW / "orders.csv"))
    inventory = pd.read_csv(RAW / "inventory.csv")

    customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
    orders.to_csv(PROCESSED / "orders_clean.csv", index=False)

    conn = sqlite3.connect(DB)
    customers.to_sql("customers", conn, if_exists="replace", index=False)
    products.to_sql("products", conn, if_exists="replace", index=False)
    orders.to_sql("orders", conn, if_exists="replace", index=False)
    inventory.to_sql("inventory", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = run_etl()
    conn.close()
    print(f"ETL complete. Database: {DB}")
