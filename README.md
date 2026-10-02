# AI-Powered Business Analytics Agent

A Streamlit business analytics application that accepts Excel/CSV data, performs automated cleaning and KPI analysis, detects unusual business records using Isolation Forest, explains unusual metrics, and generates rule-based business context.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then upload an Excel or CSV business dataset.

## Features

- Excel/CSV upload
- Data cleaning and validation
- KPI calculation
- Sales and profit trends
- Regional/category analytics
- Isolation Forest anomaly detection
- Metric-level anomaly explanation
- Rule-based business context
- Download analyzed CSV

## Note

The business context is a rule-based interpretation, not proof of the actual cause of an anomaly. The optional Generative AI layer can be added later.
