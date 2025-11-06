# dashboard/control_room_app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv

import random
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Tabs & Agents
from tabs.insights_tab import render_insights_tab
from tabs import finance_tab
from tabs.finance_chat import finance_chat_interface
from tabs.marketing_tab import render_marketing_tab
from dashboard.tabs.render_human_review_tab import render_human_review_tab

# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"✅ Loaded environment from: {env_path}")
print("🔍 GOOGLE_SVC_JSON =", os.getenv("GOOGLE_SVC_JSON"))

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Two Peaks AI Control Room",
    page_icon="☕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# GOOGLE SHEETS HELPERS (shared)
# -----------------------------------
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")
SERVICE_ACCOUNT = os.getenv("GOOGLE_SVC_JSON", "service_account.json")

def _gs_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=scopes)
    return gspread.authorize(creds)

def _get_ws(title: str):
    """Return a worksheet by title, creating it with headers if needed."""
    headers_map = {
        "PostPurchase_Engagement_Log": ["timestamp","order_id","email","first_name","products","total","status","email_message_id"]
    }
    gc = _gs_client()
    ss = gc.open(SHEET_NAME)
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows="1000", cols=str(len(headers_map[title])+2))
        ws.append_row(headers_map[title])
    return ws

def _ws_df(title: str):
    ws = _get_ws(title)
    records = ws.get_all_records()
    return pd.DataFrame(records)

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
    # Build batch updates
    for i, row in enumerate(data[1:], start=2):  # 1-based with header row
        if len(row) > id_idx and row[id_idx] in set(order_ids):
            # Update status cell
            ws.update_cell(i, status_idx+1, new_status)
            count += 1
    return count

def _generate_mock_orders(n: int = 10) -> pd.DataFrame:
    """Return a DataFrame of realistic mock Shopify orders."""
    first_names = ["Asha", "Hannah", "Raj", "Sophia", "Ethan", "Maya", "Noah", "Leah", "Kiran", "Zoe"]
    products = [
        "Signature Masala Chai",
        "Rose Radiance Chai",
        "Golden Glow Chai",
        "Saffron Infused Chai",
        "Assam Breakfast Chai",
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

# -----------------------------------
# GLOBAL THEME (Unified Palette)
# -----------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f6f3eb;
    color: #1e1c19;
    font-family: 'Poppins', sans-serif;
    padding: 1rem 3rem 3rem 3rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2e4a26 0%, #3a5c30 100%);
    color: #f4f1e8;
    border-right: 2px solid #b99746;
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p {
    color: #f4f1e8 !important;
    font-weight: 500;
}
div.stButton > button {
    background: linear-gradient(90deg, #b99746, #e7c66b);
    color: #1c1b18;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    transition: all 0.25s ease;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #e7c66b, #b99746);
    transform: scale(1.03);
}
h1, h2, h3 {
    color: #2e4a26;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e1dccf;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    color: #2e4a26;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 10px rgba(0,0,0,0.12);
    border: 1px solid #b99746;
}
.metric-card h3 {
    color: #b99746;
    margin-bottom: 0.4rem;
    font-size: 1.1rem;
}
.metric-card span {
    font-size: 1.7rem;
    font-weight: 700;
}
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #e1dccf !important;
    border-radius: 14px !important;
    padding: 1.4rem !important;
    text-align: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border: 1px solid #b99746 !important;
}
[data-testid="stMetricLabel"] {
    color: #b99746 !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    text-align: center !important;
}
[data-testid="stMetricValue"] {
    color: #2e4a26 !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
    text-align: center !important;
}
hr {
    border: 0;
    height: 1px;
    background: #d2c8b5;
    margin: 1.5rem 0;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------
logo_path = "dashboard/assets/twopeaks_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)
else:
    st.sidebar.markdown("### ☕️ Two Peaks AI Control Room")

st.sidebar.markdown("---")

tabs = [
    "🏠 Dashboard Overview",
    "📈 Marketing Agent",
    "📦 Fulfillment Agent",
    "📊 Customer Insights Agent",
    "💵 Finance & Performance Agent",
    "💬 Finance Chat",
    "💬 Support Agent"
]
choice = st.sidebar.radio("Navigate Agents", tabs)
st.sidebar.markdown("---")
st.sidebar.caption("🌿 Blending Heritage with Automation")

# -----------------------------------
# MAIN DASHBOARD CONTENT
# -----------------------------------
st.title("🌿 Two Peaks AI Control Room")
st.markdown(
    "Welcome to your **AI-powered operations console**, where each agent works like a digital employee — automating growth, fulfillment, and insight for your brand."
)
st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------------
# TAB LOGIC
# -----------------------------------
if choice == "🏠 Dashboard Overview":
    st.header("🏠 Overview Dashboard")
    st.write("A unified summary of all AI agents' key metrics.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card'><h3>Active Agents</h3><span>5</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><h3>Automations Today</h3><span>14</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><h3>Avg Response Time</h3><span>2.1 s</span></div>", unsafe_allow_html=True)
    render_human_review_tab()

# -------------------------------------------------
# 📈 MARKETING AGENT (AUTONOMOUS VERSION)
# -------------------------------------------------
elif choice == "📈 Marketing Agent":
    render_marketing_tab()

# -------------------------------------------------
# 📦 FULFILLMENT AGENT
# -------------------------------------------------
elif choice == "📦 Fulfillment Agent":
    from tabs.fulfillment_tab import render_fulfillment_tab
    render_fulfillment_tab()

elif choice == "📊 Customer Insights Agent":
    render_insights_tab()

elif choice == "💵 Finance & Performance Agent":
    st.header("💵 Finance & Performance Agent")
    st.write("Analyzes sales and ad performance to produce dashboards.")
    finance_tab.show()

elif choice == "💬 Finance Chat":
    st.header("💬 Financial Insights Chat")
    st.caption("Ask questions about revenue, expenses, or trends in your business data.")
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr"],
        "Revenue": [12000, 15000, 17000, 16000],
        "Expenses": [8000, 9500, 10000, 9000],
    })
    finance_chat_interface(df)

elif choice == "💬 Support Agent":
    from tabs import support_tab
    support_tab.show()

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown(
    "<br><center><small>© 2025 Two Peaks Chai Co. • Built with ❤️ & AI</small></center>",
    unsafe_allow_html=True
)