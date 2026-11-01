import io
import os
import smtplib
from email.message import EmailMessage

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_data, validate_data
from src.data_cleaner import clean_data
from src.analytics import calculate_kpis, create_daily_summary
from src.anomaly_detector import detect_anomalies
from src.anomaly_explainer import explain_anomalies
from src.business_rules import generate_business_context

st.set_page_config(page_title="AI Business Analytics Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI-Powered Business Analytics Agent")
st.caption("Upload business data, understand performance, detect unusual patterns, and explore actionable insights.")

with st.sidebar:
    st.header("Analysis settings")
    contamination = st.slider("Expected anomaly proportion", 0.01, 0.25, 0.08, 0.01,
                              help="Controls how many records the Isolation Forest may flag for review.")
    st.caption("Anomaly flags identify unusual patterns, not confirmed errors or fraud.")

uploaded_file = st.file_uploader("📂 Upload Business Data", type=["xlsx", "xls", "csv"])

def make_excel_report(data, anomaly_data, cleaning_report):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name="Analyzed Data", index=False)
        anomaly_data.to_excel(writer, sheet_name="Anomalies", index=False)
        pd.DataFrame([cleaning_report]).to_excel(writer, sheet_name="Cleaning Summary", index=False)
        pd.DataFrame([calculate_kpis(data)]).to_excel(writer, sheet_name="KPIs", index=False)
    output.seek(0)
    return output.getvalue()

def send_email_alert(anomaly_count, total_count, recipient):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    if not all([host, sender, password, recipient]):
        raise ValueError("Email settings are not configured. Add SMTP_HOST, SMTP_PORT, SMTP_EMAIL, and SMTP_PASSWORD as Streamlit secrets or environment variables.")
    msg = EmailMessage()
    msg["Subject"] = "Business Analytics Agent: anomaly review alert"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(f"The analysis flagged {anomaly_count} unusual records out of {total_count}. Please review the anomaly table in the application.")
    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

