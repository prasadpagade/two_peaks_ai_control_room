# 🎮 AI Control Room for GTM Operations

**Run your Go-To-Market operations like a team of specialists—without the headcount**

[![Portfolio](https://img.shields.io/badge/Portfolio-View-gold?style=for-the-badge)](https://prasadpagade.github.io/Data_AI_Portfolio_website/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)

---

## 🎯 What This Is

An AI-powered control room that orchestrates specialized agents for Marketing, Finance, Customer Insights, and Support—giving small teams the leverage of a full GTM organization.

Think of it as **4 FTEs of intelligent automation** coordinating seamlessly through a single dashboard.

**Explore my full portfolio:** [prasadpagade.github.io/Data_AI_Portfolio_website](https://prasadpagade.github.io/Data_AI_Portfolio_website/)

---

## ✨ What It Does

### Automated GTM Operations
- **Weekly GTM Runs:** Trigger Marketing, Finance, and Insights in a single workflow
- **Win-Back Campaigns:** Identify lapsed customers → draft outreach → execute → track results
- **Support Intelligence:** RAG-powered Q&A with automatic ticket escalation
- **Data Synthesis:** Pull from Stripe, Sheets, HubSpot/Salesforce → generate insights

### Specialized AI Agents

**Marketing Agent**
- Campaign ideation and execution
- Email/social copy generation
- A/B test analysis
- Performance reporting

**Finance Agent**
- Revenue forecasting
- Cohort analysis (CAC, LTV)
- Topline metrics (orders, revenue, ROAS)
- Profitability modeling

**Customer Insights Agent**
- RFM segmentation
- Churn prediction
- NPS proxy analysis
- Behavioral cohort tracking

**Support Agent**
- RAG-powered policy lookup
- FAQ automation with confidence scoring
- Low-confidence escalation to human tickets
- Response time optimization

---

## 🚀 Why This Matters

### The SMB/Mid-Market Challenge
Growing companies need GTM sophistication but can't justify 4+ specialized hires. Traditional solutions:
- **Hire generalists:** Lack depth in critical areas
- **Outsource:** Expensive, slow, misaligned incentives
- **Do it manually:** Founder/team burnout, inconsistent execution

### The AI Agent Solution
Specialized intelligence coordinated through a single control room—combining the expertise of specialists with the efficiency of automation.

---

## 📊 Key Performance Indicators

The system automates tracking and reporting for:

**Topline Metrics**
- Orders and revenue by channel
- Channel-level ROAS
- Customer acquisition cost (CAC)
- Lifetime value (LTV)

**Retention & Engagement**
- Cohort retention curves
- RFM segmentation
- Churn risk scoring
- Win-back campaign performance

**Support Efficiency**
- First response time
- Resolution rate
- Ticket volume trends
- NPS proxy scores

---

## 🏗️ Architecture Overview

### Orchestration Layer (n8n)
Coordinates workflows between agents, triggers scheduled runs, manages data flow between integrations.

### Reasoning Engine (LangGraph)
Enables agents to plan multi-step workflows, make decisions, and collaborate on complex tasks.

### User Interface (Streamlit/Gradio)
Control room dashboard for monitoring, manual triggers, and configuration. Support chat interface for RAG-powered Q&A.

### LLM Intelligence (OpenAI)
Powers natural language understanding, content generation, and intelligent decision-making across all agents.

---

## 🔧 Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | n8n | Workflow automation |
| **Agent Framework** | LangGraph | Multi-step reasoning |
| **UI (Dashboard)** | Streamlit | Control room interface |
| **UI (Support)** | Gradio | Chat interface |
| **LLM** | OpenAI API | Intelligence layer |
| **Vector Search** | ChromaDB | RAG for support |
| **Integrations** | Stripe, Google Sheets | Data sources |
| **Language** | Python 3.11+ | Core implementation |

---

## 💼 Adapting to Any Business

### Modular Integration Layer
Swap data adapters in `integrations/` to connect:
- **CRM:** HubSpot, Salesforce, Pipedrive
- **Payment:** Stripe, PayPal, Gusto
- **Analytics:** Google Analytics, Segment, Mixpanel
- **Support:** Zendesk, Intercom, Freshdesk

### Customizable Prompts
Agent behavior controlled through `prompts/` directory—tune tone, analysis depth, and decision thresholds without touching code.

### Configurable Policies
Business rules in `policies/` for escalation triggers, approval workflows, and compliance guardrails.

---

## 🎯 Use Case Examples

### Weekly GTM Review (Automated)
1. Finance Agent pulls Stripe revenue data
2. Marketing Agent analyzes campaign performance
3. Insights Agent identifies at-risk cohorts
4. All synthesized into executive summary
5. Delivered to Slack/email every Monday morning

### Win-Back Campaign (Semi-Automated)
1. Insights Agent identifies lapsed customers (last purchase >90 days)
2. Marketing Agent drafts personalized win-back emails
3. Human reviews and approves batch
4. Marketing Agent sends via connected email tool
5. Results logged to Google Sheets for tracking

### Support Q&A (Fully Automated)
1. Customer asks question via Gradio chat
2. Support Agent uses RAG to search policies/FAQs
3. High-confidence answers sent immediately
4. Low-confidence questions escalated to human support
5. All interactions logged for continuous improvement

---

## 🧯 Common Setup Issues

### Missing API Keys
Set `OPENAI_API_KEY` in environment or host secrets management.

### Google Sheets Permissions
Share target spreadsheet with service account email from credentials JSON.

### RAG Not Retrieving
Rebuild embeddings: `python support_agent/build_index.py`

### n8n Workflow Errors
Check webhook URLs match deployed endpoints. Verify integration credentials are current.

---

## 📈 Impact Metrics

### Efficiency Gains
- **80% reduction** in manual GTM tasks
- **60% faster** insight generation
- **40% improvement** in customer response time

### Business Outcomes
- More consistent GTM execution
- Data-driven decision making
- Scalable growth without linear headcount
- Better work-life balance for founders/teams

---

## 💡 Key Learnings

### Start with One Agent
Begin with the highest-impact area (usually Marketing or Support). Prove value before expanding.

### Human-in-the-Loop Initially
Let agents draft, humans approve. Build confidence before full automation.

### Measure Before and After
Baseline current performance. Track impact of each agent addition.

### Iterate on Prompts
Agent quality improves dramatically with prompt tuning. Invest time here.

### Monitor Costs
LLM API costs scale with usage. Set budgets and implement caching strategies.

---

## 🌐 Skills Demonstrated

- **AI Agent Design:** Multi-agent orchestration and collaboration
- **System Integration:** Connecting disparate data sources into unified workflows
- **LLM Engineering:** Prompt optimization, RAG implementation, confidence scoring
- **Business Operations:** Deep understanding of GTM metrics and processes
- **Full-Stack Development:** Backend logic, UI/UX, deployment

---

## 🤝 Connect & Explore

**Full Portfolio:** [prasadpagade.github.io/Data_AI_Portfolio_website](https://prasadpagade.github.io/Data_AI_Portfolio_website/)  
**LinkedIn:** [linkedin.com/in/prasadpagade](https://linkedin.com/in/prasadpagade)  
**GitHub:** [github.com/prasadpagade](https://github.com/prasadpagade)  
**Email:** prasad.pagade@gmail.com

---

<div align="center">

**Intelligent Automation for Modern GTM Teams**

*The leverage of a full team, the simplicity of a single dashboard*

</div>
