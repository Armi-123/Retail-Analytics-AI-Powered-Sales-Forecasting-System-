import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from auth_jwt import decode_token
from ai_insights import generate_advanced_insights
from report_generator import generate_pdf_report


# ---------- AUTH GUARD ----------
if "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

if st.session_state["role"] != "user":
    st.error("Access denied")
    st.stop()

user = decode_token(st.session_state.token)
st.session_state["role"] = user.get("role", "user")
st.session_state["username"] = user.get("username", "User")

st.set_page_config(page_title="User Dashboard", layout="wide")

# ---------- SIDEBAR ----------
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "User")

st.sidebar.markdown(f"👋 **Welcome, {username}**")
st.sidebar.markdown(f"🛡 Role: **{role.capitalize()}**")
st.sidebar.markdown("---")

# ---------- DATA ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "final_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "sales_forecast_model.pkl")

if not os.path.exists(DATA_PATH):
    st.error(f"File not found: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"])

# ---------- HEADER ----------
st.title("📊 Retail Analytics Dashboard")
st.caption("Business performance insights")

# ---------- FILTERS ----------
st.sidebar.header("Filters")

region = st.sidebar.selectbox("Region", ["All"] + sorted(df["Region"].unique()))
category = st.sidebar.selectbox("Category", ["All"] + sorted(df["Product_Category"].unique()))

filtered = df.copy()

if region != "All":
    filtered = filtered[filtered["Region"] == region]

if category != "All":
    filtered = filtered[filtered["Product_Category"] == category]

# ---------- KPIs ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"{filtered['Revenue'].sum():,.0f}")
col2.metric("Units Sold", f"{filtered['Units_Sold'].sum():,.0f}")
col3.metric("Avg Discount", f"{filtered['Discount_Percentage'].mean():.2f}%")
col4.metric("Rating", f"{filtered['Store_Rating'].mean():.2f}")

st.markdown("---")

# ---------- DASHBOARD CHARTS ----------
st.subheader("Revenue by Region")
fig1 = px.bar(filtered.groupby("Region")["Revenue"].sum().reset_index(),
              x="Region", y="Revenue")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Revenue by Category")
fig2 = px.bar(filtered.groupby("Product_Category")["Revenue"].sum().reset_index(),
              x="Product_Category", y="Revenue")
st.plotly_chart(fig2, use_container_width=True)

# ---------- PDF EXTRA CHARTS ----------

# Monthly Revenue Trend
monthly = df.groupby(df["Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["Date"] = monthly["Date"].astype(str)
fig_monthly = px.line(monthly, x="Date", y="Revenue")

# Forecast dummy
forecast_df = monthly.tail(6).copy()
forecast_df["Revenue"] = forecast_df["Revenue"] * 1.05
fig_forecast = px.line(forecast_df, x="Date", y="Revenue")

# ---------- FORECAST SECTION ----------
st.subheader("15-Day Sales Forecast")

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    forecast = model.forecast(15)

    future_dates = pd.date_range(start=df["Date"].max(), periods=15)
    forecast_df = pd.DataFrame({"Date": future_dates, "Forecast": forecast})

    fig3 = px.line(forecast_df, x="Date", y="Forecast", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

# ---------- DATA EXPORT ----------
with st.expander("View Sample Data"):
    st.dataframe(filtered.head(20))

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Data", csv, "filtered.csv")

# ---------- LOGOUT ----------
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

hide_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# ---------- PDF REPORT ----------
st.markdown("---")
st.subheader("📄 Generate Report")

if st.button("Generate PDF Report"):

    charts = [
        ("Revenue by Region", fig1),
        ("Revenue by Category", fig2),
        ("Monthly Revenue Trend", fig_monthly),
        ("15-Day Sales Forecast", fig_forecast)
    ]

    filters = {
        "Region": region,
        "Category": category
    }

    path = generate_pdf_report(
        df=filtered,
        filters=filters,
        prepared_by=st.session_state["username"],
        charts=charts,
        date_range=(filtered["Date"].min().date(), filtered["Date"].max().date())
    )

    st.success("Report generated successfully!")
    st.download_button("📥 Download Report", open(path, "rb"), file_name=os.path.basename(path))

# ---------- AI INSIGHTS ----------
st.markdown("---")
st.subheader("🧠 AI Business Insights")

insights, summary = generate_advanced_insights(filtered)

st.markdown("### 📋 Executive Summary")
st.info(summary)

st.markdown("### 📌 Key Insights")
for i in insights:
    st.write(i)
