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
with tab2:
    st.subheader("Generated Outreach Templates")
    if templates_df.empty:
        st.info("No templates yet. Run template_generator.py.")
    else:
        selected = st.selectbox(
            "Select a template to review:",
            options=templates_df.index,
            format_func=lambda i: f"@{templates_df.loc[i,'username']} ({templates_df.loc[i,'channel']})"
        )

        row = templates_df.loc[selected]
        st.write(f"**User:** @{row['username']} | **Channel:** {row['channel']}")
        subject = st.text_input("Subject", row["subject"])
        message = st.text_area("Message", row["message"], height=180)
        approved = st.checkbox("Approve for Send")

        if approved:
            tpl_ws.update_cell(selected + 2, templates_df.columns.get_loc("subject") + 1, subject)
            tpl_ws.update_cell(selected + 2, templates_df.columns.get_loc("message") + 1, message)

            # --- SAFE FIX: make sure we have enough columns for approval status ---
            needed_cols = 10  # add buffer columns if needed
            if tpl_ws.col_count < needed_cols:
                tpl_ws.add_cols(needed_cols - tpl_ws.col_count)

            # Write "APPROVED" to status column
            tpl_ws.update_cell(selected + 2, templates_df.columns.get_loc("status") + 1, "APPROVED")

            
            st.success("Template approved ✅")

st.divider()
st.caption("Use n8n to deliver approved templates → Instagram DM / Email")
