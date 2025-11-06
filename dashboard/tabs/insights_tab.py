"""
Two Peaks Chai Co. — Customer Intelligence Agent (Final Polished Version)
Autonomously analyzes customer patterns, generates insights, and launches campaigns.
"""

import time
import random
import streamlit as st
from insights_agent.visualizer import (
    render_kpi_summary,
    render_segment_details,
    render_insights_section,
    render_campaign_console,
)

# --- Theme ---
CHAI_CREAM = "#f8f5ed"
CHAI_GOLD  = "#b99746"
CHAI_OLIVE = "#5A7D42"
CHAI_DARK  = "#1a1a1a"


# ----------------------- Heartbeat Indicator -----------------------
# ----------------------- Heartbeat Indicator -----------------------
def render_agent_heartbeat():
    """Simulates AI agent live system status with soft brand styling"""
    if "ai_status" not in st.session_state:
        st.session_state.ai_status = "Active"

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### 🤖 AI System Status")

    with col2:
        if st.button("🔁 Refresh Insights", use_container_width=True):
            st.session_state.ai_status = random.choice(["Active", "Analyzing...", "Paused"])
            st.toast("🔄 Agent rechecking customer data streams...")

    # --- Status mapping ---
    status = st.session_state.ai_status
    if status == "Active":
        emoji, color, bg = "🟢", CHAI_OLIVE, "#e6f4ea"
    elif status == "Analyzing...":
        emoji, color, bg = "🟡", "#d4a017", "#fff8e1"
    else:  # Paused
        emoji, color, bg = "⏸️", CHAI_GOLD, "#fcf7e6"

    # --- Render status pill ---
    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;gap:8px;
            background:{bg};
            border:1px solid {CHAI_GOLD};
            border-radius:10px;
            padding:6px 14px;
            width:fit-content;
            margin-top:-10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.05);
        ">
            <span style="font-size:1.1em">{emoji}</span>
            <b style="color:{color};font-size:1em">{status}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Auto pulse every 10s (safe rerun) ---
    if "last_pulse" not in st.session_state:
        st.session_state.last_pulse = time.time()
    elif time.time() - st.session_state.last_pulse > 10:
        st.session_state.ai_status = random.choice(["Active", "Analyzing..."])
        st.session_state.last_pulse = time.time()
        try:
            st.rerun()
        except AttributeError:
            pass  # For older Streamlit builds


# ----------------------- Main Page -----------------------
def render_insights_tab():
    """Unified AI Control Tab"""
    st.header("☕ Customer Intelligence Agent")
    st.caption(
        "_Autonomously analyzing customer patterns, brewing insights, and launching campaigns — powered by the Customer Intelligence Agent._"
    )
    render_agent_heartbeat()
    st.markdown("---")

    # KPI summary
    render_kpi_summary()
    st.markdown("")

    # Segment + Insights + Campaign Console
    render_segment_details()
    st.markdown("")
    render_insights_section()
    st.markdown("")
    render_campaign_console()

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <p style='text-align:center;color:{CHAI_DARK};margin-top:25px;font-size:0.9em;'>
        © 2025 Two Peaks Chai Co. | AI Agents Operational 🟢 | Last Sync: Today 9:00 AM
        </p>
        """,
        unsafe_allow_html=True,
    )


# ----------------------- Run Standalone -----------------------
if __name__ == "__main__":
    st.set_page_config(page_title="Two Peaks AI Control Room", layout="wide", page_icon="☕")
    render_insights_tab()