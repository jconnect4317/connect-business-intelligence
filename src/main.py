from __future__ import annotations

from pathlib import Path

from generate_data import generate
from etl import DB, run_etl
from ml import train_demand_model


def main() -> None:
    raw_orders = Path(__file__).resolve().parents[1] / "data" / "raw" / "orders.csv"
    if not raw_orders.exists():
        generate()
    conn = run_etl()
    train_demand_model(conn)
    conn.close()
    print(f"Pipeline complete. Database: {DB}")


if __name__ == "__main__":
    main()
