# ------------------------------------------------------------
# Two Peaks – Marketing Lead Scoring Agent (Autonomous Edition)
# ------------------------------------------------------------
import os, re, time
import pandas as pd
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_JSON = os.getenv("GOOGLE_SVC_JSON", "service_account.json")

# --- Google Auth ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_JSON, scope)
gc = gspread.authorize(creds)
ss = gc.open(SHEET_NAME)

def ensure_ws(title, headers):
    """Ensure a worksheet exists and has the correct headers."""
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows="1000", cols=str(len(headers)+3))
        ws.append_row(headers)
    return ws

raw_ws = ss.worksheet("Instagram_Engagement_Raw")
ql_ws = ensure_ws("Qualified_Leads", ["timestamp","username","comment","likes","followers","score","reason"])
mt_ws = ensure_ws("Marketing_Templates", ["timestamp","username","channel","subject","message","status"])

data = pd.DataFrame(raw_ws.get_all_records())
if data.empty:
    print("⚠️ No engagement data found.")
    exit()

# ------------------------------------------------------------
# LLM scoring setup
# ------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)
prompt = PromptTemplate.from_template("""
Evaluate this Instagram comment for purchase interest (1–10).

Username: {username}
Comment: "{comment}"
Followers: {followers}
Likes: {likes}

Reply strictly as:
SCORE: <number> | REASON: <short reason>
""")

def parse_score(resp):
    m = re.search(r"SCORE:\s*(\d+)", resp)
    score = int(m.group(1)) if m else 5
    reason = re.sub(r".*REASON:\s*", "", resp).strip()
    return score, reason or "Neutral comment."

# ------------------------------------------------------------
# Process and score rows
# ------------------------------------------------------------
now = time.strftime("%Y-%m-%d %H:%M:%S")
qualified, queued = [], []

print(f"🧠 Evaluating {len(data)} engagement rows...")
for _, row in data.iterrows():
    msg = prompt.format(**row)
    resp = llm.invoke(msg).content
    score, reason = parse_score(resp)

    qualified.append([
        now, row["username"], row["comment"], row["likes"], row["followers"], score, reason
    ])

    if score >= 7:
        queued.append([
            now, row["username"], "instagram", "Two Peaks Chai — Hello!", "Personalized message queued", "QUEUED"
        ])
    time.sleep(0.3)

if qualified:
    ql_ws.append_rows(qualified, value_input_option="RAW")
if queued:
    mt_ws.append_rows(queued, value_input_option="RAW")

print(f"✨ Lead scoring complete — {len(qualified)} processed, {len(queued)} queued for outreach.")