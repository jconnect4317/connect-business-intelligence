from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def generate(seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    RAW.mkdir(parents=True, exist_ok=True)

    n_customers = 5_000
    n_products = 60
    n_orders = 80_000

    customer_ids = np.arange(1, n_customers + 1)
    product_ids = np.arange(1, n_products + 1)

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_name": [f"Customer {i:05d}" for i in customer_ids],
            "region": rng.choice(["North America", "Europe", "Asia Pacific", "Latin America"], n_customers, p=[0.36, 0.24, 0.28, 0.12]),
            "segment": rng.choice(["Consumer", "SMB", "Enterprise"], n_customers, p=[0.58, 0.30, 0.12]),
            "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 1_000, n_customers), unit="D"),
        }
    )

    products = pd.DataFrame(
        {
            "product_id": product_ids,
            "product_name": [f"Product {i:03d}" for i in product_ids],
            "category": rng.choice(["Software", "Hardware", "Services", "Accessories"], n_products, p=[0.35, 0.25, 0.20, 0.20]),
            "cost": np.round(rng.uniform(8, 180, n_products), 2),
        }
    )
    products["selling_price"] = np.round(products["cost"] * rng.uniform(1.35, 2.60, n_products), 2)

    order_dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n_orders), unit="D")
    product_choice = rng.choice(product_ids, n_orders)
    customer_choice = rng.choice(customer_ids, n_orders)
    base_qty = rng.poisson(2.2, n_orders) + 1

    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, n_orders + 1),
            "customer_id": customer_choice,
            "product_id": product_choice,
            "order_date": order_dates,
            "quantity": base_qty,
            "status": rng.choice(["Completed", "Completed", "Completed", "Cancelled", "Returned"], n_orders),
        }
    )
    orders = orders.merge(products[["product_id", "selling_price"]], on="product_id", how="left")
    orders["unit_price"] = np.round(orders["selling_price"] * rng.normal(1.0, 0.035, n_orders).clip(0.85, 1.15), 2)
    orders["discount_pct"] = np.round(rng.choice([0, 0.05, 0.10, 0.15, 0.20], n_orders, p=[0.38, 0.25, 0.20, 0.12, 0.05]), 2)
    orders["revenue"] = np.round(orders["quantity"] * orders["unit_price"] * (1 - orders["discount_pct"]), 2)

    # Add a small amount of realistic data quality noise for the ETL layer to detect.
    duplicate_rows = orders.sample(80, random_state=seed)
    orders = pd.concat([orders, duplicate_rows], ignore_index=True)
    orders.loc[orders.sample(60, random_state=seed + 1).index, "region_hint"] = None

    inventory = pd.DataFrame(
        {
            "product_id": product_ids,
            "current_stock": rng.integers(20, 1_000, n_products),
            "reorder_point": rng.integers(50, 300, n_products),
            "lead_time_days": rng.integers(3, 21, n_products),
        }
    )
    inventory = inventory.merge(products[["product_id", "product_name"]], on="product_id", how="left")

    customers.to_csv(RAW / "customers.csv", index=False)
    products.to_csv(RAW / "products.csv", index=False)
    orders.to_csv(RAW / "orders.csv", index=False)
    inventory.to_csv(RAW / "inventory.csv", index=False)

    print(f"Generated data in {RAW}")


if __name__ == "__main__":
    generate()
