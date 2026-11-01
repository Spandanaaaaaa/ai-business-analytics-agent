import pandas as pd

def load_data(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    if name.endswith(".csv"):
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="latin-1")
    raise ValueError("Unsupported file format. Please upload XLSX, XLS, or CSV.")

def validate_data(df):
    if df is None or df.empty:
        raise ValueError("The uploaded file is empty or contains no records.")
    if len(df.columns) < 1:
        raise ValueError("The uploaded file does not contain any columns.")
    return df
