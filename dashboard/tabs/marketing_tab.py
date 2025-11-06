# ============================================================
# marketing_tab.py — Two Peaks AI Control Room
# End-to-end autonomous workflow:
# Engagement → Lead Scoring → Template Generation → Human Review → Gmail Send
# ============================================================

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import time
import subprocess
from dotenv import load_dotenv

# ------------------------------------------------------------
# CONFIG & SETUP
# ------------------------------------------------------------
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
os.environ.pop("GSPREAD_OAUTH_CREDENTIALS_PATH", None)
os.environ.pop("GSPREAD_CREDENTIALS_FILENAME", None)

SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_ACCOUNT = os.getenv("GOOGLE_SVC_JSON", "service_account.json")

# ------------------------------------------------------------
# Helper — Fetch Google Sheet Data
# ------------------------------------------------------------
def get_sheet_data(sheet_name):
    try:
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME)
        worksheet = sheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error fetching data from {sheet_name}: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------
# Full Marketing Workflow (Autonomous)
# ------------------------------------------------------------
def run_marketing_workflow():
    try:
        with st.spinner("🚀 Running full Marketing Automation pipeline..."):
            # ------------------------------------------------------------
            # 0️⃣ Setup paths & environment
            # ------------------------------------------------------------
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            agent_dir = os.path.join(base_path, "marketing_agent")
            env_path = os.path.join(base_path, ".env")

            # ✅ Load environment variables (for Sheets + service account)
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                st.info(f"✅ Environment variables loaded from {env_path}")
            else:
                st.warning("⚠️ .env file not found — subprocesses may fail.")

            # ------------------------------------------------------------
            # 1️⃣ Simulated cross-platform engagement fetch
            # ------------------------------------------------------------
            st.toast("📡 Simulating cross-platform engagement fetch...")
            time.sleep(0.6)
            st.write("🔒 Authenticating with Instagram API (simulated)...")
            time.sleep(0.4)
            st.write("🔒 Authenticating with LinkedIn API (simulated)...")
            time.sleep(0.4)
            st.write("✅ Auth OK — requesting recent comments and likes...")
            time.sleep(0.6)
            st.write("⬇️  Received 5 new engagement rows (total 5)")
            time.sleep(0.3)
            st.write("✨ Finished simulated API sync — inserting into sheet...")

            # ------------------------------------------------------------
            # 2️⃣ Generate fake engagement data
            # ------------------------------------------------------------
            st.toast("📸 Generating engagement data...")
            add_cmd = ["python", f"{agent_dir}/add_fake_engagement.py"]
            result1 = subprocess.run(add_cmd, capture_output=True, text=True, env=os.environ.copy())
            st.code(result1.stdout or result1.stderr)
            if result1.returncode == 0:
                st.success("✅ Engagement data added successfully.")
            else:
                st.error("❌ Engagement data script failed.")
                st.stop()

            # ------------------------------------------------------------
            # 3️⃣ Run lead scoring agent
            # ------------------------------------------------------------
            st.toast("🧠 Running lead scoring agent...")
            lead_cmd = ["python", f"{agent_dir}/lead_scoring.py"]
            result2 = subprocess.run(lead_cmd, capture_output=True, text=True, env=os.environ.copy())
            st.code(result2.stdout or result2.stderr)
            if result2.returncode == 0:
                st.success("✅ Lead scoring complete — Qualified_Leads updated.")
            else:
                st.error("❌ Lead scoring failed.")
                st.stop()

            # ------------------------------------------------------------
            # 4️⃣ Generate personalized marketing templates
            # ------------------------------------------------------------
            st.toast("✉️ Creating marketing templates...")
            tpl_cmd = ["python", f"{agent_dir}/template_generator.py"]
            result3 = subprocess.run(tpl_cmd, capture_output=True, text=True, env=os.environ.copy())
            st.code(result3.stdout or result3.stderr)
            if result3.returncode == 0:
                st.success("✅ Templates generated — Marketing_Templates updated (QUEUED).")
            else:
                st.error("❌ Template generation failed.")
                st.stop()

            # ------------------------------------------------------------
            # 5️⃣ Simulated n8n Heartbeat (UI only)
            # ------------------------------------------------------------
            st.info("🌐 Simulating sync with n8n marketing pipeline...")
            time.sleep(0.6)
            st.success("✅ [Simulated] n8n heartbeat acknowledged — all agents in sync.")

            # ------------------------------------------------------------
            # 6️⃣ Refresh dashboard
            # ------------------------------------------------------------
            st.toast("🔄 Refreshing dashboard view...")
            time.sleep(3)
            # Use modern rerun function
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                # Backward compatibility for older Streamlit versions
                st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Marketing workflow error: {e}")

# ------------------------------------------------------------
# Render Marketing Agent Tab
# ------------------------------------------------------------
def render_marketing_tab():
    st.header("📈 Marketing & Lead Qualification Agent")
    st.caption("Captures engagement → qualifies leads → generates outreach templates → human approval → email send")

    # --- Load metrics ---
    engagement_df = get_sheet_data("Instagram_Engagement_Raw")
    leads_df = get_sheet_data("Qualified_Leads")
    email_df = get_sheet_data("Marketing_Templates")

    c1, c2, c3 = st.columns(3)
    c1.metric("Engagements", len(engagement_df))
    c2.metric("Qualified Leads", len(leads_df))
    c3.metric("Emails Generated", len(email_df))

    st.markdown("###")
    if st.button("▶️ Call Maketing AI Agent (End-to-End)"):
        run_marketing_workflow()