# tabs/fulfillment_tab.py
import streamlit as st
import pandas as pd
import random, os, time
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
from dotenv import load_dotenv

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
load_dotenv()
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_ACCOUNT = os.getenv("GOOGLE_SVC_JSON", "service_account.json")

# ------------------------------------------------------------
# GOOGLE SHEETS HELPERS
# ------------------------------------------------------------
def _gs_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=scopes)
    return gspread.authorize(creds)

def _get_ws(title: str):
    """Return worksheet by title, creating with headers if needed."""
    headers_map = {
        "PostPurchase_Engagement_Log": [
            "timestamp", "order_id", "email", "first_name",
            "products", "total", "status", "email_message_id"
        ],
        "Fulfillment_Templates": [
            "timestamp", "order_id", "email", "first_name", "subject", "message", "status", "reviewed_by", "sent_at"
        ]
    }
    gc = _gs_client()
    ss = gc.open(SHEET_NAME)
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows="1000", cols=str(len(headers_map[title]) + 2))
        ws.append_row(headers_map[title])
    return ws

def _ws_df(title: str):
    ws = _get_ws(title)
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    return df

def _append_rows(title: str, rows: list[list]):
    ws = _get_ws(title)
    if rows:
        ws.append_rows(rows, value_input_option="RAW")

def _update_status_by_order_ids(title: str, order_ids: list[str], new_status: str):
    """Update 'status' for matching order_ids in the sheet."""
    ws = _get_ws(title)
    data = ws.get_all_values()
    if not data:
        return 0
    headers = [h.strip().lower() for h in data[0]]
    try:
        id_idx = headers.index("order_id")
        status_idx = headers.index("status")
    except ValueError:
        return 0
    count = 0
    for i, row in enumerate(data[1:], start=2):
        if len(row) > id_idx and row[id_idx] in set(order_ids):
            ws.update_cell(i, status_idx + 1, new_status)
            count += 1
    return count

# ------------------------------------------------------------
# GPT Email Generation (Post-Purchase Fulfillment)
# ------------------------------------------------------------
from openai import OpenAI

def _generate_postpurchase_email(first_name, products, video_url):
    prompt = f"""You are a friendly chai brand fulfillment agent. Write a warm, personalized post-purchase email for a customer named {first_name} who ordered: {products}.
Requirements:
- Thank them for their order and support.
- Share a link to a step-by-step brewing tutorial video: {video_url}
- Invite them to reply with feedback or questions.
- Kindly request a product review if they enjoyed it.
- Keep the tone warm, grateful, and community-oriented.
- End the message with this signature (do not use placeholders or any other names/roles):

Warm regards,
Prasad and Hannah
Founders of Two Peaks Chai Co.

Format:
Subject: (short, friendly)
Body: (plain text, 3-6 sentences, include video link and signature above)
"""
    # Use OpenAI GPT (assumes API key in env var)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in customer engagement for a chai DTC brand."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.8,
    )
    text = response.choices[0].message.content
    # Split subject/body
    subject = ""
    message = ""
    lines = text.strip().splitlines()
    for i, l in enumerate(lines):
        if l.strip().lower().startswith("subject:"):
            subject = l.split(":", 1)[1].strip()
            message = "\n".join(lines[i+1:]).strip()
            break
    if not subject:
        subject = "Thank you for your order!"
        message = text.strip()
    return subject, message

