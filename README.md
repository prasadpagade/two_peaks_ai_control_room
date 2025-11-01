Two Peaks AI Control Room — GTM Ops With 4 FTEs of Leverage

Run your GTM like a team of specialists: Marketing, Finance, Customer Insights, and Support agents collaborate through a simple control room. Orchestrated by n8n, reasoned by LangGraph, surfaced in Streamlit/Gradio, and powered by OpenAI. Built to be reused by any SMB/mid-market business.

✨ What you get
	•	Marketing Ops: briefs → multi-variant creatives → schedule/post → performance feedback loop
	•	Finance Ops: weekly KPI packets (MRR proxy, CAC/LTV, ROAS, variance alerts)
	•	Customer Insights: RFM/cohorts, product affinities, win-back & cross-sell lists
	•	Support: 24/7 RAG chat with escalation and ticket templates

🧱 Architecture
	•	UI: Streamlit control room (dashboard/control_room_app.py), Gradio chat (dashboard/gradio_chat.py)
	•	Agents: agents/marketing/, agents/finance/, agents/insights/, agents/support/
	•	Workflows: workflows/n8n/*.json (webhooks, schedules, retries)
	•	Memory/RAG: support_agent/chroma_db/ (FAQs, SKUs, policies)
	•	Prompts & Policies: prompts/, policies/
	•	Adapters: integrations/{shopify,hubspot,salesforce,gmail,sheets}.py
	•	Observability: telemetry/ (PostHog hooks, basic OTEL tracing)

🔐 Configuration

Set these secrets in your host (Streamlit Cloud → Settings → Secrets | Docker env | Render/Heroku vars):
OPENAI_API_KEY="sk-..."
GOOGLE_SVC_JSON='{"type":"service_account",...}'   # paste the full JSON
SHEETS_SPREADSHEET_NAME="TwoPeaks_Marketing"
N8N_WEBHOOK_URL="https://n8n.twopeaks.ai/webhook/marketing_trigger"
CHROMADB_PATH="./support_agent/chroma_db"
EMAIL_ADDRESS="alerts@twopeakschai.com"
EMAIL_PASSWORD=""   # optional if using app passwords/OAuth

# 1) Clone
git clone https://github.com/<you>/two_peaks_ai_control_room && cd two_peaks_ai_control_room

# 2) Python env
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 3) Secrets (local)
export OPENAI_API_KEY="..."
export GOOGLE_SVC_JSON='{"type":"service_account",...}'
export SHEETS_SPREADSHEET_NAME="TwoPeaks_Marketing"

# 4) Run the control room
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
