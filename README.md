# Two Peaks AI Control Room

An autonomous AI operations hub for **Two Peaks Chai Co.**  
Built with **Streamlit**, **Gradio**, **OpenAI**, and **n8n**.


╔════════════════════════════════════════════════════════════════╗
║                    TWO PEAKS AI CONTROL ROOM                    ║
║                                                                ║
║  ┌───────────────┐    ┌────────────┐     ┌─────────────┐       ║
║  │ Customer      │    │ Marketing  │     │ Finance     │       ║
║  │ Insights      │───▶│ Agent      │────▶│ Agent       │────┐  ║
║  │ Agent         │◀───│ (HITL)     │◀────│ (Guardrails)│◀──┘  ║
║  └───────────────┘    └────────────┘     └─────────────┘       ║
║         │                        │                 │            ║
║         ▼                        ▼                 ▼            ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │          DECISION FEED + POLICY / EVENT BUS              │  ║
║  │  (ChromaDB + JSONL logs + Policy/Compliance checks)      │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║         │                        │                 │            ║
║         ▼                        ▼                 ▼            ║
║  ┌───────────────┐    ┌──────────────┐   ┌─────────────────┐   ║
║  │ Support Agent │    │ n8n Webhooks │   │ Google Sheets / │   ║
║  │  (RAG + FAQs) │    │ + Gmail / SMS│   │ Shopify / Drive │   ║
║  └───────────────┘    └──────────────┘   └─────────────────┘   ║
╚════════════════════════════════════════════════════════════════╝

## Setup
python -m venv .venv  
source .venv/bin/activate  
pip install -r requirements.txt  
cp .env.example .env  
streamlit run dashboard/control_room_app.py
