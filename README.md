Two Peaks AI Control Room — GTM Ops With 4 FTEs of Leverage

Run your GTM like a team of specialists: Marketing, Finance, Customer Insights, and Support agents collaborate through a simple control room. Orchestrated by n8n, reasoned by LangGraph, surfaced in Streamlit/Gradio, and powered by OpenAI. Built to be reused by any SMB/mid-market business.

streamlit run dashboard/control_room_app.py

🧪 Demo Flows
	•	Weekly GTM Run: triggers Marketing, Finance, and Insights in a single pass (n8n → agents → artifacts).
	•	Win-Back Campaign: Insights finds lapsed customers → Marketing drafts/send → results logged to Sheets.
	•	Support Q&A: Gradio chat pulls policies/FAQ via RAG, escalates low-confidence answers to ticket.

📊 KPIs This Automates
	•	Topline (orders/revenue), channel ROAS, CAC/LTV, cohort retention, RFM segments, NPS proxy, first-response time.

🧰 Adapting to Any Business

Swap adapters in integrations/ (HubSpot/Salesforce/Gusto). Keep prompts in prompts/; edit thresholds in policies/.

🧯 Troubleshooting
	•	Missing OPENAI_API_KEY → set in host secrets.
	•	Sheets permissions → share the spreadsheet with your service account email.
	•	RAG not retrieving → rebuild embeddings: python support_agent/build_index.py.
