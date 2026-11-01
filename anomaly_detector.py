import pandas as pd
from sklearn.ensemble import IsolationForest

PREFERRED = ["Sales", "Revenue", "Profit", "Quantity", "Discount", "Price", "Cost", "Amount", "Total"]

def detect_anomalies(df, contamination=0.08):
    df = df.copy()
    numeric_columns = [c for c in PREFERRED if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric_columns) < 2:
        numeric_columns = [c for c in df.select_dtypes(include="number").columns if c not in {"Anomaly"}]
    if len(numeric_columns) < 2:
        df["Anomaly"] = 1
        df["Anomaly Status"] = "Not evaluated"
        df["Anomaly Severity"] = "N/A"
        df.attrs["anomaly_columns"] = numeric_columns
        return df

    features = df[numeric_columns].copy()
    features = features.replace([float("inf"), float("-inf")], pd.NA)
    features = features.fillna(features.median()).fillna(0)
    if len(features) < 5 or features.nunique().max() <= 1:
        predictions = [1] * len(df)
    else:
        model = IsolationForest(contamination=min(max(float(contamination), 0.01), 0.25), random_state=42, n_estimators=200)
        predictions = model.fit_predict(features)

    df["Anomaly"] = predictions
    df["Anomaly Status"] = pd.Series(predictions, index=df.index).map({1: "Normal", -1: "Anomaly"})
    df["Anomaly Severity"] = df["Anomaly Status"].map({"Normal": "Normal", "Anomaly": "Review"})
    df.attrs["anomaly_columns"] = numeric_columns
    return df
