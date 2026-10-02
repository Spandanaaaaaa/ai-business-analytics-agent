import pandas as pd

def load_data(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    raise ValueError("Unsupported file format. Please upload XLSX or CSV.")

def validate_data(df):
    if df.empty:
        raise ValueError("The uploaded file is empty.")
    return df
