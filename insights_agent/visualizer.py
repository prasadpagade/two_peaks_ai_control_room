"""
Two Peaks Chai Co. — Visualizer
Final polished version:
- Clean KPI row, Insights, and Campaign Console
- Static interactivity (st.toast feedback)
- Auto-generated subheaders and badges
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# --- Chai Theme ---
CHAI_CREAM = "#f8f5ed"
CHAI_GOLD  = "#b99746"
CHAI_OLIVE = "#5A7D42"
CHAI_DARK  = "#1a1a1a"


# ----------------------- KPI Summary -----------------------
def render_kpi_summary():
    """Static performance snapshot row"""
    st.markdown(f"<h3 style='color:{CHAI_DARK};margin-bottom:0;'>📈 Performance Snapshot</h3>", unsafe_allow_html=True)

    metrics = [
        ("1,284", "Total Orders"),
        ("1,220", "Total Shipped"),
        ("64", "Total Returns"),
        ("$58.45", "Avg Order Value"),
    ]

    cols = st.columns(len(metrics), gap="large")
    for (val, label), col in zip(metrics, cols):
        with col:
            st.markdown(
                f"""
                <div style="background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};
                            border-radius:12px;padding:16px;text-align:center;
                            box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                    <div style="font-size:1.2em;color:{CHAI_OLIVE};font-weight:bold;">{val}</div>
                    <div style="color:{CHAI_DARK};font-size:0.9em;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ----------------------- Segment Overview -----------------------
def generate_segment_overview() -> px.bar:
    """Static customer segment visualization"""
    data = pd.DataFrame({
        "Segment": ["Loyalist", "Engaged Customer", "High-Value Newcomer", "At-Risk Repeat", "First-time Buyer"],
        "Count": [6, 5, 4, 3, 2],
    })
    fig = px.bar(
        data,
        x="Segment",
        y="Count",
        color="Segment",
        text="Count",
        color_discrete_sequence=["#B99746", "#A9B18F", "#6D8B74", "#5A7D42", "#D4AF37"],
        title="Customer Segments Overview",
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        plot_bgcolor=CHAI_CREAM,
        paper_bgcolor=CHAI_CREAM,
        font=dict(family="Georgia", color=CHAI_OLIVE, size=15),
        xaxis_title="Customer Segment",
        yaxis_title="Number of Customers",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        height=350,
    )
    return fig


