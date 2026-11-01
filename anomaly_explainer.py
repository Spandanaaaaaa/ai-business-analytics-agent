import pandas as pd
import numpy as np

def _robust_score(series, value):
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty or pd.isna(value):
        return 0.0
    median = clean.median()
    mad = np.median(np.abs(clean - median))
    if mad == 0:
        std = clean.std()
        if std == 0 or pd.isna(std):
            return 0.0
        return abs(value - clean.mean()) / std
    return abs(value - median) / (1.4826 * mad)

def explain_anomalies(df):
    df = df.copy()
    metrics = [c for c in df.select_dtypes(include="number").columns if c not in {"Anomaly"}]
    reasons, severities = [], []
    for _, row in df.iterrows():
        if row.get("Anomaly", 1) != -1:
            reasons.append("No unusual pattern detected")
            severities.append("Normal")
            continue
        unusual, max_score = [], 0
        for metric in metrics:
            score = _robust_score(df[metric], row.get(metric))
            max_score = max(max_score, score)
            if score >= 2.5:
                median = pd.to_numeric(df[metric], errors="coerce").median()
                direction = "high" if row[metric] > median else "low"
                unusual.append(f"{metric} unusually {direction} (robust score {score:.1f})")
        reasons.append("; ".join(unusual) if unusual else "Combination of numeric metrics is unusual")
        severities.append("High" if max_score >= 5 else "Medium")
    df["Anomaly Reason"] = reasons
    df["Anomaly Severity"] = severities
    return df
