import pandas as pd
import numpy as np

def generate_advanced_insights(df: pd.DataFrame):
    insights = []

    # Ensure date format
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    # ========== 1. Revenue trend ==========
    monthly = df.groupby("Month")["Revenue"].sum()

    if len(monthly) > 1:
        growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
        trend = "increased" if growth > 0 else "decreased"
        insights.append(
            f"📈 Revenue has {trend} by {abs(growth):.2f}% compared to last month."
        )

    # ========== 2. Best/Worst Region ==========
    region_sales = df.groupby("Region")["Revenue"].sum()
    best_region = region_sales.idxmax()
    worst_region = region_sales.idxmin()

    insights.append(f"🏆 Best performing region: {best_region}.")
    insights.append(f"⚠️ Lowest performing region: {worst_region}.")

    # ========== 3. Best/Worst Category ==========
    cat_sales = df.groupby("Product_Category")["Revenue"].sum()
    best_cat = cat_sales.idxmax()
    worst_cat = cat_sales.idxmin()

    insights.append(f"🛍️ Top category: {best_cat}.")
    insights.append(f"📉 Weakest category: {worst_cat}.")

    # ========== 4. Anomaly Detection ==========
    daily = df.groupby("Date")["Revenue"].sum()
    mean = daily.mean()
    std = daily.std()

    anomalies = daily[daily < mean - 2 * std]

    if not anomalies.empty:
        insights.append(
            f"🚨 Anomaly detected: Unusual revenue drop on {anomalies.index[-1].date()}."
        )

    # ========== 5. Smart Recommendation ==========
    insights.append(
        f"💡 Recommendation: Focus marketing campaigns on {worst_region} and introduce offers in {worst_cat} category."
    )

    # ========== 6. Executive Summary ==========
    summary = f"""
    Overall business performance shows that {best_region} is driving most revenue while
    {worst_region} is underperforming. The strongest product category is {best_cat},
    whereas {worst_cat} needs strategic improvement. Recent trends indicate revenue is
    {'growing' if growth > 0 else 'declining'}, requiring data-driven decision making.
    """

    return insights, summary.strip()
