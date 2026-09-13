from __future__ import annotations

from pathlib import Path
import sqlite3

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"

FEATURES = ["lag_1", "lag_7", "lag_14", "lag_28", "dow", "dayofyear"]


def build_daily_series(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query(
        """
        SELECT DATE(order_date) AS date, SUM(revenue) AS revenue
        FROM orders
        WHERE status = 'Completed'
        GROUP BY DATE(order_date)
        ORDER BY date
        """,
        conn,
    )
    if df.empty:
        return pd.DataFrame(columns=["date", "revenue"])

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D", fill_value=0).reset_index()
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)
    return df


def _feature_frame(daily: pd.DataFrame) -> pd.DataFrame:
    frame = daily.copy()
    for lag in [1, 7, 14, 28]:
        frame[f"lag_{lag}"] = frame["revenue"].shift(lag)
    frame["dow"] = frame["date"].dt.dayofweek
    frame["dayofyear"] = frame["date"].dt.dayofyear
    return frame


def train_demand_model(conn: sqlite3.Connection) -> Path:
    MODELS.mkdir(parents=True, exist_ok=True)
    daily = build_daily_series(conn)
    if len(daily) < 60:
        raise ValueError("At least 60 daily observations are required to train the forecast model.")

    frame = _feature_frame(daily).dropna().copy()
    split = int(len(frame) * 0.8)
    train = frame.iloc[:split]
    test = frame.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=12,
        min_samples_leaf=2,
    )
    model.fit(train[FEATURES], train["revenue"])

    predictions = model.predict(test[FEATURES])
    mae = mean_absolute_error(test["revenue"], predictions)
    rmse = mean_squared_error(test["revenue"], predictions) ** 0.5
    r2 = r2_score(test["revenue"], predictions)

    artifact = MODELS / "daily_revenue_forecaster.joblib"
    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
            "metrics": {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)},
            "training_rows": int(len(train)),
            "test_rows": int(len(test)),
        },
        artifact,
    )
    return artifact


def forecast_next_7_days(conn: sqlite3.Connection) -> pd.DataFrame:
    artifact = MODELS / "daily_revenue_forecaster.joblib"
    if not artifact.exists():
        train_demand_model(conn)

    payload = joblib.load(artifact)
    model = payload["model"]
    daily = build_daily_series(conn)
    if len(daily) < 28:
        raise ValueError("At least 28 daily observations are required to forecast.")

    history = list(daily["revenue"].astype(float))
    last_date = daily["date"].max()
    rows = []

    for step in range(1, 8):
        date = last_date + pd.Timedelta(days=step)
        feat = pd.DataFrame(
            [
                {
                    "lag_1": history[-1],
                    "lag_7": history[-7],
                    "lag_14": history[-14],
                    "lag_28": history[-28],
                    "dow": date.dayofweek,
                    "dayofyear": date.dayofyear,
                }
            ]
        )
        prediction = max(0.0, float(model.predict(feat[FEATURES])[0]))
        rows.append({"date": date, "forecast_revenue": prediction})
        history.append(prediction)

    return pd.DataFrame(rows)


def forecast_model_metrics(conn: sqlite3.Connection) -> dict[str, float]:
    artifact = MODELS / "daily_revenue_forecaster.joblib"
    if not artifact.exists():
        train_demand_model(conn)
    payload = joblib.load(artifact)
    return payload["metrics"]


def detect_anomalies(conn: sqlite3.Connection) -> pd.DataFrame:
    daily = build_daily_series(conn)
    if daily.empty:
        return daily.assign(anomaly=pd.Series(dtype=bool), anomaly_score=pd.Series(dtype=float))
    if len(daily) < 30:
        return daily.assign(anomaly=False, anomaly_score=np.nan)

    model = IsolationForest(contamination=0.03, random_state=42, n_estimators=200)
    labels = model.fit_predict(daily[["revenue"]])
    scores = model.decision_function(daily[["revenue"]])

    result = daily.copy()
    result["anomaly"] = labels == -1
    result["anomaly_score"] = scores
    return result
