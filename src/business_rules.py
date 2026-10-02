import pandas as pd

def generate_business_context(df):
    df = df.copy()
    contexts = []

    sales_median = df["Sales"].median() if "Sales" in df.columns else None
    quantity_median = df["Quantity"].median() if "Quantity" in df.columns else None
    profit_median = df["Profit"].median() if "Profit" in df.columns else None

    for _, row in df.iterrows():
        if row["Anomaly"] != -1:
            contexts.append("No unusual business pattern detected.")
            continue

        sales = row.get("Sales")
        quantity = row.get("Quantity")
        profit = row.get("Profit")

        if sales_median is not None and quantity_median is not None:
            sales_low = sales < sales_median
            sales_high = sales > sales_median
            quantity_low = quantity < quantity_median
            quantity_high = quantity > quantity_median

            if sales_low and quantity_low:
                contexts.append(
                    "Sales and quantity are both below the typical level; "
                    "possible demand or sales-volume issue."
                )
                continue

            if sales_high and quantity_low:
                contexts.append(
                    "Sales are high while quantity is low; "
                    "pricing or high-value transactions may be worth investigating."
                )
                continue

        if profit_median is not None and sales_median is not None:
            if profit < profit_median and sales >= sales_median:
                contexts.append(
                    "Profit is low relative to sales; "
                    "costs, discounts, or margin pressure may require investigation."
                )
                continue

            if profit > profit_median and sales > sales_median:
                contexts.append(
                    "Sales and profit are both high; "
                    "this may represent an unusually strong transaction."
                )
                continue

        contexts.append(
            "The record is statistically unusual and should be investigated "
            "against the underlying business process."
        )

    df["Business Context"] = contexts
    return df
