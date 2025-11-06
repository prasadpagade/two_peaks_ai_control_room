import pandas as pd
import numpy as np

def generate_financial_metrics(df: pd.DataFrame) -> dict:
    """Compute financial KPIs safely for Two Peaks Chai Co."""
    if df is None or df.empty:
        return {
            "Total Revenue": 0,
            "Total Profit": 0,
            "Avg ROAS": 0,
            "Avg Profit Margin": 0,
            "Total Orders": 0,
        }

    df = df.copy()

    # --- Normalize ad_spend/ads column ---
    if "ad_spend" in df.columns:
        df = df.rename(columns={"ad_spend": "ads"})
    if "ads" not in df.columns:
        df["ads"] = 0.0

    # --- Ensure expected columns exist ---
    required_cols = ["revenue", "cogs", "ads", "fulfillment", "shipping", "overhead"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0
        # Convert to numeric, coercing errors and filling missing with 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # --- Derived metrics ---
    df["profit"] = (
        df["revenue"]
        - (
            df["cogs"]
            + df["ads"]
            + df["fulfillment"]
            + df["shipping"]
            + df["overhead"]
        )
    )

    # Avoid divide by zero for ROAS
    df["roas"] = np.where(df["ads"] > 0, df["revenue"] / df["ads"], 0).round(2)

    # Avoid divide by zero for profit margin
    df["profit_margin"] = np.where(df["revenue"] > 0, (df["profit"] / df["revenue"]) * 100, 0).round(2)

    # --- Aggregate metrics ---
    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    avg_roas = df["roas"].replace([np.inf, -np.inf], 0).mean()
    avg_profit_margin = df["profit_margin"].replace([np.inf, -np.inf], 0).mean()

    metrics = {
        "Total Revenue": round(total_revenue, 2),
        "Total Profit": round(total_profit, 2),
        "Avg ROAS": round(avg_roas, 2),
        "Avg Profit Margin": round(avg_profit_margin, 2),
        "Total Orders": int(len(df)),
    }

    return metrics