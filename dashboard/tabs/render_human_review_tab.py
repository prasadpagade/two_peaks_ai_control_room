import streamlit as st
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

def render_human_review_tab():
    st.markdown("---")
    st.subheader("🧠 Human Review Queue — Approve Queued Marketing Emails")

    # ------------------------------------------------------------
    # CONFIG & SETUP
    # ------------------------------------------------------------
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    os.environ.pop("GSPREAD_OAUTH_CREDENTIALS_PATH", None)
    os.environ.pop("GSPREAD_CREDENTIALS_FILENAME", None)

    SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
    SERVICE_ACCOUNT = os.getenv("GOOGLE_SVC_JSON", "service_account.json")
    #WEBHOOK_URL = os.getenv("N8N_MARKETING_URL")

    if not SERVICE_ACCOUNT or not SHEET_NAME:
        st.error("⚠️ GOOGLE_SVC_JSON and SHEETS_SPREADSHEET_NAME environment variables must be set.")
        return

    # --- Auto-refresh each time tab is revisited ---
    if "refresh_flag" not in st.session_state:
        st.session_state.refresh_flag = 0
    else:
        st.session_state.refresh_flag += 1

    # Clear cache so latest data always loads when tab is reopened
    st.cache_data.clear()

    if not hasattr(st, "rerun"):
        st.rerun = st.experimental_rerun

    try:
        # ---- Google Sheets Connection ----
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME)
        tpl_ws = sheet.worksheet("Marketing_Templates")
        templates_df = pd.DataFrame(tpl_ws.get_all_records())

        # ---- Diagnostics ----
        st.caption(f"📊 Loaded {len(templates_df)} templates from Google Sheets.")
        if not templates_df.empty:
            st.dataframe(
                templates_df.head(),
                use_container_width=True,
                hide_index=True,
            )

        # ---- Normalize and verify columns ----
        templates_df.columns = templates_df.columns.map(lambda c: str(c).strip().lower() if not isinstance(c, str) else c.strip().lower())
        st.caption(f"🧩 Normalized columns: {list(templates_df.columns)}")
        if "status" not in templates_df.columns:
            possible = [c for c in templates_df.columns if "status" in c.lower()]
            if possible:
                templates_df.rename(columns={possible[0]: "status"}, inplace=True)
            else:
                st.warning(f"⚠️ 'status' column not found in Marketing_Templates. Columns available: {list(templates_df.columns)}")
                return
        else:
            # ---- Filter QUEUED entries ----
            queued_df = templates_df[
                templates_df["status"].astype(str).str.upper().str.strip() == "QUEUED"
            ]

            # ---- Refresh ----
            if st.button("🔄 Refresh Queue"):
                st.rerun()

            # ---- Show Results ----
            if queued_df.empty:
                st.info("✅ No queued templates right now.")
            else:
                st.success(f"🕒 {len(queued_df)} templates awaiting approval")

                for idx, row in queued_df.iterrows():
                    with st.expander(
                        f"📩 @{row['username']} ({row.get('channel', 'email')}) — {row['status']}"
                    ):
                        subject = st.text_input(
                            "Subject", row.get("subject", ""), key=f"subj_{idx}"
                        )
                        message = st.text_area(
                            "Message", row.get("message", ""), height=160, key=f"msg_{idx}"
                        )

                        c1, c2 = st.columns([1, 1])
                        if c1.button("✅ Approve & Send", key=f"approve_{idx}"):
                            tpl_ws.update_cell(
                                idx + 2, templates_df.columns.get_loc("subject") + 1, subject
                            )
                            tpl_ws.update_cell(
                                idx + 2, templates_df.columns.get_loc("message") + 1, message
                            )
                            tpl_ws.update_cell(
                                idx + 2,
                                templates_df.columns.get_loc("status") + 1,
                                "APPROVED",
                            )
                            st.success(
                                f"Approved ✅ @{row['username']} — Gmail automation will send shortly."
                            )
                            st.rerun()

                        if c2.button("🗑️ Reject", key=f"reject_{idx}"):
                            tpl_ws.update_cell(
                                idx + 2,
                                templates_df.columns.get_loc("status") + 1,
                                "REJECTED",
                            )
                            st.warning(f"Rejected ❌ @{row['username']} removed from queue.")
                            st.rerun()

    except Exception as e:
        st.error(f"⚠️ Could not load Marketing_Templates for review: {e}")