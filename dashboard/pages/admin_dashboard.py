import streamlit as st
import pandas as pd
import os
import plotly.express as px
from auth_jwt import decode_token
from ai_insights import generate_advanced_insights
from admin_report import generate_admin_report


# ---------- AUTH GUARD ----------
if "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

if st.session_state["role"] != "admin":
    st.error("Access denied")
    st.stop()

# ---------- SYNC SESSION ----------
user = decode_token(st.session_state.token)
st.session_state["role"] = user.get("role", "user")
st.session_state["username"] = user.get("username", "User")

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# ---------- SIDEBAR ----------
role = st.session_state.get("role", "Admin")
username = st.session_state.get("username", "User")

st.sidebar.markdown(f"👋 **Welcome, {username}**")
st.sidebar.markdown(f"🛡 Role: **{role.capitalize()}**")
st.sidebar.markdown("---")

# ---------- DATA ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "final_data.csv")

if not os.path.exists(DATA_PATH):
    st.error(f"File not found: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"])

# ---------- HEADER ----------
st.title("🛠️ Admin Control Panel")
st.caption("System-wide analytics overview")

# ---------- KPIs ----------
total_revenue = df["Revenue"].sum()
total_users = df["Customer_Type"].nunique()
avg_order = df["Revenue"].mean()
best_region = df.groupby("Region")["Revenue"].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"{total_revenue:,.0f}")
col2.metric("👥 Total Customer Types", total_users)
col3.metric("📦 Avg Order Value", f"{avg_order:,.2f}")
col4.metric("🌍 Best Region", best_region)

st.markdown("---")

# ---------- MAIN CHART ----------
st.subheader("Revenue by Region")
region_sales = df.groupby("Region")["Revenue"].sum().reset_index()
fig_region = px.bar(region_sales, x="Region", y="Revenue")
st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")

# ---------- EXTRA CHARTS FOR PDF ----------
category_sales = df.groupby("Product_Category")["Revenue"].sum().reset_index()
fig_category = px.bar(category_sales, x="Product_Category", y="Revenue")

monthly = df.groupby(df["Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
monthly["Date"] = monthly["Date"].astype(str)
fig_monthly = px.line(monthly, x="Date", y="Revenue")

forecast_df = monthly.tail(6).copy()
forecast_df["Revenue"] = forecast_df["Revenue"] * 1.05
fig_forecast = px.line(forecast_df, x="Date", y="Revenue")

# ---------- SEARCH ----------
st.subheader("Data Explorer")

search = st.text_input("Search by Store / Product / City")
filtered = df.copy()

if search:
    filtered = df[
        df["Store_Location"].str.contains(search, case=False, na=False) |
        df["Product_Category"].str.contains(search, case=False, na=False)
    ]

st.dataframe(filtered.head(50), use_container_width=True)

# ---------- DOWNLOAD DATA ----------
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Full Dataset", csv, "full_data.csv")

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

# ---------- PDF EXPORT ----------
st.markdown("---")
st.subheader("📄 Export Report")

if st.button("Generate Professional PDF Report"):
    path = generate_admin_report(
    df=filtered,
    filters={
        "Search": search if search else "All",
        "Records Included": len(filtered)
    },
    prepared_by=st.session_state["username"],
    charts=[
        ("Revenue by Region", fig_region),
        ("Revenue by Category", fig_category),
        ("Monthly Revenue Trend", fig_monthly),
        ("15-Day Sales Forecast", fig_forecast)
    ],
    date_range=(filtered["Date"].min().date(), filtered["Date"].max().date())
)


    with open(path, "rb") as f:
        st.download_button(
            "⬇️ Download Report",
            f,
            file_name=os.path.basename(path),
            mime="application/pdf"
        )

# ---------- AI INSIGHTS ----------
st.markdown("---")
st.subheader("🧠 AI Business Insights")

insights, summary = generate_advanced_insights(filtered)

st.markdown("### 📋 Executive Summary")
st.info(summary)

st.markdown("### 📌 Key Insights")
for i in insights:
    st.write(i)
