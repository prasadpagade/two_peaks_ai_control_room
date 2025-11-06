import sys, os
import streamlit as st
import pandas as pd

# Plotly for richer charts
try:
    import plotly.express as px
except Exception:
    px = None  # Fallback to Streamlit native charts if Plotly isn't available

# --- Make sure Python can find finance_agent package ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Safe imports from finance_agent
try:
    from finance_agent.generate_financial_report import generate_financial_metrics
except Exception:
    generate_financial_metrics = None

try:
    from finance_agent.summarize_financials import summarize_financials
except Exception:
    summarize_financials = None

# Chat interface (already in your project)
from tabs.finance_chat import finance_chat_interface


# -------------------------------
# Helpers
# -------------------------------
def _safe_metric(metrics: dict, key: str, default=0):
    try:
        return metrics.get(key, default)
    except Exception:
        return default


def _format_currency(x):
    try:
        return f"${x:,.0f}"
    except Exception:
        return "-"


def _format_percent(x):
    try:
        return f"{x:.1f}%"
    except Exception:
        return "-"


# -------------------------------
# Main UI
# -------------------------------
def show():
    # ---- Load Data ----
    # Keep relative path so it works when app is launched from project root
    data_path = os.path.join(PROJECT_ROOT, "finance_agent", "financial_data.csv")
    if not os.path.exists(data_path):
        st.error("Missing data file: finance_agent/financial_data.csv")
        return

    try:
        df = pd.read_csv(data_path)
       # st.success(f"✅ Loaded {len(df)} rows from {data_path}")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return

    # st.write("📂 Loaded data from:", data_path)
    # st.write("✅ Rows loaded:", len(df))
    # st.write(df.head())
    # st.write("Current working directory:", os.getcwd())
    # st.dataframe(df.head(10))

    # Normalize numeric columns
    numeric_cols = ["revenue", "cogs", "ads", "fulfillment", "shipping", "overhead", "profit_margin"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Adaptive filter: Show only recent 60 days of data, fallback to all if none found
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    if not df.empty:
        cutoff_date = df["date"].max() - pd.Timedelta(days=60)
        df = df[df["date"] >= cutoff_date]
    if df.empty:
        st.warning("⚠️ No recent financial data found (last 60 days). Showing all available data instead.")
        df = pd.read_csv(data_path)

    # ---- Compute Metrics (defensive) ----
    metrics = {}
    if generate_financial_metrics:
        try:
            metrics = generate_financial_metrics(df) or {}
        except Exception as e:
            st.warning(f"Metric generation error: {e}")
            metrics = {}
    if not metrics:
        st.info("No computed metrics available — displaying default placeholders.")

    # Fallbacks if your generator hasn't filled them
    total_revenue = _safe_metric(metrics, "Total Revenue", default=float(df.get("revenue", pd.Series([0])).sum()))
    total_orders = int(_safe_metric(metrics, "Total Orders", default=int(df.get("orders", pd.Series([0])).sum())))
    avg_roas = float(_safe_metric(metrics, "Avg ROAS", default=float(df.get("roas", pd.Series([0])).replace([float('inf')], 0).mean() or 0)))
    avg_margin = float(_safe_metric(metrics, "Avg Profit Margin", default=float(df.get("profit_margin", pd.Series([0])).mean() * 100 if "profit_margin" in df.columns else 0)))

    # ---- KPI Cards (Chai theme) ----
    # -----------------------------
# TEMPORARY HARD-CODED METRICS
# -----------------------------
    # st.markdown("<h2 style='color:#3A4D39;'>💼 Finance & Performance Agent</h2>", unsafe_allow_html=True)
    # st.caption("Analyzes sales and ad performance to produce dashboards.")

    # ✅ Try loading real metrics from CSV — fallback to demo values if it fails
    try:
        metrics = generate_financial_metrics(df)
        st.success("✅ Loaded live financial metrics from CSV.")
    except Exception as e:
        st.warning(f"⚠️ Could not compute metrics dynamically: {e}. Using fallback demo values.")
        # Fallback demo data
        metrics = {
            "Total Revenue": 52780.45,
            "Total Profit": 18250.76,
            "Avg ROAS": 3.27,
            "Avg Profit Margin": 48.6,
            "Total Orders": 90,
        }


    st.markdown("""
    <style>
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .metric-card {
        background-color: #1b1b1b;
        border-radius: 16px;
        padding: 16px 14px;
        color: #e5c17d;
        text-align: center;
        border: 1px solid #2a2a2a;
        box-shadow: 0 1px 4px rgba(0,0,0,0.25);
    }
    .metric-title { font-weight: 700; font-size: 0.9rem; color: #e5c17d; margin-bottom: 6px; }
    .metric-value { font-size: 1.2rem; color: #f3e2b3; }
    @media (max-width: 900px) { .metric-grid { grid-template-columns: repeat(2, 1fr); } }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='metric-grid'>
            <div class='metric-card'><div class='metric-title'>Revenue (Total)</div><div class='metric-value'>${metrics['Total Revenue']:,.0f}</div></div>
            <div class='metric-card'><div class='metric-title'>Orders</div><div class='metric-value'>{metrics['Total Orders']:,}</div></div>
            <div class='metric-card'><div class='metric-title'>Avg ROAS</div><div class='metric-value'>{metrics['Avg ROAS']:.2f}×</div></div>
            <div class='metric-card'><div class='metric-title'>Profit Margin</div><div class='metric-value'>{metrics['Avg Profit Margin']:.1f}%</div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---- Split Layout: Charts (left) | Insights + Chat (right) ----
    col_left, col_right = st.columns([2, 1], gap="large")

    # ----------------- LEFT: Charts -----------------
    with col_left:
        st.subheader("📈 Daily Revenue Trend")

        # Fallback handling for missing chart data
        if df["revenue"].sum() == 0:
            st.info("No revenue data available for plotting.")
            return

        if "date" in df.columns and "revenue" in df.columns:
            df_sorted = df.sort_values("date")
            if px:
                # Smooth the curve using a 3-day rolling mean, min_periods=1 to avoid NaNs
                df_sorted["revenue_smoothed"] = df_sorted["revenue"].rolling(3, min_periods=1).mean()
                fig = px.line(df_sorted, x="date", y="revenue_smoothed", markers=False)
                fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.line_chart(df_sorted, x="date", y="revenue", use_container_width=True)
        else:
            st.info("Revenue trend requires 'date' and 'revenue' columns.")

        # Expense breakdown (pie)
        st.subheader("💸 Expense Breakdown")
        # Detect common expense columns; ignore missing
        expense_cols = [c for c in ["cogs", "ads", "fulfillment", "shipping", "overhead"] if c in df.columns]
        if expense_cols:
            expense_sums = df[expense_cols].sum().reset_index()
            expense_sums.columns = ["category", "amount"]
            if px:
                fig2 = px.pie(expense_sums, names="category", values="amount", hole=0.3)
                fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.bar_chart(expense_sums.set_index("category"))
        else:
            st.caption("No expense columns found. Add any of: cogs, ads, fulfillment, shipping, overhead.")

    # ----------------- RIGHT: Insights + Chat -----------------
    with col_right:
        st.subheader("🧠 Financial Insight Summary")
        if summarize_financials:
            if st.button("▶ Generate Summary"):
                with st.spinner("Analyzing financial data..."):
                    try:
                        summary = summarize_financials(df)
                        st.success("Insight Generated ✅")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Summary error: {e}")
        else:
            st.info("`summarize_financials.py` not available or failed to import.")

        st.markdown("---")
        finance_chat_interface(df)  # Conversational RAG with your finance data

    # ---- Alerts (WoW / thresholds) — optional visual flags ----
    try:
        if "date" in df.columns and "revenue" in df.columns:
            df_week = df.sort_values("date").set_index("date").resample("W")["revenue"].sum()
            if len(df_week) >= 2:
                wow_change = ((df_week.iloc[-1] - df_week.iloc[-2]) / max(df_week.iloc[-2], 1e-9)) * 100
                if wow_change <= -10:
                    st.warning(f"⚠️ Revenue down {wow_change:.1f}% week-over-week.")
    except Exception:
        pass