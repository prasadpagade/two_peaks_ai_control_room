"""
Modular functions for generating and saving autonomous customer insights
for Two Peaks Chai Co. using GPT-4o-mini and Google Sheets.
"""

import os
import pandas as pd
import gspread
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------------------------------------------
# ENVIRONMENT & GLOBAL CONFIG
# ------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SHEET_NAME = "TwoPeaks_Marketing"

# ------------------------------------------------------------
# 1️⃣ LOAD CUSTOMER SEGMENT DATA
# ------------------------------------------------------------
def load_segment_data():
    """
    Loads the 'Customer_Segments' worksheet from TwoPeaks_Marketing Google Sheet.
    For Two Peaks Chai Co. brand context.
    Returns:
        pd.DataFrame: Clean DataFrame of customer segments.
    """
    try:
        gc = gspread.service_account(filename="service_account.json")
        ss = gc.open(SHEET_NAME)
        seg_ws = ss.worksheet("Customer_Segments")
        seg_df = pd.DataFrame(seg_ws.get_all_records())
        return seg_df
    except Exception as e:
        print(f"⚠️ Could not load Customer_Segments: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------
# 2️⃣ GENERATE INSIGHT SUMMARY (GPT-4o-mini)
# ------------------------------------------------------------
def generate_insight_summary(segment_df):
    """
    Generates a marketing insights report using GPT-4o-mini based on segment data.
    For Two Peaks Chai Co. brand context.
    Args:
        segment_df (pd.DataFrame): DataFrame containing customer segment data.
    Returns:
        str: AI-generated marketing insights report text.
    """
    if segment_df.empty:
        return "⚠️ No customer data available to generate insights."

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, api_key=OPENAI_API_KEY)
    parser = StrOutputParser()

    prompt_text = """
You are a marketing strategist for Two Peaks Chai Co., a premium DTC chai brand.
You have customer data showing total orders, total spend, average order value, recency, and assigned segments.

Analyze the following customer data and write a concise report (3–5 paragraphs) covering:
1. Overview of key customer segments and what they reveal.
2. Behavioral insights (buying frequency, loyalty, at-risk trends).
3. Recommendations for marketing actions (offers, retention, new product ideas).

Customer Segment Snapshot:
{segment_table}

Write the report in a warm, executive-friendly tone that fits Two Peaks’ brand — calm, reflective, and data-savvy.
End with a one-line summary headline.
"""
    prompt = PromptTemplate.from_template(prompt_text)
    segment_table = segment_df[
        ["Customer First Name", "Customer Last Name", "segment", "total_orders", "total_spent", "recency_days"]
    ].head(20).to_string(index=False)

    final_prompt = prompt.format(segment_table=segment_table)
    response = llm.invoke(final_prompt)

    response_text = getattr(response, "content", str(response))
    return response_text.strip()

# ------------------------------------------------------------
# 3️⃣ SAVE REPORT TO GOOGLE SHEETS
# ------------------------------------------------------------
def save_to_sheets(report_text, worksheet_name="Insights_Report"):
    """
    Saves the AI-generated marketing insights report to a Google Sheets tab.
    For Two Peaks Chai Co. brand context.
    Args:
        report_text (str): The report text to save.
        worksheet_name (str): The worksheet/tab name (default: "Insights_Report").
    """
    try:
        gc = gspread.service_account(filename="service_account.json")
        ss = gc.open(SHEET_NAME)

        # Delete if exists
        try:
            ws_old = ss.worksheet(worksheet_name)
            ss.del_worksheet(ws_old)
        except Exception:
            pass

        ws_new = ss.add_worksheet(title=worksheet_name, rows=100, cols=1)
        ws_new.update([["Generated Report"], [report_text]])
        print(f"✅ Report saved successfully to '{worksheet_name}' tab.")

    except Exception as e:
        print(f"❌ Failed to save report: {e}")

# ------------------------------------------------------------
# 4️⃣ QUICK TEST WRAPPER (Optional)
# ------------------------------------------------------------
def run_summary():
    """
    Convenience function to load segments → generate insights → save report.
    Used for debugging or autonomous workflows for Two Peaks Chai Co.
    """
    df = load_segment_data()
    report = generate_insight_summary(df)
    save_to_sheets(report)
    return report