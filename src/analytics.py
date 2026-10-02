import pandas as pd

def calculate_kpis(df):
    kpis = {}

    if "Sales" in df.columns:
        kpis["Total Sales"] = df["Sales"].sum()
        kpis["Average Sales"] = df["Sales"].mean()

    if "Profit" in df.columns:
        kpis["Total Profit"] = df["Profit"].sum()
        kpis["Average Profit"] = df["Profit"].mean()

    if "Quantity" in df.columns:
        kpis["Total Quantity"] = df["Quantity"].sum()

    if "Sales" in df.columns and len(df):
        kpis["Average Order Value"] = df["Sales"].sum() / len(df)

    return kpis

def create_daily_summary(df):
    if "Date" not in df.columns:
        return pd.DataFrame()

    cols = {}
    if "Sales" in df.columns:
        cols["Sales"] = ("Sales", "sum")
    if "Profit" in df.columns:
        cols["Profit"] = ("Profit", "sum")
    if "Quantity" in df.columns:
        cols["Quantity"] = ("Quantity", "sum")

    if not cols:
        return pd.DataFrame()

    daily = df.groupby("Date").agg(**cols).reset_index()
    return daily
