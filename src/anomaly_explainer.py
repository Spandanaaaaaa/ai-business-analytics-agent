import pandas as pd
import numpy as np

def _robust_score(series, value):
    median = series.median()
    mad = np.median(np.abs(series - median))

    if mad == 0:
        std = series.std()
        if std == 0 or pd.isna(std):
            return 0
        return abs(value - series.mean()) / std

    return abs(value - median) / (1.4826 * mad)

def explain_anomalies(df):
    df = df.copy()

    metrics = [
        c for c in ["Sales", "Quantity", "Discount", "Profit"]
        if c in df.columns
    ]

    reasons = []

    for idx, row in df.iterrows():
        if row["Anomaly"] != -1:
            reasons.append("Normal business pattern")
            continue

        unusual = []

        for metric in metrics:
            score = _robust_score(df[metric], row[metric])
            if score >= 2.5:
                median = df[metric].median()
                direction = "high" if row[metric] > median else "low"
                unusual.append(f"{metric} unusually {direction}")

        if unusual:
            reasons.append("; ".join(unusual))
        else:
            reasons.append("Combination of metrics is unusual")

    df["Anomaly Reason"] = reasons
    return df
