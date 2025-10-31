# dashboard/tabs/insights_tab.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Optional imports for charting
import matplotlib.pyplot as plt

# -----------------------------------
# GOOGLE SHEETS SETUP (with graceful fallback)
# -----------------------------------
def load_sheet_data():
    try:
        # Expected: service account JSON stored locally or via environment variable
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file("google_service_account.json", scopes=scopes)
        gc = gspread.authorize(creds)

        # Example: read data from your main sheet
        sh = gc.open("TwoPeaks_Data")
        worksheet = sh.worksheet("Insights")
        df = pd.DataFrame(worksheet.get_all_records())
        return df

    except Exception as e:
        st.warning("⚠️ Could not connect to Google Sheets — using sample data instead.")
        df = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr"],
            "Revenue": [12000, 14500, 17000, 16500],
            "Orders": [240, 280, 320, 300],
            "Repeat_Customers": [50, 62, 71, 69],
        })
        return df


# -----------------------------------
# INSIGHTS TAB RENDER
# -----------------------------------
def render_insights_tab():
    st.header("📊 Customer Insights Agent")
    st.caption("View performance trends, returning customers, and key growth insights.")

    df = load_sheet_data()

    # --- Metric Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>Total Revenue</h3><span>${df['Revenue'].sum():,.0f}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>Total Orders</h3><span>{df['Orders'].sum()}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>Avg Revenue / Order</h3><span>${df['Revenue'].sum() / df['Orders'].sum():.2f}</span></div>", unsafe_allow_html=True)
    with col4:
        repeat_rate = (df['Repeat_Customers'].sum() / df['Orders'].sum()) * 100
        st.markdown(f"<div class='metric-card'><h3>Repeat Customer %</h3><span>{repeat_rate:.1f}%</span></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Chart Section ---
    st.subheader("📈 Monthly Revenue Trend")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["Month"], df["Revenue"], marker="o", color="#b99746", linewidth=2)
    ax.set_facecolor("#f6f3eb")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.set_title("Revenue Growth", fontweight="bold", color="#2e4a26")
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Table View ---
    st.subheader("📋 Detailed Data")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<br><small>💡 Tip: Connect your Google Sheet ‘TwoPeaks_Data → Insights’ to auto-sync these metrics.</small>", unsafe_allow_html=True)