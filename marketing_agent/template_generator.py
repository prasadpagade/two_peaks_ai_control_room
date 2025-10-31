# ------------------------------------------------------------
# Two Peaks – Marketing Template Generator
# ------------------------------------------------------------
import os, time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# --- Load environment variables ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME")
SERVICE_JSON = os.getenv("GOOGLE_SVC_JSON")

# --- Google Sheets auth ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_JSON, scope)
gc = gspread.authorize(creds)
ss = gc.open(SHEET_NAME)

# Source: Qualified_Leads
ql_ws = ss.worksheet("Qualified_Leads")

# Destination: Marketing_Templates
try:
    tpl_ws = ss.worksheet("Marketing_Templates")
except gspread.exceptions.WorksheetNotFound:
    tpl_ws = ss.add_worksheet(title="Marketing_Templates", rows="100", cols="5")
    tpl_ws.append_row(["timestamp", "username", "channel", "subject", "message"])

# --- Load leads ---
df = pd.DataFrame(ql_ws.get_all_records())
mqls = df[df["score"] >= 8]

if mqls.empty:
    print("⚠️  No qualified leads (score ≥ 8) found.")
    exit()

# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=OPENAI_API_KEY)

prompt = PromptTemplate.from_template("""
You are a friendly social-media copywriter for Two Peaks Chai Co.
Write a concise outreach message for user @{username}.
Tone: warm, authentic, lightly playful.
Mention something about {reason} and invite them to explore Two Peaks Chai.

Return two lines:
Subject: <short subject line>
Message: <1–2 sentences>
""")

# --- Generate templates ---
for _, r in mqls.iterrows():
    text = prompt.format(username=r["username"], reason=r["reason"])
    resp = llm.invoke(text).content
    subject = "Two Peaks Chai — Hello!"
    if "Subject:" in resp:
        parts = resp.split("Subject:")[-1].split("Message:")
        subject = parts[0].strip()
        message = parts[1].strip() if len(parts) > 1 else ""
    else:
        message = resp.strip()

    for channel in ["email", "instagram_dm"]:
        tpl_ws.append_row([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            r["username"], channel, subject, message
        ], value_input_option="RAW")

print("✅ Templates generated → 'Marketing_Templates' sheet updated.")
