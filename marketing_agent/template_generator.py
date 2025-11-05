# ------------------------------------------------------------
# Two Peaks – Marketing Template Generator (Personalized & Clean Edition)
# ------------------------------------------------------------

import os
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# ------------------------------------------------------------
# Load environment & configure
# ------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_JSON = os.getenv("GOOGLE_SVC_JSON", "service_account.json")

# ------------------------------------------------------------
# Google Sheets auth & worksheet handles
# ------------------------------------------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_JSON, scope)
gc = gspread.authorize(creds)
ss = gc.open(SHEET_NAME)

# Ensure Marketing_Templates exists with correct headers
try:
    tpl_ws = ss.worksheet("Marketing_Templates")
except gspread.exceptions.WorksheetNotFound:
    tpl_ws = ss.add_worksheet(title="Marketing_Templates", rows="1000", cols="6")
    tpl_ws.append_row(["timestamp", "username", "channel", "subject", "message", "status"])

# Load qualified leads (keep only strong scores)
ql_ws = ss.worksheet("Qualified_Leads")
df = pd.DataFrame(ql_ws.get_all_records())
if df.empty:
    print("⚠️  No qualified leads data found in 'Qualified_Leads'.")
    raise SystemExit(0)

mqls = df[df.get("score", 0) >= 7].copy()
if mqls.empty:
    print("⚠️  No qualified leads (score ≥ 7).")
    raise SystemExit(0)

# ------------------------------------------------------------
# Helper: Cleanup placeholder rows
# ------------------------------------------------------------
def clean_placeholder_rows():
    try:
        all_rows = tpl_ws.get_all_records()
        delete_indices = []
        for i, row in enumerate(all_rows, start=2):  # Skip header
            subj = str(row.get("subject", "")).strip()
            msg = str(row.get("message", "")).strip().lower()
            if subj == "Two Peaks Chai — Hello!" and msg == "personalized message queued":
                delete_indices.append(i)

        if delete_indices:
            print(f"🧹 Cleaning up {len(delete_indices)} placeholder rows...")
            for idx in sorted(delete_indices, reverse=True):
                tpl_ws.delete_rows(idx)
            print("✅ Placeholder rows removed successfully.")
        else:
            print("✨ No placeholder rows found — sheet already clean.")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

# Initial cleanup before generating new templates
clean_placeholder_rows()

# ------------------------------------------------------------
# LLM setup for copy generation
# ------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6, api_key=OPENAI_API_KEY)

prompt = PromptTemplate.from_template("""
You are a warm, emotionally intelligent social media copywriter for Two Peaks Chai Co.

Your goal is to write a *personalized, thoughtful outreach message* to user @{username}
based on their engagement with our brand.

Here’s what we know about them:
- Their comment: "{comment}"
- Likes: {likes}
- Followers: {followers}
- Reason for scoring: {reason}

Tone: friendly, authentic, and chai-inspired — include warmth, gratitude, and subtle humor.
Each note should feel hand-crafted, like a genuine human message.

Return two lines:
1️⃣ A creative subject line (5–8 words, no emojis).
2️⃣ A personal message (2–3 sentences) that connects to their comment and gently invites them to explore or revisit Two Peaks Chai.
Separate the two lines with a blank line.
""")

# ------------------------------------------------------------
# Generate personalized templates
# ------------------------------------------------------------
rows = []
print(f"✉️ Generating personalized messages for {len(mqls)} leads...")

for _, r in mqls.iterrows():
    text = prompt.format(
        username=r["username"],
        comment=r["comment"],
        likes=r["likes"],
        followers=r["followers"],
        reason=r["reason"],
    )

    resp = llm.invoke(text).content.strip()

    # Split at first double newline (subject + message)
    if "\n\n" in resp:
        parts = resp.split("\n\n", 1)
        subject = parts[0].strip()
        message = parts[1].strip()
    else:
        subject = "Two Peaks Chai — Hello!"
        message = resp.strip()

    # Fallback for short or invalid messages
    if not message or len(message) < 25:
        message = (
            f"Hey @{r['username']}! We absolutely love your chai energy — "
            "thank you for spreading the warmth! Come explore the cozy world of Two Peaks Chai ☕️✨"
        )

    # Add both email + instagram versions
    rows.append([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        r["username"],
        "email",
        subject,
        message,
        "QUEUED",
    ])
    rows.append([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        r["username"],
        "instagram",
        subject,
        message,
        "QUEUED",
    ])
    time.sleep(0.3)

tpl_ws.append_rows(rows, value_input_option="RAW")
print(f"✅ Templates generated → {len(rows)} total messages added to Marketing_Templates.")

# Final cleanup after adding rows
clean_placeholder_rows()