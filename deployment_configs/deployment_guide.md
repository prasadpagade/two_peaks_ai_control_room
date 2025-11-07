# Deployment Configuration for Two Peaks AI Control Room

## Recommended: Hybrid Deployment Strategy

### Why Hybrid?
1. **Public Layer** (Free): Showcase architecture, drive interest
2. **Demo Layer** (Controlled): Protected demo with cached responses
3. **Production Layer** (Private): Real implementation for paying customers

---

## DEPLOYMENT OPTION 1: Streamlit Community Cloud (RECOMMENDED FOR DEMO)

### Pros:
- ✅ **Free** (no hosting costs)
- ✅ Built-in authentication
- ✅ Easy deployment (GitHub integration)
- ✅ Auto-updates on git push
- ✅ Share via link (password protected)

### Cons:
- ❌ Limited compute (1GB RAM, shared CPU)
- ❌ Apps sleep after inactivity
- ❌ No custom domain on free tier

### Setup Steps:

#### 1. Prepare Repository Structure
```
two_peaks_ai_control_room/
├── dashboard/
│   ├── control_room_app.py          # Main Streamlit app
│   ├── pages/                        # Multi-page app
│   └── demo_mode.py                  # Demo mode with cached data
├── requirements.txt                  # Python dependencies
├── .streamlit/
│   ├── config.toml                   # Streamlit config
│   └── secrets.toml.example          # Secret template (not committed)
└── README.md
```

#### 2. Create `requirements.txt`
```txt
streamlit==1.29.0
langchain==0.1.0
langgraph==0.0.20
openai==1.6.0
chromadb==0.4.18
pandas==2.1.4
plotly==5.18.0
python-dotenv==1.0.0
pydantic==2.5.3
requests==2.31.0
```

#### 3. Create `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

#### 4. Implement Demo Mode

**File: `dashboard/demo_mode.py`**
```python
import os
import json
from typing import Dict, Any

# Demo mode flag from environment
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Cached responses for demo
CACHED_RESPONSES = {
    "weekly_gtm": {
        "marketing": {
            "campaigns_active": 8,
            "roas_by_channel": {
                "email": 4.2,
                "social": 2.8,
                "paid_search": 3.5
            },
            "top_performing": "Email - Product Launch (12.3% CTR)"
        },
        "finance": {
            "revenue_week": 47800,
            "cac": 42,
            "ltv_cac_ratio": 3.2,
            "burn_rate": 18000,
            "forecast_month": 210000
        },
        "insights": {
            "total_customers": 1847,
            "segments": {
                "champions": 342,
                "loyal": 487,
                "at_risk": 127,
                "churned": 89
            },
            "churn_risk_alert": {
                "count": 23,
                "avg_ltv": 2400,
                "potential_recovery": 55200
            }
        },
        "support": {
            "tickets_week": 180,
            "avg_response_time": "28 seconds",
            "deflection_rate": 0.62,
            "top_issues": [
                "Return policy questions",
                "Shipping delays",
                "Product recommendations"
            ]
        }
    },
    "winback_campaign": {
        "churned_customers_found": 89,
        "target_segment": "At Risk (90 days inactive)",
        "email_drafts_created": 89,
        "estimated_response_rate": 0.10,
        "potential_revenue": 21360,
        "campaign_cost": 445
    },
    "support_query": {
        "question": "What's your return policy?",
        "answer": "Our return policy allows returns within 30 days of purchase for unopened items. Perishable items like chai can be returned within 7 days if refrigerated properly. You'll receive a full refund or replacement.",
        "confidence": 0.94,
        "source": "Returns & Refunds Policy, Section 3.2",
        "response_time": 0.4
    }
}

def get_demo_data(query_type: str) -> Dict[str, Any]:
    """
    Returns cached demo data instead of making real API calls.
    
    Args:
        query_type: Type of query (weekly_gtm, winback_campaign, support_query)
    
    Returns:
        Cached response data
    """
    if not DEMO_MODE:
        raise ValueError("Demo mode not enabled")
    
    return CACHED_RESPONSES.get(query_type, {})

def is_demo_mode() -> bool:
    """Check if app is running in demo mode"""
    return DEMO_MODE
```

