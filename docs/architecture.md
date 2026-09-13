# Architecture

## Overview

The project follows a small, modular analytics architecture designed to demonstrate how a local prototype could evolve into a production data product.

```text
                 +----------------------+
                 | Synthetic Source CSV |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Python Ingestion      |
                 | Validation / Cleaning |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | SQLite Analytical DB  |
                 +----------+-----------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
     +------------------+       +-------------------+
     | SQL Analytics    |       | ML Layer          |
     | KPIs / Segments  |       | Anomalies /       |
     | Products / Stock |       | Forecasting      |
     +---------+--------+       +---------+---------+
              \                         /
               \                       /
                +---------+-----------+
                          |
                          v
                +----------------------+
                | Streamlit Dashboard  |
                +----------------------+
```

## Design choices

### Local-first execution

SQLite is used instead of a paid managed database. This keeps the portfolio reproducible with only a laptop while preserving the core analytical workflow.

### Synthetic data

Synthetic data provides realistic volume and data-quality issues without exposing confidential business information.

### Modular Python code

The pipeline is split into data generation, ETL, analytics, ML, and presentation layers. This makes individual components easier to test and replace.

### Time-aware forecasting evaluation

The forecasting model uses a chronological 80/20 split rather than a random split to avoid training on future observations relative to the evaluation period.

## Production evolution

A production implementation could replace the local components with cloud object storage, managed orchestration, a warehouse, centralized observability, access controls, and CI/CD without changing the high-level business workflow.