if uploaded_file:
    try:
        raw_df = load_data(uploaded_file)
        validate_data(raw_df)
        df, cleaning_report = clean_data(raw_df)
        if df.empty:
            st.error("No usable records remain after cleaning.")
            st.stop()

        df = detect_anomalies(df, contamination=contamination)
        df = explain_anomalies(df)
        df = generate_business_context(df)
        anomalies = df[df["Anomaly Status"] == "Anomaly"].copy()
        st.success(f"Successfully analyzed {len(df):,} records from **{uploaded_file.name}**.")

        tabs = st.tabs(["🏠 Overview", "📋 Data & Cleaning", "📊 Dashboard", "🚨 Anomalies", "💡 Insights & Assistant", "📤 Reports & Alerts"])

        with tabs[0]:
            st.subheader("Dataset overview")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Records", f"{len(df):,}")
            c2.metric("Columns", f"{len(df.columns):,}")
            c3.metric("Missing values", f"{df.isna().sum().sum():,}")
            c4.metric("Records to review", f"{len(anomalies):,}")
            st.subheader("Business KPIs")
            kpis = calculate_kpis(df)
            if kpis:
                cols = st.columns(min(len(kpis), 4))
                for i, (name, value) in enumerate(kpis.items()):
                    if pd.notna(value):
                        cols[i % len(cols)].metric(name, f"{value:,.2f}")
            else:
                st.info("No standard sales, revenue, profit, or quantity fields were found. You can still explore the dataset and numeric anomalies.")
            st.subheader("Data quality snapshot")
            quality = pd.DataFrame({"Column": df.columns, "Data type": [str(x) for x in df.dtypes], "Missing": [int(df[c].isna().sum()) for c in df.columns], "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns]})
            st.dataframe(quality, use_container_width=True, hide_index=True)

        with tabs[1]:
            st.subheader("Cleaning summary")
            q1, q2, q3 = st.columns(3)
            q1.metric("Input rows", f"{cleaning_report['input_rows']:,}")
            q2.metric("Rows after cleaning", f"{cleaning_report['output_rows']:,}")
            q3.metric("Blank / duplicate rows removed", f"{cleaning_report['removed_blank_or_duplicate_rows']:,}")
            st.caption(f"Missing values: {cleaning_report['missing_values_before']:,} before cleaning → {cleaning_report['missing_values_after']:,} after cleaning. Missing values are retained where possible rather than automatically deleting valid records.")
            st.subheader("Cleaned and analyzed data")
            st.dataframe(df, use_container_width=True, height=430)
            st.download_button("⬇️ Download analyzed CSV", df.to_csv(index=False).encode("utf-8"), "analyzed_business_data.csv", "text/csv")

        with tabs[2]:
            st.subheader("Business dashboard")
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                chosen_metric = st.selectbox("Choose a metric to explore", numeric_cols, index=0)
                categorical = [c for c in df.select_dtypes(include=["object", "category"]).columns if c not in {"Anomaly Status", "Anomaly Reason", "Business Context", "Anomaly Severity"}]
                if categorical:
                    group_col = st.selectbox("Break down by", categorical, index=0)
                    grouped = df.groupby(group_col, dropna=False)[chosen_metric].sum().reset_index().sort_values(chosen_metric, ascending=False)
                    st.plotly_chart(px.bar(grouped, x=group_col, y=chosen_metric, title=f"{chosen_metric} by {group_col}", text_auto=".2s"), use_container_width=True)
                if "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"]):
                    daily = create_daily_summary(df)
                    if not daily.empty:
                        trend_metric = chosen_metric if chosen_metric in daily.columns else daily.columns[1]
                        st.plotly_chart(px.line(daily, x="Date", y=trend_metric, markers=True, title=f"{trend_metric} over time"), use_container_width=True)
            else:
                st.info("No numeric columns are available for charts.")
            if "Region" in df.columns and ("Sales" in df.columns or "Revenue" in df.columns):
                sales_col = "Sales" if "Sales" in df.columns else "Revenue"
                regional = df.groupby("Region", as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False)
                st.plotly_chart(px.pie(regional, names="Region", values=sales_col, title=f"{sales_col} share by region"), use_container_width=True)

        with tabs[3]:
            st.subheader("Anomaly detection")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total records", f"{len(df):,}")
            c2.metric("Flagged records", f"{len(anomalies):,}")
            c3.metric("Flag rate", f"{len(anomalies) / max(len(df), 1) * 100:.1f}%")
            if anomalies.empty:
                st.success("No unusual records were detected with the current settings.")
            else:
                severity_filter = st.multiselect("Filter severity", ["High", "Medium"], default=["High", "Medium"])
                filtered = anomalies[anomalies["Anomaly Severity"].isin(severity_filter)]
                display_cols = [c for c in ["Date", "Product", "Category", "Region", "Sales", "Revenue", "Quantity", "Discount", "Profit", "Anomaly Severity", "Anomaly Reason", "Business Context"] if c in filtered.columns]
                st.dataframe(filtered[display_cols], use_container_width=True, height=420)
                st.download_button("⬇️ Download anomaly records", filtered.to_csv(index=False).encode("utf-8"), "anomaly_records.csv", "text/csv")

        with tabs[4]:
            st.subheader("Business insights")
            if anomalies.empty:
                st.info("No anomaly records to explain. Try adjusting the expected anomaly proportion.")
            else:
                for i, (_, row) in enumerate(anomalies.head(30).iterrows(), 1):
                    with st.expander(f"{i}. {row.get('Anomaly Severity', 'Review')} severity — {row.get('Anomaly Reason', 'Unusual record')}"):
                        for col in ["Date", "Product", "Category", "Region", "Sales", "Revenue", "Quantity", "Discount", "Profit"]:
                            if col in row.index and pd.notna(row[col]):
                                st.write(f"**{col}:** {row[col]}")
                        st.write(f"**Possible business context:** {row.get('Business Context', 'Further investigation required.')}")
                st.caption("These are statistical signals and possible explanations. Validate them with source systems and business owners.")
            st.divider()
            st.subheader("Ask the analytics assistant")
            question = st.text_input("Ask about this uploaded dataset", placeholder="Example: Which region has the highest sales?")
            if question:
                q = question.lower()
                sales_col = "Sales" if "Sales" in df.columns else ("Revenue" if "Revenue" in df.columns else None)
                if "anomal" in q or "unusual" in q:
                    st.write(f"The model flagged **{len(anomalies)}** of **{len(df)}** records ({len(anomalies)/max(len(df),1)*100:.1f}%).")
                elif sales_col and "region" in q and "Region" in df.columns:
                    ranked = df.groupby("Region")[sales_col].sum().sort_values(ascending=False)
                    st.write(f"Highest {sales_col} region: **{ranked.index[0]}** ({ranked.iloc[0]:,.2f}).")
                elif sales_col and ("sales" in q or "revenue" in q):
                    st.write(f"Total {sales_col}: **{df[sales_col].sum():,.2f}**; average: **{df[sales_col].mean():,.2f}**.")
                elif "profit" in q and "Profit" in df.columns:
                    st.write(f"Total profit: **{df['Profit'].sum():,.2f}**; average profit: **{df['Profit'].mean():,.2f}**.")
                elif "missing" in q or "quality" in q:
                    st.write(f"The dataset contains **{df.isna().sum().sum():,}** missing values across **{df.shape[1]}** columns.")
                else:
                    st.write("I can currently answer questions about anomalies, sales/revenue totals, profit, regional sales, and missing values. Try one of those questions.")

        with tabs[5]:
            st.subheader("Download report")
            report = make_excel_report(df, anomalies, cleaning_report)
            st.download_button("📥 Download complete Excel report", report, "business_analytics_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.divider()
            st.subheader("Email anomaly alert")
            recipient = st.text_input("Recipient email address")
            if st.button("Send anomaly alert", disabled=(len(anomalies) == 0)):
                try:
                    send_email_alert(len(anomalies), len(df), recipient.strip())
                    st.success("Email alert sent.")
                except Exception as exc:
                    st.error(str(exc))
            st.caption("Email delivery requires SMTP credentials configured securely in your deployment secrets. Never paste passwords into the app.")

    except Exception as e:
        st.error(f"Could not analyze this file: {e}")
else:
    st.info("Upload an Excel or CSV file to start.")
    st.markdown("""
    ### What this app does
    - 📥 Upload Excel, XLS, or CSV business data
    - 🧹 Clean data and show a data-quality summary
    - 📊 Calculate KPIs and explore charts
    - 🤖 Detect unusual patterns using Isolation Forest
    - 🔎 Explain unusual metrics and assign review severity
    - 💡 Generate possible business context and answer basic dataset questions
    - 📥 Export analyzed data and a multi-sheet Excel report
    - ✉️ Send anomaly alerts when SMTP is configured
    """)
