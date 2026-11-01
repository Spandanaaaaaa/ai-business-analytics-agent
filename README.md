# AI-Powered Business Analytics Agent

An enhanced version of the existing Streamlit project. It keeps the same app identity and original modules while adding richer data quality reporting, flexible KPI exploration, anomaly severity, an analytics Q&A helper, Excel reporting, and optional email alerts.

## Features
- Upload Excel (`.xlsx`, `.xls`) and CSV files
- Clean blank/duplicate rows, parse common date columns, and convert common business measures
- Data-quality snapshot and cleaning summary
- Business KPIs including revenue/sales, profit, quantity, average order value, and profit margin where available
- Interactive metric and category charts
- Isolation Forest anomaly detection with configurable expected anomaly proportion
- Metric-level anomaly explanations and High/Medium review severity
- Rule-based business context (possible explanations, not confirmed causes)
- Basic dataset Q&A for anomaly, sales/revenue, profit, regional sales, and missing-value questions
- Download analyzed CSV, anomaly CSV, and multi-sheet Excel report
- Optional SMTP email alerts

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional email configuration
Configure these environment variables or Streamlit secrets on the existing deployment:
- `SMTP_HOST`
- `SMTP_PORT` (usually `587`)
- `SMTP_EMAIL`
- `SMTP_PASSWORD`

Do not commit credentials to GitHub. Email alerts remain unavailable until SMTP is configured.

## Important notes
- Isolation Forest identifies statistically unusual records; it does not prove fraud, mistakes, or business causes.
- Business context is rule-based and should be validated against source systems.
- The in-app analytics assistant currently uses local dataset calculations. It does not send data to an external GenAI provider.
- Keep the existing GitHub repository, branch, Streamlit app, and demo URL. Update the existing repository with these files rather than creating a second deployment.
