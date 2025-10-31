# 💼 Two Peaks Finance & Performance Agent

This agent analyzes Shopify-style data to generate daily/weekly performance summaries
and AI-written financial insights for Two Peaks Chai Co.

## Files
- `mock_financial_data.csv` — Sample dataset (revenue, orders, ad spend, etc.)
- `generate_financial_report.py` — KPI calculations
- `summarize_financials.py` — Mock AI insights
- `finance_agent_tab.py` — Streamlit UI
- `finance_agent_workflow.json` — n8n automation skeleton

## Run the Agent
```bash
streamlit run two_peaks_ai_agents/finance_agent/finance_agent_tab.py