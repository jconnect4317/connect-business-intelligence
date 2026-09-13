# Architecture

```text
Synthetic CSV Data
       |
       v
Python Ingestion + Validation
       |
       v
Cleaning / Transformation
       |
       v
SQLite Analytical Database
       |
       +----> KPI SQL queries
       |
       +----> Anomaly Detection
       |
       +----> Revenue Forecasting
       |
       v
Streamlit Dashboard
```

The project is intentionally local-first so the entire system can be demonstrated without paid cloud infrastructure.