**File: `dashboard/control_room_app.py`** (Modified)
```python
import streamlit as st
from demo_mode import is_demo_mode, get_demo_data

st.set_page_config(
    page_title="Two Peaks AI Control Room",
    page_icon="🎛️",
    layout="wide"
)

# Demo mode banner
if is_demo_mode():
    st.warning("🎬 **DEMO MODE** - Using cached responses to avoid API costs. For live demo, contact prasad@twopeakschai.com")

# Main dashboard
st.title("🎛️ Two Peaks AI Control Room")
st.markdown("Run your GTM operations like a team of specialists")

# Weekly GTM Run
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("▶️ Run Weekly GTM", type="primary", use_container_width=True):
        with st.spinner("Running all agents..."):
            if is_demo_mode():
                results = get_demo_data("weekly_gtm")
            else:
                # Real API call
                results = run_real_agents()
            
            # Display results
            st.success("✅ Weekly GTM report complete!")
            
            # Marketing
            with st.expander("🎨 Marketing Agent", expanded=True):
                st.metric("Active Campaigns", results["marketing"]["campaigns_active"])
                st.json(results["marketing"]["roas_by_channel"])
            
            # Finance
            with st.expander("💰 Finance Agent", expanded=True):
                st.metric("Revenue (Week)", f"${results['finance']['revenue_week']:,}")
                st.metric("CAC", f"${results['finance']['cac']}")
                st.metric("LTV:CAC", f"{results['finance']['ltv_cac_ratio']}:1")
            
            # Insights
            with st.expander("📈 Insights Agent", expanded=True):
                st.metric("Total Customers", results["insights"]["total_customers"])
                st.json(results["insights"]["segments"])
            
            # Support
            with st.expander("🎧 Support Agent", expanded=True):
                st.metric("Tickets (Week)", results["support"]["tickets_week"])
                st.metric("Avg Response Time", results["support"]["avg_response_time"])

# More UI components...
```

#### 5. Deploy to Streamlit Cloud

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add demo mode for Streamlit deployment"
git push origin main
```

2. **Connect to Streamlit Cloud:**
- Go to https://share.streamlit.io
- Sign in with GitHub
- Click "New app"
- Select repository: `prasadpagade/two_peaks_ai_control_room`
- Main file: `dashboard/control_room_app.py`
- Advanced settings:
  - Python version: 3.10
  - Secrets: Add `DEMO_MODE = "true"`

3. **Configure Authentication** (Streamlit Cloud):
- In app settings → Sharing
- Enable "Restrict viewing access"
- Add authorized emails (or keep private link)

4. **Share:**
- Get app URL: `https://prasadpagade-two-peaks-control-room.streamlit.app`
- Share password-protected link with hiring teams

---

## DEPLOYMENT OPTION 2: Vercel (Static Landing Page)

### Use Case: Public marketing site with architecture diagrams

### Setup:

#### 1. Create Next.js Site
```bash
npx create-next-app@latest two-peaks-landing
cd two-peaks-landing
```

#### 2. Add Interactive Diagrams
```javascript
// pages/index.js
import Head from 'next/head'
import { useState } from 'react'

export default function Home() {
  return (
    <div className="container">
      <Head>
        <title>Two Peaks AI Control Room</title>
      </Head>

      <main>
        <h1>🎛️ Two Peaks AI Control Room</h1>
        <p>Automate your GTM operations with AI agents</p>
        
        {/* Embedded architecture diagram */}
        <img src="/architecture.svg" alt="System Architecture" />
        
        {/* Demo video */}
        <iframe 
          src="https://www.loom.com/embed/YOUR_VIDEO_ID" 
          width="100%" 
          height="400"
        />
        
        {/* ROI Calculator (static JS) */}
        <ROICalculator />
        
        {/* Request demo CTA */}
        <a href="https://your-streamlit-demo.app">
          Try Live Demo (Password Protected)
        </a>
      </main>
    </div>
  )
}
```

