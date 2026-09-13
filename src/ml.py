from __future__ import annotations

from pathlib import Path
import sqlite3

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest


ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"


def build_daily_series(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query("""
        SELECT DATE(order_date) AS date, SUM(revenue) AS revenue
        FROM orders
        WHERE status = 'Completed'
        GROUP BY DATE(order_date)
        ORDER BY date
    """, conn)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D", fill_value=0).reset_index()
    return df


def train_demand_model(conn: sqlite3.Connection) -> Path:
    MODELS.mkdir(parents=True, exist_ok=True)
    daily = build_daily_series(conn)
    for lag in [1, 7, 14, 28]:
        daily[f"lag_{lag}"] = daily["revenue"].shift(lag)
    daily["dow"] = daily["date"].dt.dayofweek
    daily["dayofyear"] = daily["date"].dt.dayofyear
    train = daily.dropna().copy()
    features = ["lag_1", "lag_7", "lag_14", "lag_28", "dow", "dayofyear"]

    model = RandomForestRegressor(n_estimators=250, random_state=42, n_jobs=-1, max_depth=10)
    model.fit(train[features], train["revenue"])
    artifact = MODELS / "daily_revenue_forecaster.joblib"
    joblib.dump({"model": model, "features": features}, artifact)
    return artifact


def forecast_next_7_days(conn: sqlite3.Connection) -> pd.DataFrame:
    artifact = MODELS / "daily_revenue_forecaster.joblib"
    if not artifact.exists():
        train_demand_model(conn)
    payload = joblib.load(artifact)
    model = payload["model"]
    features = payload["features"]

    daily = build_daily_series(conn)
    history = list(daily["revenue"].astype(float))
    last_date = daily["date"].max()
    rows = []
    for step in range(1, 8):
        date = last_date + pd.Timedelta(days=step)
        feat = pd.DataFrame([{ 
            "lag_1": history[-1],
            "lag_7": history[-7],
            "lag_14": history[-14],
            "lag_28": history[-28],
            "dow": date.dayofweek,
            "dayofyear": date.dayofyear,
        }])
        pred = max(0.0, float(model.predict(feat[features])[0]))
        rows.append({"date": date, "forecast_revenue": pred})
        history.append(pred)
    return pd.DataFrame(rows)


def detect_anomalies(conn: sqlite3.Connection) -> pd.DataFrame:
    daily = build_daily_series(conn)
    if len(daily) < 30:
        return daily.assign(anomaly=False, anomaly_score=np.nan)
    features = daily[["revenue"]].copy()
    model = IsolationForest(contamination=0.03, random_state=42)
    labels = model.fit_predict(features)
    scores = model.decision_function(features)
    result = daily.copy()
    result["anomaly"] = labels == -1
    result["anomaly_score"] = scores
    return result
