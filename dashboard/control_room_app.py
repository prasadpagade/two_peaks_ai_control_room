# dashboard/control_room_app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Tabs & Agents
from tabs.insights_tab import render_insights_tab
from tabs import finance_tab
from tabs.finance_chat import finance_chat_interface

# Load environment variables
load_dotenv()

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
# GLOBAL THEME (Unified Palette)
# -----------------------------------
st.markdown("""
<style>
/* Root layout */
[data-testid="stAppViewContainer"] {
    background-color: #f6f3eb; /* light chai beige */
    color: #1e1c19;
    font-family: 'Poppins', sans-serif;
    padding: 1rem 3rem 3rem 3rem;
    overflow: visible !important;
}

/* Sidebar */
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

/* Buttons */
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

/* Titles & Headers */
h1, h2, h3 {
    color: #2e4a26;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

/* Metrics */
.metric-card {
    background: #ffffff;
    border: 1px solid #e1dccf;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    color: #2e4a26;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    transition: 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 10px rgba(0,0,0,0.12);
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

/* Section lines */
hr {
    border: 0;
    height: 1px;
    background: #d2c8b5;
    margin: 1.5rem 0;
}

/* Streamlit tweaks */
section.main > div {
    padding-top: 0rem;
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

elif choice == "📈 Marketing Agent":
    st.header("📈 Marketing & Lead Qualification Agent")
    st.write("Captures Instagram engagement → qualifies leads → generates outreach templates.")
    c1, c2, c3 = st.columns(3)
    for label, value in [("Engagements","245"),("Qualified Leads","38"),("Emails Generated","22")]:
        with (c1 if label=="Engagements" else c2 if label=="Qualified Leads" else c3):
            st.markdown(f"<div class='metric-card'><h3>{label}</h3><span>{value}</span></div>", unsafe_allow_html=True)
    if st.button("▶️ Run Marketing Workflow"):
        os.system("python marketing_agent/add_fake_engagement.py && python marketing_agent/lead_scoring.py")
        st.success("Marketing workflow executed successfully ✅")

elif choice == "📦 Fulfillment Agent":
    st.header("📦 Post-Purchase Engagement Agent")
    st.write("Enhances post-purchase experience with gratitude messages and brewing tips.")
    if st.button("📬 Trigger Shopify Webhook"):
        os.system("curl -X POST https://prasadpagade.app.n8n.cloud/shopify/order-create")
        st.success("Post-purchase engagement workflow triggered ✅")

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
    st.header("💬 Support Agent (RAG-Powered Concierge)")
    st.write("Your AI assistant trained on product FAQs, brewing rituals, and order support.")

    # Gradio app URL (must be running in background)
    gradio_url = "http://127.0.0.1:7860"

    st.markdown(
        f"""
        <div style="border: 2px solid #b99746; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
            <iframe 
                src="{gradio_url}" 
                width="100%" 
                height="750" 
                style="border: none;"
                allow="microphone; clipboard-write;"
            ></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("If the assistant doesn’t appear, make sure `rag_support_bot.py` is running in another terminal window.")

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown(
    "<br><center><small>© 2025 Two Peaks Chai Co. • Built with ❤️ & AI</small></center>",
    unsafe_allow_html=True
)