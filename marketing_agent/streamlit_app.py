# ------------------------------------------------------------
# Two Peaks – Marketing Agent Dashboard (Streamlit)
# ------------------------------------------------------------
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import streamlit as st

# --- Load environment ---
load_dotenv()
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME")
SERVICE_JSON = os.getenv("GOOGLE_SVC_JSON")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_JSON, scope)
gc = gspread.authorize(creds)
ss = gc.open(SHEET_NAME)

# --- Read data ---
ql_ws = ss.worksheet("Qualified_Leads")
tpl_ws = ss.worksheet("Marketing_Templates")

leads_df = pd.DataFrame(ql_ws.get_all_records())
records = tpl_ws.get_all_records(expected_headers=["timestamp", "username", "channel", "subject", "message", "status"])
templates_df = pd.DataFrame(records)


# --- UI Layout ---
st.set_page_config(page_title="Two Peaks – Marketing Agent", layout="wide")
st.title("🫖 Two Peaks AI — Marketing Agent Dashboard")

tab1, tab2 = st.tabs(["Qualified Leads", "Outreach Templates"])

# ---------------------------- TAB 1 ----------------------------
with tab1:
    st.subheader("Qualified Leads (Score ≥ 8)")
    if leads_df.empty:
        st.info("No leads available yet.")
    else:
        st.dataframe(
            leads_df.sort_values("score", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# ---------------------------- TAB 2 ----------------------------
# ---------------------------- TAB 2 ----------------------------
with tab2:
    st.subheader("Generated Outreach Templates")

    queued_df = templates_df[templates_df["status"].str.upper() == "QUEUED"]

    if queued_df.empty:
        st.info("No queued templates. Run scoring or wait for n8n content generation.")
    else:
        for idx, row in queued_df.iterrows():
            st.markdown(f"### @{row['username']} ({row['channel']})")
            subject = st.text_input("Subject", row["subject"] or "", key=f"subj_{idx}")
            message = st.text_area("Message", row["message"] or "", height=160, key=f"msg_{idx}")

            if st.button(f"✅ Approve & Send to {row['username']}", key=f"approve_{idx}"):
                tpl_ws.update_cell(idx + 2, templates_df.columns.get_loc("subject") + 1, subject)
                tpl_ws.update_cell(idx + 2, templates_df.columns.get_loc("message") + 1, message)
                tpl_ws.update_cell(idx + 2, templates_df.columns.get_loc("status") + 1, "APPROVED")
                st.success(f"Approved ✅ – Workflow will auto-send via Gmail soon.")

            st.divider()

st.divider()
st.caption("Use n8n to deliver approved templates → Instagram DM / Email")
