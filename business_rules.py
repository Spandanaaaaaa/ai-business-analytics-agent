import pandas as pd

def generate_business_context(df):
    df = df.copy()
    contexts = []
    numeric = [c for c in ["Sales", "Revenue", "Quantity", "Profit", "Discount", "Cost"] if c in df.columns]
    medians = {c: pd.to_numeric(df[c], errors="coerce").median() for c in numeric}
    sales_col = "Sales" if "Sales" in df.columns else ("Revenue" if "Revenue" in df.columns else None)
    for _, row in df.iterrows():
        if row.get("Anomaly", 1) != -1:
            contexts.append("No unusual business pattern detected.")
            continue
        sales = row.get(sales_col) if sales_col else None
        quantity = row.get("Quantity")
        profit = row.get("Profit")
        discount = row.get("Discount")
        if sales_col and quantity is not None and pd.notna(quantity):
            if sales < medians[sales_col] and quantity < medians["Quantity"]:
                contexts.append("Sales and quantity are both below typical levels; investigate demand, stock availability, or sales volume.")
                continue
            if sales > medians[sales_col] and quantity < medians["Quantity"]:
                contexts.append("Sales are high while quantity is low; review premium pricing or unusually high-value transactions.")
                continue
        if profit is not None and pd.notna(profit) and sales_col and pd.notna(sales):
            if profit < medians["Profit"] and sales >= medians[sales_col]:
                contexts.append("Profit is low relative to sales; review costs, discounts, and margin pressure.")
                continue
        if discount is not None and pd.notna(discount) and "Discount" in medians and discount > medians["Discount"]:
            contexts.append("Discount is above its typical level; check promotion rules and their effect on margin.")
            continue
        contexts.append("This record is statistically unusual. Compare it with the related transaction and operational records before deciding on a cause.")
    df["Business Context"] = contexts
    return df
