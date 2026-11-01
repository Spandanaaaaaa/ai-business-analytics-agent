import pandas as pd

def calculate_kpis(df):
    kpis = {}
    sales_col = "Sales" if "Sales" in df.columns else ("Revenue" if "Revenue" in df.columns else None)
    if sales_col:
        kpis["Total Sales / Revenue"] = pd.to_numeric(df[sales_col], errors="coerce").sum()
        kpis["Average Sales / Revenue"] = pd.to_numeric(df[sales_col], errors="coerce").mean()
        kpis["Average Order Value"] = pd.to_numeric(df[sales_col], errors="coerce").sum() / max(len(df), 1)
    for col, label in [("Profit", "Total Profit"), ("Quantity", "Total Quantity")]:
        if col in df.columns:
            kpis[label] = pd.to_numeric(df[col], errors="coerce").sum()
    if "Profit" in df.columns and sales_col:
        total_sales = pd.to_numeric(df[sales_col], errors="coerce").sum()
        kpis["Profit Margin (%)"] = (pd.to_numeric(df["Profit"], errors="coerce").sum() / total_sales * 100) if total_sales else 0
    return kpis

def create_daily_summary(df):
    if "Date" not in df.columns or not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        return pd.DataFrame()
    measures = [c for c in ["Sales", "Revenue", "Profit", "Quantity"] if c in df.columns]
    if not measures:
        return pd.DataFrame()
    return df.dropna(subset=["Date"]).groupby("Date", as_index=False)[measures].sum().sort_values("Date")
