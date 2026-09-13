# conn.ect Business Intelligence

An end-to-end business intelligence and data automation portfolio project built around a realistic synthetic e-commerce business.

## Business problem

Growing businesses often accumulate operational data across recurring files and systems. Manual reporting makes data preparation slow, inconsistent, and reactive.

This project demonstrates a local-first solution that turns raw business data into a reusable analytical workflow with automated insights, anomaly detection, revenue forecasting, and inventory risk signals.

## What it demonstrates

- Synthetic data generation for customers, products, orders, and inventory
- Data validation, cleaning, and transformation with Python and pandas
- Analytical storage and SQL querying with SQLite
- Business KPI calculations
- Month-over-month revenue analysis
- Machine-learning anomaly detection with Isolation Forest
- Seven-day revenue forecasting with a Random Forest model
- Chronological train/test evaluation with MAE, RMSE, and R²
- Interactive Streamlit dashboard for decision support
- Automated tests with pytest
- Dockerized local execution
- GitHub Actions CI

## Architecture

```text
Synthetic Business Data
          |
          v
  Ingestion + Validation
          |
          v
 Cleaning + Transformation
          |
          v
      SQLite DB
       /     \
      /       \
 Analytics     ML
   /   |      / \
 KPIs Products Anomaly Detection
      |          \
      |       Revenue Forecast
       \         /
        \       /
       Streamlit Dashboard
```

See [docs/architecture.md](docs/architecture.md) for more detail.

## Local setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the end-to-end pipeline

```bash
python src/main.py
```

This generates synthetic data when needed, validates/cleans the raw data, loads SQLite, and trains the forecasting model.

### 4. Launch the dashboard

```bash
streamlit run app/dashboard.py
```

### 5. Run tests

```bash
pytest -q
```

## Portfolio notes

This is an independently created portfolio project using synthetic data. It is not based on confidential employer data, code, systems, or workflows.

No paid cloud services are required. The project is designed to run locally on a laptop and uses free/open-source Python tooling.

Any stated business impact should be interpreted as a potential production benefit unless a measured result is explicitly reported.

## What a production version could add

- Cloud object storage and managed orchestration
- Role-based access control
- Incremental data loading
- Data quality monitoring and alerts
- Model registry and experiment tracking
- CI/CD deployment
- Real client data integrations
