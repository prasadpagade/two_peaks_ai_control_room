import pandas as pd

def generate_financial_metrics(df: pd.DataFrame) -> dict:
    """Compute daily and aggregate financial KPIs for Two Peaks Chai Co."""
    df["profit"] = df["revenue"] - (df["ad_spend"] + df["cost_of_goods"] + df["refunds"])
    df["roas"] = (df["revenue"] / df["ad_spend"]).round(2)
    df["aov"] = (df["revenue"] / df["orders"]).round(2)

    latest = df.iloc[-1]
    total_profit = df["profit"].sum()
    total_revenue = df["revenue"].sum()

    metrics = {
        "Total Revenue": total_revenue,
        "Total Orders": df["orders"].sum(),
        "Avg ROAS": df["roas"].mean(),
        "Avg Profit Margin": (total_profit / total_revenue) * 100 if total_revenue else 0,
        "Latest Day": latest["date"],
        "Latest Revenue": latest["revenue"],
        "Latest ROAS": latest["roas"],
        "Latest Profit": latest["profit"],
    }

    return metrics