#### 3. Deploy to Vercel
```bash
npm install -g vercel
vercel login
vercel deploy
```

**Result:** Free static site at `https://two-peaks-control-room.vercel.app`

---

## DEPLOYMENT OPTION 3: Railway / Fly.io (Production)

### Use Case: Full production deployment with real API calls

### Pros:
- ✅ Full control over environment
- ✅ Can run n8n workflows
- ✅ Custom domains
- ✅ Better compute resources

### Cons:
- ❌ Costs $5-20/month
- ❌ More complex setup

### Setup (Railway):

#### 1. Create `railway.toml`
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "streamlit run dashboard/control_room_app.py --server.port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### 2. Add Environment Variables
```bash
DEMO_MODE=false
OPENAI_API_KEY=sk-proj-...
GOOGLE_SHEETS_CREDS={"type":"service_account",...}
N8N_WEBHOOK_URL=https://your-n8n.app/webhook
```

#### 3. Deploy
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## RECOMMENDED ARCHITECTURE FOR YOUR USE CASE

### Scenario: Impress potential employers without incurring API costs

```
┌────────────────────────────────────────────────────────────┐
│                PUBLIC LANDING (Vercel - Free)              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Static site with:                                    │ │
│  │  • Architecture diagrams                             │ │
│  │  • Embedded Loom video                               │ │
│  │  • ROI calculator (static JS, no backend)            │ │
│  │  • "Try Demo" CTA → Streamlit                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  URL: https://two-peaks-ai.vercel.app                     │
└────────────────────────────────────────────────────────────┘
                           │
                           │ (Click "Try Demo")
                           ▼
┌────────────────────────────────────────────────────────────┐
│          DEMO DASHBOARD (Streamlit Cloud - Free)           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Streamlit app with DEMO_MODE=true                   │ │
│  │  • All responses cached (no API calls)               │ │
│  │  • Password protected                                │ │
│  │  • Banner: "Demo mode - contact for live version"   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  URL: https://prasadpagade-two-peaks.streamlit.app        │
│  Auth: Restricted viewing (share password-protected link)        │
└────────────────────────────────────────────────────────────┘
```

**Total Cost: $0** ✅

---

## FINAL RECOMMENDATION

### For Portfolio Interviews:

**Use:** Streamlit Community Cloud with Demo Mode

**Why:**
1. ✅ **Zero API costs** (cached responses)
2. ✅ **Professional presentation** (clean UI)
3. ✅ **Easy to share** (password-protected link)
4. ✅ **Fast deployment** (5 minutes from code to live)
5. ✅ **No infrastructure management**

**Deployment Checklist:**
- [ ] Push code to GitHub
- [ ] Enable demo mode (`DEMO_MODE=true`)
- [ ] Deploy to Streamlit Cloud
- [ ] Test demo flows (weekly GTM, win-back, support)
- [ ] Configure access restrictions for demo link
- [ ] Send email with context:
  ```
  Hi [Hiring Manager],
  
  Here's a live demo of the AI Control Room I built:
  https://prasadpagade-two-peaks.streamlit.app
  
  It's running in demo mode (cached responses) to avoid API costs,
  but shows the full system architecture and UX.
  
  For technical deep dive, see:
  - GitHub: [repo link]
  - Architecture docs: [link]
  - Video walkthrough: [Loom link]
  
  Looking forward to discussing how this can benefit your organization!
  
  Best,
  Prasad
  ```

---

## Alternative: Docker Container (For Local Demo)

### If they want to run it themselves:

**Create `Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV DEMO_MODE=true

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/control_room_app.py"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  control-room:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEMO_MODE=true
    volumes:
      - ./data:/app/data
```

**Usage:**
```bash
docker-compose up
# Visit http://localhost:8501
```

**Benefits:**
- ✅ Runs on their machine (no sharing concerns)
- ✅ No external dependencies
- ✅ Professional packaging

