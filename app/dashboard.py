from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analytics import customer_segments, headline_metrics, inventory_risk, monthly_kpis, top_products
from ml import detect_anomalies, forecast_next_7_days

DB = ROOT / "data" / "business.db"

st.set_page_config(page_title="conn.ect BI", page_icon="📊", layout="wide")
st.title("conn.ect Business Intelligence")
st.caption("Portfolio demo: automated analytics, anomaly detection, and revenue forecasting")

if not DB.exists():
    st.error("Database not found. Run `python src/main.py` first.")
    st.stop()

conn = sqlite3.connect(DB)
metrics = headline_metrics(conn)
cols = st.columns(4)
cols[0].metric("Revenue", f"${metrics['revenue']:,.0f}")
cols[1].metric("Orders", f"{metrics['orders']:,}")
cols[2].metric("Customers", f"{metrics['customers']:,}")
cols[3].metric("Avg. Order Value", f"${metrics['avg_order_value']:,.2f}")

st.subheader("Revenue trend")
monthly = monthly_kpis(conn)
fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly revenue")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Top products")
    products = top_products(conn)
    fig = px.bar(products, x="revenue", y="product_name", orientation="h", title="Revenue by product")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Revenue by customer segment")
    segments = customer_segments(conn)
    fig = px.pie(segments, names="segment", values="revenue", title="Revenue mix")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("7-day revenue forecast")
forecast = forecast_next_7_days(conn)
st.dataframe(forecast, use_container_width=True, hide_index=True)

st.subheader("Detected anomalies")
anomalies = detect_anomalies(conn)
st.dataframe(anomalies[anomalies["anomaly"]].tail(20), use_container_width=True, hide_index=True)

st.subheader("Inventory risk")
risk = inventory_risk(conn)
st.dataframe(risk[risk["risk_status"] == "At Risk"].head(20), use_container_width=True, hide_index=True)

conn.close()
