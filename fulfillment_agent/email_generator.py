# fulfillment_agent/email_generator.py
# ------------------------------------------------------------
# Two Peaks – Fulfillment Email Generator (GPT-personalized)
# ------------------------------------------------------------
import os, time
import pandas as pd
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# ------------------------------------------------------------
# ENV + SHEETS CONFIG
# ------------------------------------------------------------
load_dotenv()
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_JSON = os.getenv("GOOGLE_SVC_JSON", "service_account.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(SERVICE_JSON, scopes=SCOPES)
gc = gspread.authorize(creds)
ss = gc.open(SHEET_NAME)

# ------------------------------------------------------------
# Source + Destination Sheets
# ------------------------------------------------------------
src_ws = ss.worksheet("PostPurchase_Engagement_Log")

try:
    dest_ws = ss.worksheet("Fulfillment_Templates")
except gspread.exceptions.WorksheetNotFound:
    dest_ws = ss.add_worksheet(title="Fulfillment_Templates", rows="500", cols="7")
    dest_ws.append_row(["timestamp", "order_id", "first_name", "email", "subject", "message", "status"])

# ------------------------------------------------------------
# Load shipped orders
# ------------------------------------------------------------
df = pd.DataFrame(src_ws.get_all_records())
shipped = df[df["status"].str.upper() == "SHIPPED"]

if shipped.empty:
    print("⚠️ No shipped orders found — nothing to generate.")
    exit()

# ------------------------------------------------------------
# LLM Setup
# ------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=OPENAI_API_KEY)

prompt = PromptTemplate.from_template("""
You are a warm, grateful brand founder writing a personalized thank-you email
to a customer of Two Peaks Chai Co.

Customer details:
- Name: {first_name}
- Product: {product}

Write a short email with:
- a friendly thank-you note
- mention that their order has shipped
- invite them to watch a short chai-making video from your grandmother’s recipe
- include this YouTube link: https://www.youtube.com/watch?v=EaKA3Wc-49s
- invite them to leave a review if they enjoy it.

Tone: sincere, authentic, slightly playful, under 120 words.
Return two fields:
Subject: <short subject line>
Message: <personalized body text>
""")

# ------------------------------------------------------------
# Generate personalized emails
# ------------------------------------------------------------
rows = []
for _, r in shipped.iterrows():
    text = prompt.format(first_name=r["first_name"], product=r["products"])
    response = llm.invoke(text).content

    subject = "Your chai is on its way ☕️"
    message = response.strip()

    if "Subject:" in response:
        parts = response.split("Subject:")[-1].split("Message:")
        subject = parts[0].strip()
        message = parts[1].strip() if len(parts) > 1 else message

    rows.append([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        r["order_id"],
        r["first_name"],
        r["email"],
        subject,
        message,
        "QUEUED"
    ])
    print(f"✅ Generated thank-you email for {r['first_name']} ({r['products']})")

# ------------------------------------------------------------
# Write to Sheets
# ------------------------------------------------------------
dest_ws.append_rows(rows, value_input_option="RAW")
print(f"✅ Added {len(rows)} personalized emails → 'Fulfillment_Templates' (QUEUED).")