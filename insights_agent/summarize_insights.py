# insights_agent/summarize_insights.py
import pandas as pd
import gspread
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# Optional check
# print("Loaded OpenAI key prefix:", os.getenv("OPENAI_API_KEY")[:8])

# --- 1. Setup ---
gc = gspread.service_account(filename="service_account.json")
ss = gc.open("TwoPeaks_Marketing")

# Load customer segment data
seg_ws = ss.worksheet("Customer_Segments")
seg_df = pd.DataFrame(seg_ws.get_all_records())

# --- 2. Prepare LLM ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
parser = StrOutputParser()

# --- 3. Prompt Template ---
prompt_text = """
You are a marketing strategist for Two Peaks Chai Co., a premium DTC chai brand.
You have customer data showing total orders, total spend, average order value, recency, and assigned segments.

Analyze the following customer data and write a concise report (3–5 paragraphs) covering:
1. Overview of key customer segments and what they reveal.
2. Behavioral insights (buying frequency, loyalty, at-risk trends).
3. Recommendations for marketing actions (offers, retention, new product ideas).

Customer Segment Snapshot:
{segment_table}

Write the report in a clear, executive-friendly tone as if presenting to founders.
End with a one-line summary headline.
"""
prompt = PromptTemplate.from_template(prompt_text)

# Format input table
segment_table = seg_df[["Customer First Name", "Customer Last Name", "segment", "total_orders", "total_spent", "recency_days"]].head(20).to_string(index=False)

# --- 4. Run LLM ---
final_prompt = prompt.format(segment_table=segment_table)
response = llm.invoke(final_prompt)

# Extract plain text from AIMessage
if hasattr(response, "content"):
    response_text = response.content
else:
    response_text = str(response)

# --- 5. Write output to new Google Sheet tab ---
try:
    ws_old = ss.worksheet("Insights_Report")
    ss.del_worksheet(ws_old)
except Exception:
    pass

ws_new = ss.add_worksheet(title="Insights_Report", rows=100, cols=1)
#ws_new.update([["Generated Report"], [response_text[:49500]]])
ws_new.update([["Generated Report"], [response_text]])

print("✅ Insights report created! Check 'Insights_Report' tab in your sheet.")