def render_segment_details():
    """Graph + mini insights table"""
    st.markdown(f"<h3 style='color:{CHAI_DARK};margin-bottom:0;'>📦 Segment Control Room</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1], gap="large")

    seg_data = pd.DataFrame({
        "Segment": ["Loyalist", "Engaged Customer", "High-Value Newcomer", "At-Risk Repeat", "First-time Buyer"],
        "Customers": ["Asha, Rohan", "Sita, Dev", "Arjun, Anita", "Raj", "Maya"],
        "Insights": [
            "High repeat rate, frequent reorders",
            "Engaged via newsletter campaigns",
            "New but premium order value",
            "Risk of churn, declining frequency",
            "Low spend, new acquisition"
        ]
    })

    with col1:
        st.plotly_chart(generate_segment_overview(), use_container_width=True)
    with col2:
        st.dataframe(seg_data, use_container_width=True, hide_index=True)


# ----------------------- Insights Section -----------------------
def render_insights_section():
    """Daily AI-generated summary"""
    st.markdown("### 🧠 Insights & Recommendations")
    st.caption("Auto-generated daily by the Customer Intelligence Agent. Next update: Tomorrow 9 AM.")

    # Insight badges
    st.markdown(f"""
    <div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;'>
      <span style='background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};padding:6px 12px;
                  border-radius:8px;color:{CHAI_OLIVE};'>💚 20 High-Value Customers Identified</span>
      <span style='background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};padding:6px 12px;
                  border-radius:8px;color:{CHAI_OLIVE};'>📈 12% Growth Potential</span>
      <span style='background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};padding:6px 12px;
                  border-radius:8px;color:{CHAI_OLIVE};'>🛒 Recommended Action: Launch Green Chai Week</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style='color:{CHAI_DARK};font-size:1.05em;line-height:1.6;'>
    The Customer Intelligence Agent has analyzed engagement data and identified clear opportunities for growth. 
    <b>Loyal customers</b> continue to drive recurring orders, while <b>high-value newcomers</b> offer potential for upselling. 
    <b>At-risk repeat buyers</b> should be targeted with retention offers and loyalty discounts to reduce churn. 
    These insights refresh every morning at <b>9 AM</b> to align with campaign recommendations below.
    </p>
    """, unsafe_allow_html=True)


# ----------------------- Campaign Console -----------------------
def render_campaign_card(title, roi):
    """Single campaign card with interactive buttons"""
    key_base = title.replace(" ", "_").lower()

    st.markdown(f"""
        <div style="
            background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};
            border-radius:12px;padding:16px;margin-bottom:16px;">
            <i style='color:{CHAI_OLIVE};'>🤖 Agent recommends this campaign</i><br><br>
            <b style='color:{CHAI_OLIVE};font-size:1.05em;'>{title}</b><br>
            <span style='color:{CHAI_DARK};font-size:0.95em;'><i>Estimated ROI: {roi}</i></span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve & Launch", key=f"{key_base}_approve"):
            st.session_state[key_base] = "approved"
            st.toast(f"🚀 '{title}' approved — launching by 4 PM today!")

    with col2:
        if st.button("🕒 Schedule for Later", key=f"{key_base}_schedule"):
            st.session_state[key_base] = "scheduled"
            st.toast(f"📅 '{title}' scheduled for tomorrow 10 AM.")

    with col3:
        if st.button("❌ Reject", key=f"{key_base}_reject"):
            st.session_state[key_base] = "rejected"
            st.toast(f"🗑 '{title}' discarded.")


# ----------------------- Campaign Console -----------------------
def render_campaign_console():
    """Static campaign list linked with insights and interactive actions"""
    st.markdown(
        f"<h3 style='color:{CHAI_DARK};margin-bottom:0;'>🎯 Campaign Console</h3>"
        f"<p style='color:{CHAI_DARK};font-style:italic;font-size:0.9em;'>"
        f"Auto-generated daily by Customer Intelligence Agent — next update: tomorrow 9 AM.</p>",
        unsafe_allow_html=True,
    )

    # --- Define campaigns (first one linked to insights) ---
    if "active_campaigns" not in st.session_state:
        st.session_state.active_campaigns = [
            (
                "💚 Retention Boost for At-Risk Customers",
                "Target at-risk buyers with loyalty offers and personalized chai bundles to reduce churn.",
                "Estimated ROI: 2.3×"
            ),
            (
                "🧘‍♀️ Yoga Studio Collab + Sampler Codes",
                "Community co-branding effort to reach wellness audiences with chai samplers.",
                "Estimated ROI: 1.7×"
            ),
            (
                "📸 IG UGC Contest: #TwoPeaksChai Moments",
                "Drive engagement via user-generated posts and stories featuring Two Peaks blends.",
                "Estimated ROI: 1.6×"
            )
        ]

    card_style = (
        f"background:{CHAI_CREAM};border:1px solid {CHAI_GOLD};border-radius:12px;"
        f"padding:16px 18px;margin-bottom:16px;"
        f"box-shadow:0 2px 6px rgba(0,0,0,0.05);"
    )

    # --- Render campaigns dynamically ---
    for i, (title, desc, roi) in enumerate(st.session_state.active_campaigns.copy()):
        with st.container():
            # Recommendation header only for the first one
            if i == 0:
                st.markdown(
                    f"""
                    <div style="{card_style}">
                        <div style="color:{CHAI_OLIVE};font-style:italic;font-size:0.95em;margin-bottom:6px;">
                            *Agent recommends this campaign based on latest customer insights:*
                        </div>
                        <div style="color:{CHAI_OLIVE};font-weight:700;font-size:1.1em;margin-top:2px;">
                            {title}
                        </div>
                        <div style="color:{CHAI_DARK};font-size:0.95em;margin-top:6px;margin-bottom:6px;">
                            {desc}
                        </div>
                        <div style="color:{CHAI_DARK};font-size:0.9em;margin-bottom:12px;">
                            <i>{roi}</i>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="{card_style}">
                        <div style="color:{CHAI_OLIVE};font-weight:700;font-size:1.1em;margin-top:2px;">
                            {title}
                        </div>
                        <div style="color:{CHAI_DARK};font-size:0.95em;margin-top:6px;margin-bottom:6px;">
                            {desc}
                        </div>
                        <div style="color:{CHAI_DARK};font-size:0.9em;margin-bottom:12px;">
                            <i>{roi}</i>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # --- Action Buttons ---
            a, b, c = st.columns([1, 1, 1])
            with a:
                if st.button(f"✅ Approve & Launch ({i})"):
                    st.toast(f"🚀 '{title}' approved and will launch by 4 PM today!")
            with b:
                if st.button(f"🕒 Schedule for Later ({i})"):
                    st.toast(f"🗓️ '{title}' scheduled for tomorrow morning.")
            with c:
                if st.button(f"❌ Reject ({i})"):
                    st.session_state.active_campaigns.pop(i)
                    st.toast(f"🗑️ '{title}' was removed from the queue.")
                    st.rerun()