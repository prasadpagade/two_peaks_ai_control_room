import sys, os
import streamlit as st
import pandas as pd
from tabs.finance_chat import finance_chat_interface

# --- Make sure Python can find finance_agent package ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from finance_agent.generate_financial_report import generate_financial_metrics
from finance_agent.summarize_financials import summarize_financials

def show():  
    st.markdown("<h2 style='color:#3A4D39;'>💼 Finance & Performance Agent</h2>", unsafe_allow_html=True)

    # ---- Load Data ----
    df = pd.read_csv("finance_agent/mock_financial_data.csv")
    metrics = generate_financial_metrics(df)

    # ---- KPI Cards ----
    st.markdown("""
    <style>
    .metric-container {
        background-color: #1b1b1b;
        border-radius: 16px;
        padding: 20px;
        color: #e5c17d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"<div class='metric-container'><b>Revenue (7-Day)</b><br>${metrics['Total Revenue']:.0f}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='metric-container'><b>Orders</b><br>{int(metrics['Total Orders'])}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='metric-container'><b>Avg ROAS</b><br>{metrics['Avg ROAS']:.2f}×</div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<div class='metric-container'><b>Profit Margin</b><br>{metrics['Avg Profit Margin']:.1f}%</div>", unsafe_allow_html=True)

    st.divider()

    # ---- Revenue Trend ----
    st.subheader("📈 Daily Revenue Trend")
    st.line_chart(df, x="date", y="revenue")

    # ---- AI Summary ----
    st.subheader("🧠 Financial Insight Summary")
    if st.button("▶ Generate Summary"):
        with st.spinner("Analyzing financial data..."):
            summary = summarize_financials(df)
            st.success("Insight Generated ✅")
            st.write(summary)

    # ---- Future Chat Section ----
    st.markdown("---")
    finance_chat_interface(df)