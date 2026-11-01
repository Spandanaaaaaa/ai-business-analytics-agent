import pandas as pd

BUSINESS_NUMERIC_HINTS = ("sales", "revenue", "profit", "quantity", "discount", "price", "cost", "amount", "total")

def clean_data(df):
    """Clean common business fields without silently dropping unrelated columns."""
    df = df.copy()
    initial_rows = len(df)
    initial_missing = int(df.isna().sum().sum())
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").drop_duplicates()

    # Normalize common date column names to the existing app's Date convention.
    date_col = next((c for c in df.columns if c.lower().strip() in {"date", "order date", "transaction date"}), None)
    if date_col and date_col != "Date":
        df = df.rename(columns={date_col: "Date"})
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert known business measures and numeric-looking text columns.
    for col in df.columns:
        if col in {"Date"}:
            continue
        if col.lower() in {"sales", "revenue", "profit", "quantity", "discount", "price", "cost", "amount", "total"}:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[$,₹%]", "", regex=True), errors="coerce")
        elif df[col].dtype == "object":
            converted = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
            if converted.notna().mean() >= 0.85:
                df[col] = converted

    # Preserve rows where some measures are missing; downstream calculations handle nulls.
    df = df.reset_index(drop=True)
    report = {
        "input_rows": initial_rows,
        "output_rows": len(df),
        "removed_blank_or_duplicate_rows": initial_rows - len(df),
        "missing_values_before": initial_missing,
        "missing_values_after": int(df.isna().sum().sum()),
    }
    return df, report
