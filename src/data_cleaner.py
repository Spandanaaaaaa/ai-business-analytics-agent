import pandas as pd

def clean_data(df):
    df = df.copy()
    df = df.dropna(how="all")
    df = df.drop_duplicates()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_columns = ["Sales", "Quantity", "Discount", "Profit"]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    existing = [c for c in numeric_columns if c in df.columns]
    if existing:
        df = df.dropna(subset=existing)

    return df.reset_index(drop=True)
