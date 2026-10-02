import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    df = df.copy()

    numeric_columns = [
        c for c in ["Sales", "Quantity", "Discount", "Profit"]
        if c in df.columns
    ]

    if len(numeric_columns) < 2:
        raise ValueError(
            "At least two numeric business columns are required for anomaly detection."
        )

    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    df["Anomaly"] = model.fit_predict(df[numeric_columns])
    df["Anomaly Status"] = df["Anomaly"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    return df
