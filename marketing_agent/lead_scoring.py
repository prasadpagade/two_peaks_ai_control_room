# ------------------------------------------------------------
# Two Peaks – Marketing Lead Scoring Agent
# ------------------------------------------------------------
import os, re, time
import pandas as pd
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# --- Load env vars ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEETS_SPREADSHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME")
GOOGLE_SVC_JSON = os.getenv("GOOGLE_SVC_JSON")

# --- Google Sheets auth ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SVC_JSON, scope)
client = gspread.authorize(creds)
ss = client.open(SHEETS_SPREADSHEET_NAME)
raw_ws = ss.worksheet("Instagram_Engagement_Raw")

# Create or open destination sheet
try:
    ql_ws = ss.worksheet("Qualified_Leads")
except gspread.exceptions.WorksheetNotFound:
    ql_ws = ss.add_worksheet(title="Qualified_Leads", rows="100", cols="7")
    ql_ws.append_row(
        ["timestamp", "username", "comment", "likes", "followers", "score", "reason"]
    )

# --- Load recent engagement data ---
data = pd.DataFrame(raw_ws.get_all_records())
if data.empty:
    print("⚠️  No engagement data found. Run the webhook first.")
    exit()

# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)

prompt = PromptTemplate.from_template("""
You are a marketing analyst for a premium chai brand.
Evaluate this Instagram comment and rate purchase interest 1–10.

Username: {username}
Comment: "{comment}"
Followers: {followers}
Likes on comment: {likes}

Respond only as:
SCORE: <number> | REASON: <short reason>
""")

def parse_score(text):
    m = re.search(r"SCORE:\s*(\d+)", text)
    score = int(m.group(1)) if m else 5
    reason = re.sub(r".*REASON:\s*", "", text).strip() or "Neutral comment."
    return score, reason

# --- Score and append ---
for _, row in data.iterrows():
    message = prompt.format(
        username=row["username"],
        comment=row["comment"],
        followers=row["followers"],
        likes=row["likes"],
    )
    response = llm.invoke(message).content
    score, reason = parse_score(response)

    ql_ws.append_row([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        row["username"], row["comment"],
        row["likes"], row["followers"],
        score, reason
    ], value_input_option="RAW")

print("✅  Lead scoring complete — results added to 'Qualified_Leads'.")
