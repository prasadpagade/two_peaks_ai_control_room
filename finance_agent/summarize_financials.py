# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
import pandas as pd
import numpy as np

def summarize_financials(df: pd.DataFrame) -> str:
    """
    Generates a financial performance summary with safe handling for missing data.
    """

    # --- Normalize Columns ---
    if "ads" not in df.columns:
        if "ad_spend" in df.columns:
            df = df.rename(columns={"ad_spend": "ads"})
        else:
            df["ads"] = 0.0

    # Ensure all relevant columns exist and are numeric
    for col in ["revenue", "cogs", "fulfillment", "shipping", "overhead", "profit_margin"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["ads"] = pd.to_numeric(df["ads"], errors="coerce").fillna(0)

    # --- Compute Metrics ---
    total_revenue = df.get("revenue", pd.Series([0.0])).sum()
    total_ads = df.get("ads", pd.Series([0.0])).sum()
    total_cogs = df.get("cogs", pd.Series([0.0])).sum()
    total_fulfillment = df.get("fulfillment", pd.Series([0.0])).sum()
    total_shipping = df.get("shipping", pd.Series([0.0])).sum()
    total_overhead = df.get("overhead", pd.Series([0.0])).sum()

    total_expenses = total_cogs + total_ads + total_fulfillment + total_shipping + total_overhead
    avg_profit_margin = df["profit_margin"].mean() * 100 if "profit_margin" in df.columns else 0.0
    avg_roas = total_revenue / total_ads if total_ads > 0 else 0.0
    net_profit = total_revenue - total_expenses
    profitability = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    # --- Build Summary ---
    summary = (
        f"Over the past {len(df)} transactions, total revenue reached **${total_revenue:,.2f}**, "
        f"with total expenses of **${total_expenses:,.2f}**. "
        f"Advertising spend was **${total_ads:,.2f}**, yielding an average ROAS of **{avg_roas:.2f}×**. "
        f"Average profit margin stands at **{avg_profit_margin:.1f}%**, and overall profitability is **{profitability:.1f}%**. "
        f"Net profit for this period is **${net_profit:,.2f}**."
    )

    # --- Optional Insights ---
    if avg_profit_margin < 40:
        summary += " 💡 Profit margins are on the lower side — review pricing or sourcing strategy."
    elif avg_roas < 2:
        summary += " 📈 Consider optimizing ad performance to improve ROAS."
    else:
        summary += " ✅ Strong financial health detected this period."

    return summary

# ---- Future Integration (Commented Out) ----
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# prompt = PromptTemplate(
#     input_variables=["stats"],
#     template=(
#         "You are an AI financial analyst for Two Peaks Chai Co.\n"
#         "Given these KPIs, provide a 2–3 sentence summary with insights:\n{stats}"
#     )
# )
# response = llm.invoke(prompt.format(stats=df.describe().to_string()))
# return response.content