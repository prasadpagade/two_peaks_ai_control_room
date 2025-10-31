# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
import pandas as pd

def summarize_financials(df: pd.DataFrame) -> str:
    """
    Generates a mock AI-style financial summary.
    Future: Replace with LangChain + OpenAI once live Shopify data is available.
    """
    avg_roas = df["revenue"].sum() / df["ad_spend"].sum()
    top_region = df.groupby("region")["revenue"].sum().idxmax()
    total_revenue = df["revenue"].sum()
    total_orders = df["orders"].sum()

    summary = (
        f"Revenue for the past {len(df)} days totals ${total_revenue:.2f} "
        f"across {total_orders} orders. Average ROAS stands at {avg_roas:.2f}×. "
        f"{top_region} continues to be the top-performing region. "
        f"Focus on scaling ad spend efficiency and introducing repeat-customer rewards."
    )
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