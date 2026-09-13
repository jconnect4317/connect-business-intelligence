# conn.ect Business Intelligence

Automated business intelligence, data automation, and machine learning system built from scratch.

## What this project demonstrates

- Synthetic data generation for a realistic e-commerce business
- Python data ingestion and cleaning
- SQL analytics using SQLite
- Automated KPI calculations
- Machine-learning based anomaly detection
- Seven-day revenue forecasting
- Interactive Streamlit dashboard
- Automated tests with pytest
- Reproducible local execution with Docker
- CI checks with GitHub Actions

## Business problem

A growing business has operational data spread across recurring files. Manual reporting creates delays, makes data quality harder to control, and can hide important changes in revenue or inventory.

This project demonstrates a self-contained system that turns raw business data into an analytical database, business metrics, automated signals, forecasts, and a decision-ready dashboard.

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Local setup

### 1. Create an environment

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline

```bash
python src/main.py
```

This generates synthetic raw data, cleans and loads the data into SQLite, and trains the forecasting model.

### 3. Launch the dashboard

```bash
streamlit run app/dashboard.py
```

Open the local Streamlit address shown in your terminal.

### 4. Run tests

```bash
pytest -q
```

## Project structure

```text
src/             pipeline, analytics, and ML code
app/             Streamlit dashboard
tests/            automated tests
data/             raw/processed data and local SQLite database
models/           trained model artifacts
docs/             architecture documentation
```

## Portfolio notes

This is an independently created portfolio project using synthetic data. It is not based on confidential employer data, code, systems, or workflows.

Business impact statements in this repository describe potential production value unless a measured result is explicitly shown.
