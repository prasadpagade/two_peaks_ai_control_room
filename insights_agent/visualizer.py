"""
Chai-Themed Visualization + Interactive Console for Two Peaks Chai Co.
- Olive/Gold theme
- Plotly charts
- Segment side-panel with customer details
- Campaign console with 3s auto-rotation (no autorefresh)
- Lightweight KPI widgets
"""

import time
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHAI_CREAM = "#f8f5ed"
CHAI_GOLD  = "#b99746"
CHAI_OLIVE = "#5A7D42"
CHAI_DARK  = "#46351d"

try:
    from streamlit_plotly_events import plotly_events
    _HAVE_PLOTLY_EVENTS = True
except Exception:
    _HAVE_PLOTLY_EVENTS = False

try:
    import streamlit as st
except ImportError:
    st = None  # allow import without Streamlit


# ----------------------- Data Utilities -----------------------
def merge_segments_extra_fields(seg_df: pd.DataFrame, seg_sheet_df: pd.DataFrame) -> pd.DataFrame:
    """Merge CLV / Notes / Tags from a sheet if present (by Email)."""
    if seg_sheet_df is None or seg_sheet_df.empty:
        return seg_df
    left = seg_df.copy()
    right = seg_sheet_df.rename(columns=lambda c: c.strip())
    if "Email" in left.columns and "Email" in right.columns:
        keep = [c for c in ["Email", "CLV", "Notes", "Tags"] if c in right.columns]
        if keep:
            return left.merge(right[keep], on="Email", how="left")
    return seg_df