def _generate_mock_orders(n: int = 10) -> pd.DataFrame:
    """Generate realistic mock Shopify orders."""
    first_names = ["Asha", "Hannah", "Raj", "Sophia", "Ethan", "Maya", "Noah", "Leah", "Kiran", "Zoe"]
    products = [
        "Signature Masala Chai", "Rose Radiance Chai", "Golden Glow Chai",
        "Saffron Infused Chai", "Assam Breakfast Chai",
    ]
    rows = []
    for i in range(n):
        rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "order_id": f"TP-{random.randint(10000, 99999)}",
            "email": f"customer{i}@example.com",
            "first_name": random.choice(first_names),
            "products": random.choice(products),
            "total": round(random.uniform(12, 45), 2),
            "status": random.choice(["SHIPPED", "PENDING", "DELIVERED"]),
            "email_message_id": ""
        })
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# MAIN RENDER FUNCTION
# ------------------------------------------------------------
def render_fulfillment_tab():
    st.header("📦 Fulfillment Agent — Post-Purchase Engagement")
    st.caption("Simulates fulfillment operations and personalized post-purchase emails.")

    # --- Metrics Section ---
    df = _ws_df("PostPurchase_Engagement_Log")
    df_templates = _ws_df("Fulfillment_Templates")
    total_orders = len(df)
    delivered = len(df[df["status"].str.upper() == "DELIVERED"]) if not df.empty else 0
    approved = len(df_templates[df_templates["status"].str.upper() == "APPROVED"]) if not df_templates.empty else 0
    sent = len(df_templates[df_templates["status"].str.upper() == "SENT"]) if not df_templates.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", total_orders)
    c2.metric("Delivered", delivered)
    c3.metric("Approved", approved)
    c4.metric("Emails Sent", sent)
    st.markdown("---")

    # --- Fulfillment Workflow Button ---
    st.markdown("#### Full Fulfillment Workflow")
    workflow_btn = st.button("▶️ Run Fulfillment Workflow (Delivered Orders Only)")
    if workflow_btn:
        # (Optional) Generate mock orders if none
        if df.empty:
            new_orders = _generate_mock_orders(10)
            _append_rows("PostPurchase_Engagement_Log", new_orders.values.tolist())
            st.info("Generated 10 mock orders.")
            df = _ws_df("PostPurchase_Engagement_Log")
        # Generate emails for all delivered (not yet queued)
        delivered_orders = df[df["status"].str.upper() == "DELIVERED"]
        already_queued = set(df_templates["order_id"]) if not df_templates.empty else set()
        to_generate = delivered_orders[~delivered_orders["order_id"].isin(already_queued)]
        rows = []
        video_url = "https://www.youtube.com/watch?v=EaKA3Wc-49s"
        now = datetime.now()
        for _, row in to_generate.iterrows():
            subject, message = _generate_postpurchase_email(
                row["first_name"], row["products"], video_url
            )
            rows.append([
                now.strftime("%Y-%m-%d %H:%M:%S"),
                row["order_id"], row["email"], row["first_name"],
                subject, message, "QUEUED", "", ""
            ])
        if rows:
            _append_rows("Fulfillment_Templates", rows)
            st.success(f"Generated {len(rows)} post-purchase emails for delivered orders.")
        else:
            st.info("No new delivered orders to generate emails for.")
        st.rerun()

    # --- Generate Mock Orders Button ---
    if st.button("🛍️ Generate Mock Orders"):
        new_orders = _generate_mock_orders(10)
        _append_rows("PostPurchase_Engagement_Log", new_orders.values.tolist())
        st.success("✅ 10 mock Shopify orders added to PostPurchase_Engagement_Log.")
        st.rerun()

    # --- Generate Emails Button ---
    if st.button("📬 Generate Post-Purchase Emails (Delivered Orders Only)"):
        delivered_orders = df[df["status"].str.upper() == "DELIVERED"]
        already_queued = set(df_templates["order_id"]) if not df_templates.empty else set()
        to_generate = delivered_orders[~delivered_orders["order_id"].isin(already_queued)]
        if to_generate.empty:
            st.info("No new delivered orders to generate emails for.")
        else:
            st.info(f"Generating {len(to_generate)} post-purchase emails for delivered orders...")
            video_url = "https://www.youtube.com/watch?v=EaKA3Wc-49s"
            rows = []
            now = datetime.now()
            for _, row in to_generate.iterrows():
                subject, message = _generate_postpurchase_email(
                    row["first_name"], row["products"], video_url
                )
                rows.append([
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    row["order_id"], row["email"], row["first_name"],
                    subject, message, "QUEUED", "", ""
                ])
            _append_rows("Fulfillment_Templates", rows)
            st.success(f"Generated {len(rows)} post-purchase emails for delivered orders.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Order Log Overview")
    st.dataframe(df)
    st.markdown("---")

    # --- Human-in-the-Loop Review Section ---
    st.subheader("🧠 Human-in-the-Loop Review")
    st.info("Review, edit, and approve/reject personalized post-purchase emails before sending.")
    df_templates = _ws_df("Fulfillment_Templates")
    review_df = df_templates[df_templates["status"].str.upper() == "QUEUED"] if not df_templates.empty else pd.DataFrame()
    if not review_df.empty:
        for idx, row in review_df.iterrows():
            with st.expander(f"Order {row['order_id']} — {row['first_name']} ({row['email']})"):
                subject = st.text_input(
                    f"Subject (Order {row['order_id']})", row["subject"], key=f"subject_{row['order_id']}"
                )
                message = st.text_area(
                    f"Message (Order {row['order_id']})", row["message"], key=f"msg_{row['order_id']}"
                )
                colA, colB = st.columns(2)
                approved = colA.button(
                    "✅ Approve", key=f"approve_{row['order_id']}"
                )
                rejected = colB.button(
                    "❌ Reject", key=f"reject_{row['order_id']}"
                )
                if approved or rejected:
                    ws = _get_ws("Fulfillment_Templates")
                    ws_all = ws.get_all_values()
                    headers = [h.strip().lower() for h in ws_all[0]]
                    oid_idx = headers.index("order_id")
                    subj_idx = headers.index("subject")
                    msg_idx = headers.index("message")
                    status_idx = headers.index("status")
                    reviewed_by_idx = headers.index("reviewed_by")
                    # Find row to update
                    for i, row_ws in enumerate(ws_all[1:], start=2):
                        if len(row_ws) > oid_idx and row_ws[oid_idx] == row["order_id"]:
                            ws.update_cell(i, subj_idx + 1, subject)
                            ws.update_cell(i, msg_idx + 1, message)
                            ws.update_cell(i, status_idx + 1, "APPROVED" if approved else "REJECTED")
                            ws.update_cell(i, reviewed_by_idx + 1, os.getenv("USER", "HITL"))
                            break
                    st.success("Email template updated.")
                    st.rerun()
    else:
        st.info("No queued emails for review.")

    # --- Brewing Tutorial Section (unchanged) ---
    st.markdown("---")
    st.subheader("🎥 Brewing Tutorial")
    st.markdown("Watch the Two Peaks founders' step-by-step chai brewing tutorial below:")
    video_url = "https://www.youtube.com/embed/EaKA3Wc-49s"
    fallback_url = "https://www.youtube.com/watch?v=EaKA3Wc-49s"
    st.markdown(
        f"""
<iframe width="560" height="315" src="{video_url}" 
frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
allowfullscreen></iframe>
<br>
<small>If the video doesn't load, <a href="{fallback_url}" target="_blank">click here to watch on YouTube</a>.</small>
""",
        unsafe_allow_html=True,
    )