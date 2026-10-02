import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_data, validate_data
from src.data_cleaner import clean_data
from src.analytics import calculate_kpis, create_daily_summary
from src.anomaly_detector import detect_anomalies
from src.anomaly_explainer import explain_anomalies
from src.business_rules import generate_business_context

st.set_page_config(
    page_title="AI Business Analytics Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Powered Business Analytics Agent")
st.caption("Automated Excel/CSV analytics, anomaly detection, and business insights")

uploaded_file = st.file_uploader(
    "📂 Upload Business Data",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        raw_df = load_data(uploaded_file)
        validate_data(raw_df)
        df = clean_data(raw_df)

        if df.empty:
            st.error("No usable records remain after cleaning.")
            st.stop()

        df = detect_anomalies(df)
        df = explain_anomalies(df)
        df = generate_business_context(df)

        st.success(f"Successfully loaded and analyzed {len(df):,} records.")

        tabs = st.tabs([
            "🏠 Overview",
            "📋 Data",
            "📊 Dashboard",
            "🚨 Anomalies",
            "💡 Business Insights"
        ])

        with tabs[0]:
            st.subheader("Dataset Overview")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", f"{len(df):,}")
            c2.metric("Columns", f"{len(df.columns):,}")
            c3.metric("Missing Values", f"{df.isna().sum().sum():,}")
            c4.metric("Anomalies", f"{(df['Anomaly Status'] == 'Anomaly').sum():,}")

            kpis = calculate_kpis(df)
            st.subheader("📌 Business KPIs")
            cols = st.columns(len(kpis))
            for col, (name, value) in zip(cols, kpis.items()):
                col.metric(name, f"{value:,.2f}")

        with tabs[1]:
            st.subheader("📋 Cleaned Data Preview")
            st.dataframe(df, use_container_width=True, height=500)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Analyzed CSV",
                csv,
                "analyzed_business_data.csv",
                "text/csv"
            )

        with tabs[2]:
            st.subheader("📊 Business Dashboard")

            daily = create_daily_summary(df)
            if not daily.empty:
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.line(
                        daily, x="Date", y="Sales",
                        title="Sales Trend", markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with c2:
                    fig = px.line(
                        daily, x="Date", y="Profit",
                        title="Profit Trend", markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if "Region" in df.columns:
                regional = (
                    df.groupby("Region", as_index=False)["Sales"]
                    .sum()
                    .sort_values("Sales", ascending=False)
                )
                fig = px.bar(
                    regional,
                    x="Region",
                    y="Sales",
                    title="Sales by Region",
                    text_auto=".2s"
                )
                st.plotly_chart(fig, use_container_width=True)

            if "Category" in df.columns:
                category = (
                    df.groupby("Category", as_index=False)["Sales"]
                    .sum()
                    .sort_values("Sales", ascending=False)
                )
                fig = px.pie(
                    category,
                    names="Category",
                    values="Sales",
                    title="Sales by Category"
                )
                st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            st.subheader("🚨 AI Anomaly Detection")

            anomalies = df[df["Anomaly Status"] == "Anomaly"].copy()

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Records", len(df))
            c2.metric("Anomalies", len(anomalies))
            rate = (len(anomalies) / len(df) * 100) if len(df) else 0
            c3.metric("Anomaly Rate", f"{rate:.1f}%")

            if anomalies.empty:
                st.success("No unusual records were detected.")
            else:
                st.warning(f"{len(anomalies)} unusual records detected.")

                display_cols = [
                    c for c in [
                        "Date", "Product", "Category", "Region",
                        "Sales", "Quantity", "Discount", "Profit",
                        "Anomaly Reason", "Business Context"
                    ] if c in anomalies.columns
                ]

                st.dataframe(
                    anomalies[display_cols],
                    use_container_width=True,
                    height=450
                )

        with tabs[4]:
            st.subheader("💡 Business Insights")

            anomalies = df[df["Anomaly Status"] == "Anomaly"]

            if anomalies.empty:
                st.info("No anomalies available for business interpretation.")
            else:
                for i, (_, row) in enumerate(anomalies.iterrows(), start=1):
                    st.markdown(f"### Insight {i}")

                    if "Date" in row and pd.notna(row["Date"]):
                        st.write(f"**Date:** {row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else row['Date']}")

                    if "Product" in row:
                        st.write(f"**Product:** {row['Product']}")
                    if "Region" in row:
                        st.write(f"**Region:** {row['Region']}")

                    st.write(f"**Detected issue:** {row.get('Anomaly Reason', 'Unusual business pattern')}")
                    st.write(f"**Business context:** {row.get('Business Context', 'Requires further investigation.')}")

                    st.divider()

    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Upload an Excel or CSV file to start the analysis.")
    st.markdown("""
    ### What this app does
    - 📥 Upload Excel/CSV business data
    - 🧹 Clean and validate the dataset
    - 📊 Calculate business KPIs
    - 📈 Analyze sales and profit trends
    - 🤖 Detect unusual records using Isolation Forest
    - 🔎 Explain which metrics look unusual
    - 💡 Generate rule-based business context
    - 📥 Download the analyzed dataset
    """)