# ----------------------- KPI Widgets -----------------------
def render_kpi_widgets(df: pd.DataFrame, seg_df: pd.DataFrame):
    """Small KPI strip; safe & fast."""
    if st is None:
        return
    total_customers = seg_df["Email"].nunique() if "Email" in seg_df.columns else len(seg_df)
    loyal = int((seg_df.get("segment", pd.Series(dtype=str)) == "Loyalist").sum())
    aov = float(seg_df.get("avg_order_value", pd.Series([0.0])).mean() or 0.0)
    recent_new = int((seg_df.get("segment", pd.Series(dtype=str)) == "High-Value Newcomer").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Customers", f"{total_customers}")
    with c2: st.metric("Loyalists", f"{loyal}")
    with c3: st.metric("Avg AOV", f"${aov:,.0f}")
    with c4: st.metric("New (HVN)", f"{recent_new}")


# ----------------------- Charts -----------------------
def generate_revenue_plot(df: pd.DataFrame) -> go.Figure:
    """
    Olive-themed revenue line; robust when limited data present.
    If only one month available, it still renders a single point.
    """
    if "Created at" in df.columns and "Total" in df.columns:
        tmp = df.copy()
        tmp["month"] = pd.to_datetime(tmp["Created at"], errors="coerce").dt.to_period("M").astype(str)
        monthly = tmp.groupby("month", sort=False)["Total"].sum().reset_index()
    else:
        monthly = pd.DataFrame({"month":["Jan","Feb","Mar","Apr","May","Jun"], "Total":[9000,10500,11900,13300,14700,16100]})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["Total"],
        mode="lines+markers",
        line=dict(color=CHAI_GOLD, width=3),
        marker=dict(size=10, color=CHAI_OLIVE, line=dict(width=2, color=CHAI_GOLD)),
        hovertemplate="<b>%{x}</b><br>Revenue: <b>$%{y:,.0f}</b><extra></extra>",
        name="Monthly Revenue"
    ))
    fig.update_layout(
        title="Monthly Revenue - Two Peaks Chai Co.",
        plot_bgcolor=CHAI_CREAM, paper_bgcolor=CHAI_CREAM,
        font=dict(family="Georgia", color=CHAI_OLIVE, size=16),
        xaxis=dict(title="Month", gridcolor="#eae2c8"),
        yaxis=dict(title="Revenue ($)", gridcolor="#eae2c8"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def generate_segment_overview(segment_df: pd.DataFrame) -> go.Figure:
    """Olive-themed bar chart of segments (counts)."""
    if "segment" not in segment_df.columns:
        raise ValueError("DataFrame must contain a 'segment' column.")
    counts = segment_df["segment"].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    fig = px.bar(
        counts, x="segment", y="count", color="segment",
        color_discrete_sequence=["#C0B283", "#A9B18F", "#6D8B74", "#5A7D42", "#D4AF37", "#8FAF9A"],
        text="count",
        hover_data={"segment": True, "count": True},
        title="Customer Segments Overview",
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        plot_bgcolor=CHAI_CREAM, paper_bgcolor=CHAI_CREAM,
        font=dict(family="Georgia", color=CHAI_OLIVE, size=15),
        xaxis_title="Customer Segment", yaxis_title="Number of Customers",
        showlegend=False, margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


# ----------------------- Segment Interactions -----------------------
def segment_chart_interactions(fig: go.Figure):
    """
    Return selected segment on click if streamlit-plotly-events is installed.
    Fallback to a selectbox so UX always works.
    """
    if st is None:
        return None
    selected = None
    if _HAVE_PLOTLY_EVENTS:
        events = plotly_events(fig, click_event=True, hover_event=False, select_event=False)
        if events:
            selected = events[0].get("x")
    else:
        with st.expander("🔎 Explore a segment", expanded=False):
            cats = []
            for tr in fig.data:
                if hasattr(tr, "x"):
                    for v in tr.x:
                        if v not in cats:
                            cats.append(v)
            selected = st.selectbox("Open details for segment:", cats) if cats else None
    return selected


def render_segment_modal(selected_segment: str, seg_df: pd.DataFrame):
    """
    SIDE-PANEL (not overlay): shows customers for the selected segment
    with insight_summary and optional CLV/Notes/Tags.
    """
    if st is None or not selected_segment:
        return
    subset = seg_df[seg_df["segment"] == selected_segment].copy()
    if subset.empty:
        return

    st.markdown(f"#### Segment: {selected_segment}")
    box = st.container(border=True)
    with box:
        for _, r in subset.iterrows():
            full_name = " ".join([str(r.get("Customer First Name","")).strip(), str(r.get("Customer Last Name","")).strip()]).strip()
            email = r.get("Email", "")
            insight = r.get("insight_summary", "")
            clv = r.get("CLV", "")
            notes = r.get("Notes", "")
            tags = r.get("Tags", "")
            st.markdown(
                f"<div style='padding:6px 0;border-bottom:1px dashed {CHAI_GOLD}'>"
                f"<b style='color:{CHAI_OLIVE}'>{full_name}</b> • <span>{email}</span><br>"
                f"{insight}<br>"
                f"<span style='color:{CHAI_DARK};font-size:0.92em'>"
                f"{('CLV: ' + str(clv) + ' • ') if clv != '' else ''}"
                f"{('Notes: ' + str(notes) + ' • ') if notes != '' else ''}"
                f"{('Tags: ' + str(tags)) if tags != '' else ''}"
                f"</span></div>",
                unsafe_allow_html=True
            )


# ----------------------- Campaign Console -----------------------
def _campaign_pool():
    return [
        ("🌿 Green Chai Week — eco-pack discounts", 2.1),
        ("🧘‍♀️ Yoga studio collab + sampler codes", 1.7),
        ("📧 ‘Warm Up Your Day’ email re-activation", 1.5),
        ("🎁 VIP surprise sampler for top 5% AOV", 2.4),
        ("📸 IG UGC contest: #TwoPeaksChai moments", 1.6),
        ("🤝 Local bakery bundle: Chai + Pastry", 1.8),
    ]


def render_campaign_console(rotation_seconds: int = 3):
    """
    Rotating suggestion card with Pause + ROI + olive styling.
    Uses session_state and st.rerun() (Streamlit ≥1.31).
    """
    if st is None:
        return

    st.markdown(
        f"""
        <style>
        .tp-card {{
            background:{CHAI_CREAM}; border:1px solid {CHAI_GOLD}; border-radius:12px;
            padding:14px 16px; margin-bottom:14px;
        }}
        .tp-flash {{ animation: flash 1s linear infinite; }}
        @keyframes flash {{
            0% {{ background-color: {CHAI_CREAM}; }}
            50% {{ background-color: #fff8e6; }}
            100% {{ background-color: {CHAI_CREAM}; }}
        }}
        .tp-olive {{ color:{CHAI_OLIVE}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "tp_campaigns" not in st.session_state:
        st.session_state.tp_campaigns = _campaign_pool()
    if "tp_idx" not in st.session_state:
        st.session_state.tp_idx = 0
    if "tp_pause" not in st.session_state:
        st.session_state.tp_pause = False
    if "tp_last" not in st.session_state:
        st.session_state.tp_last = time.time()

    left, right = st.columns([1,1])
    with left:
        st.checkbox("Pause rotation", value=st.session_state.tp_pause, key="tp_pause")
    with right:
        st.caption(f"Autonomous Mode  {'🟢' if not st.session_state.tp_pause else '⚪️'}")

    if not st.session_state.tp_pause and (time.time() - st.session_state.tp_last >= rotation_seconds):
        st.session_state.tp_idx = (st.session_state.tp_idx + 1) % len(st.session_state.tp_campaigns)
        st.session_state.tp_last = time.time()
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            try:
                st.experimental_rerun()
            except Exception:
                pass

    title, roi = st.session_state.tp_campaigns[st.session_state.tp_idx]
    st.markdown(
        f"<div class='tp-card tp-flash'><div class='tp-olive'><b>Suggested Campaign:</b></div>"
        f"<div style='font-size:1.15em'>{title}</div>"
        f"<div style='margin-top:6px' class='tp-olive'><i>Estimated ROI:</i> <b>{roi:.1f}×</b></div></div>",
        unsafe_allow_html=True,
    )

    a, b, c = st.columns([1, 1, 1])
    with a:
        if st.button("✅ Approve & Launch"):
            st.success("Campaign approved! Launching soon…")
    with b:
        if st.button("🕒 Schedule for Later"):
            st.info("Added to scheduled campaigns.")
    with c:
        auto = st.toggle("🤖 Autonomous Mode", value=not st.session_state.tp_pause)
        st.session_state.tp_pause = not auto