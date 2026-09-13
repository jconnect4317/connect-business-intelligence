from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analytics import (
    customer_segments,
    data_quality_summary,
    headline_metrics,
    inventory_risk,
    monthly_kpis,
    top_products,
)
from ml import detect_anomalies, forecast_model_metrics, forecast_next_7_days

DB = ROOT / "data" / "business.db"

st.set_page_config(page_title="conn.ect BI", page_icon="📊", layout="wide")
st.title("conn.ect Business Intelligence")
st.caption("Decision-support demo: automated analytics, anomaly detection, forecasting, and inventory signals")

if not DB.exists():
    st.error("Database not found. Run `python src/main.py` first.")
    st.stop()

conn = sqlite3.connect(DB)
metrics = headline_metrics(conn)
monthly = monthly_kpis(conn)
anomalies = detect_anomalies(conn)
forecast = forecast_next_7_days(conn)

cols = st.columns(4)
cols[0].metric("Revenue", f"${metrics['revenue']:,.0f}")
cols[1].metric("Orders", f"{metrics['orders']:,}")
cols[2].metric("Customers", f"{metrics['customers']:,}")
cols[3].metric("Avg. Order Value", f"${metrics['avg_order_value']:,.2f}")

st.subheader("Revenue trend")
if not monthly.empty:
    fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly revenue")
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), height=380)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Executive insights")
if not monthly.empty:
    best_month = monthly.loc[monthly["revenue"].idxmax()]
    latest_month = monthly.iloc[-1]
    latest_growth = latest_month["mom_growth_pct"]
    anomaly_count = int(anomalies["anomaly"].sum())
    forecast_total = float(forecast["forecast_revenue"].sum())

    growth_text = "not available" if latest_growth != latest_growth else f"{latest_growth:+.1f}%"
    st.info(
        f"**Business summary**\n\n"
        f"• Revenue peaked at **${best_month['revenue']:,.0f}** in **{best_month['month']}**.\n\n"
        f"• The latest reporting month generated **${latest_month['revenue']:,.0f}** across **{int(latest_month['orders']):,} orders**.\n\n"
        f"• Latest month-over-month revenue movement: **{growth_text}**.\n\n"
        f"• The anomaly model flagged **{anomaly_count}** unusual daily revenue observations.\n\n"
        f"• Seven-day forecast: approximately **${forecast_total:,.0f}**."
    )

left, right = st.columns(2)
with left:
    st.subheader("Top products")
    products = top_products(conn)
    fig = px.bar(products, x="revenue", y="product_name", orientation="h", title="Revenue by product")
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), height=430)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Revenue by customer segment")
    segments = customer_segments(conn)
    fig = px.pie(segments, names="segment", values="revenue", title="Revenue mix")
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), height=430)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("7-day revenue forecast")
forecast_display = forecast.copy()
forecast_display["date"] = forecast_display["date"].dt.strftime("%Y-%m-%d")
forecast_display["forecast_revenue"] = forecast_display["forecast_revenue"].round(2)
st.dataframe(forecast_display, use_container_width=True, hide_index=True)

st.subheader("Forecast model evaluation")
model_metrics = forecast_model_metrics(conn)
m1, m2, m3 = st.columns(3)
m1.metric("MAE", f"${model_metrics['mae']:,.0f}")
m2.metric("RMSE", f"${model_metrics['rmse']:,.0f}")
m3.metric("R²", f"{model_metrics['r2']:.2f}")
st.caption("Evaluation uses a chronological 80/20 holdout from the synthetic historical series.")

st.subheader("Detected anomalies")
anomaly_rows = anomalies[anomalies["anomaly"]].copy()
anomaly_rows["date"] = anomaly_rows["date"].dt.strftime("%Y-%m-%d")
st.dataframe(anomaly_rows.tail(20), use_container_width=True, hide_index=True)

st.subheader("Inventory risk")
risk = inventory_risk(conn)
st.dataframe(risk[risk["risk_status"] == "At Risk"].head(20), use_container_width=True, hide_index=True)

with st.expander("Data coverage"):
    quality = data_quality_summary(conn)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Customers", f"{quality['customers']:,}")
    q2.metric("Products", f"{quality['products']:,}")
    q3.metric("Orders", f"{quality['orders']:,}")
    q4.metric("Inventory items", f"{quality['inventory_items']:,}")

conn.close()
