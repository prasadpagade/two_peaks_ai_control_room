# --- Chai Theme ---
CHAI_CREAM = "#f8f5ed"
CHAI_OLIVE = "#5A7D42"
CHAI_GOLD  = "#b99746"
CHAI_DARK  = "#46351d"

import re
import streamlit as st

# Data + AI
from insights_agent.segment_customers import load_customer_data, segment_customers
from insights_agent.summarize_insights import generate_insight_summary, load_segment_data

# Visuals + Console (all names match visualizer.py)
from insights_agent.visualizer import (
    generate_revenue_plot,
    generate_segment_overview,
    render_campaign_console,
    render_segment_modal,
    merge_segments_extra_fields,
    segment_chart_interactions,
    render_kpi_widgets,
)

# ---------------- Helpers ----------------
def _clean_and_highlight_olive(text: str) -> str:
    """Strip stray HTML tags and highlight numbers/$/% in olive."""
    if not text:
        return ""
    # remove broken/embedded spans/divs
    text = re.sub(r"</?(span|div)[^>]*>", "", text)
    # highlight numbers, $, %
    def repl(m):
        return f"<b style='color:{CHAI_OLIVE}'>{m.group(0)}</b>"
    return re.sub(r"(\$?\d[\d,]*(\.\d+)?%?)", repl, text)

def _key_takeaways(seg_df):
    if seg_df is None or seg_df.empty:
        return []
    total = len(seg_df)
    loyal = int((seg_df["segment"] == "Loyalist").sum()) if "segment" in seg_df else 0
    hvn   = int((seg_df["segment"] == "High-Value Newcomer").sum()) if "segment" in seg_df else 0
    badges = [f"🧑‍🤝‍🧑 {total} customers profiled"]
    if loyal: badges.append(f"💚 {loyal} Loyalists")
    if hvn:   badges.append(f"🛒 {hvn} High-Value Newcomers")
    return badges

# ---------------- Main Tab ----------------
def render_insights_tab():
    st.header("☕ Customer Intelligence Agent")
    st.caption("Your friendly self-learning chai agent, always brewing up smart insights and growth ideas for your shop.")

    # Load base orders + derive segments
    df = load_customer_data()
    if df is None or df.empty:
        st.warning("⚠️ No customer data found — check your Google Sheet or the fallback.")
        return

    seg = segment_customers(df)

    # Merge optional extras (CLV / Notes / Tags) from Customer_Segments sheet
    try:
        extras = load_segment_data()  # may be empty
        seg = merge_segments_extra_fields(seg, extras)
    except Exception:
        pass

    # ===== Row 1: Metrics (left) | Insights (right) =====
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("📊 Customer Metrics Highlights")
        # KPI widgets only
        render_kpi_widgets(df, seg, olive=CHAI_OLIVE, gold=CHAI_GOLD, cream=CHAI_CREAM)
        st.caption("Key customer insights at a glance")

    with right:
        st.subheader("🧠 Insights & Recommendations")
        badges = _key_takeaways(seg)
        if badges:
            st.markdown(
                "<div style='display:flex;flex-wrap:wrap;gap:8px'>"
                + "".join(
                    [f"<span style='background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};color:{CHAI_OLIVE};padding:6px 10px;border-radius:12px'>{b}</span>"
                     for b in badges]
                )
                + "</div>",
                unsafe_allow_html=True,
            )
        try:
            report = generate_insight_summary(seg)
            report = _clean_and_highlight_olive(report)
            st.markdown(f"<div style='line-height:1.6;color:{CHAI_DARK}'>{report}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error generating insight summary: {e}")

    st.markdown("---")

    # ===== Row 2: Segment Control (left) | Segment Details (right) =====
    s_left, s_right = st.columns([1, 1], gap="large")

    with s_left:
        st.subheader("📦 Segment Control Room")
        try:
            seg_fig = generate_segment_overview(seg)  # olive styling inside
            selected_segment = segment_chart_interactions(seg_fig)  # click/selector
            st.plotly_chart(seg_fig, use_container_width=True)
        except Exception as e:
            selected_segment = None
            st.error(f"❌ Error rendering segment chart: {e}")

    with s_right:
        # compact side panel (table/cards) instead of full-screen modal
        render_segment_sidepanel(seg, selected_segment, olive=CHAI_OLIVE, gold=CHAI_GOLD, cream=CHAI_CREAM, dark=CHAI_DARK)

    st.markdown("---")

    # ===== Row 3: Campaign Console =====
    st.subheader("🎯 Campaign Console")
    try:
        render_campaign_console(rotation_seconds=3, olive=CHAI_OLIVE, gold=CHAI_GOLD, cream=CHAI_CREAM)
    except Exception as e:
        st.error(f"❌ Error rendering campaign console: {e}")