# Architecture Diagram 2: Technical System Architecture
# For Engineering and Technical Stakeholders

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI1[Streamlit<br/>Control Room<br/>Dashboard]
        UI2[Gradio<br/>Support Chat<br/>Interface]
    end
    
    subgraph "API Gateway"
        API[FastAPI<br/>REST Endpoints<br/>+ WebSocket]
    end
    
    subgraph "Orchestration Layer"
        N8N[n8n Workflow Engine<br/>────────────<br/>• Cron Schedules<br/>• Event Triggers<br/>• Error Handling<br/>• Retry Logic]
    end
    
    subgraph "Multi-Agent Coordination"
        SUP[LangGraph Supervisor<br/>────────────<br/>• Task Routing<br/>• State Management<br/>• Parallel Execution<br/>• Result Aggregation]
    end
    
    subgraph "Agent Layer"
        MA[Marketing Agent<br/>────────────<br/>LLM: GPT-4 Turbo<br/>Tools:<br/>• Campaign Gen<br/>• Channel Analysis<br/>• Email Drafting]
        
        FA[Finance Agent<br/>────────────<br/>LLM: GPT-3.5 Turbo<br/>Tools:<br/>• Metrics Calc<br/>• Forecasting<br/>• Budget Analysis]
        
        IA[Insights Agent<br/>────────────<br/>LLM: GPT-4 Turbo<br/>Tools:<br/>• RFM Segmentation<br/>• Churn Prediction<br/>• Cohort Analysis]
        
        SA[Support Agent<br/>────────────<br/>LLM: GPT-3.5 Turbo<br/>RAG: ChromaDB<br/>Tools:<br/>• KB Search<br/>• Ticket Creation<br/>• Confidence Scoring]
    end
    
    subgraph "Integration Layer"
        INT1[Email API<br/>SendGrid/Mailgun]
        INT2[Google Sheets<br/>API v4]
        INT3[CRM Adapter<br/>HubSpot/Salesforce]
        INT4[Payments<br/>Stripe API]
        INT5[Support<br/>Zendesk API]
    end
    
    subgraph "Data Layer"
        VEC[ChromaDB<br/>Vector Store<br/>────────────<br/>Knowledge Base<br/>Embeddings]
        
        CACHE[Redis Cache<br/>────────────<br/>Session State<br/>Query Results]
        
        DB[(PostgreSQL<br/>────────────<br/>Audit Logs<br/>Metrics History)]
    end
    
    subgraph "External Services"
        LLM[OpenAI API<br/>────────────<br/>GPT-4 Turbo<br/>GPT-3.5 Turbo<br/>text-embedding-3]
    end
    
    UI1 --> API
    UI2 --> API
    API --> N8N
    N8N --> SUP
    
    SUP --> MA
    SUP --> FA
    SUP --> IA
    SUP --> SA
    
    MA --> LLM
    FA --> LLM
    IA --> LLM
    SA --> LLM
    SA --> VEC
    
    MA --> INT1
    MA --> INT3
    FA --> INT2
    FA --> INT4
    IA --> INT3
    IA --> INT2
    SA --> INT5
    SA --> VEC
    
    SUP --> CACHE
    N8N --> DB
    
    style SUP fill:#4A90E2,stroke:#000,stroke-width:3px,color:#fff
    style N8N fill:#FF6B6B,stroke:#000,stroke-width:2px,color:#fff
    style MA fill:#FFB6C1,stroke:#000,stroke-width:2px
    style FA fill:#98FB98,stroke:#000,stroke-width:2px
    style IA fill:#87CEEB,stroke:#000,stroke-width:2px
    style SA fill:#DDA0DD,stroke:#000,stroke-width:2px
    style LLM fill:#FFD700,stroke:#000,stroke-width:2px
    style VEC fill:#FFA500,stroke:#000,stroke-width:2px
```

## Technology Stack Details

### Frontend
- **Streamlit**: Python-based web framework for data apps
- **Gradio**: ML model interface for support chat
- **Plotly**: Interactive visualizations

### Backend
- **FastAPI**: High-performance async API framework
- **LangChain/LangGraph**: Multi-agent orchestration
- **n8n**: Workflow automation and scheduling

### LLMs
- **GPT-4 Turbo**: Creative/complex reasoning tasks
  - Marketing content generation
  - Customer insight analysis
- **GPT-3.5 Turbo**: Fast/structured tasks
  - Financial calculations
  - Support query responses
- **text-embedding-3**: Vector embeddings for RAG

### Data Storage
- **ChromaDB**: Vector database for semantic search
- **Redis**: In-memory cache for sessions
- **PostgreSQL**: Relational DB for audit logs
- **Google Sheets**: Lightweight data storage/sharing

### Integrations
- **Email**: SendGrid, Mailgun
- **CRM**: HubSpot, Salesforce (adapter pattern)
- **Payments**: Stripe
- **Support**: Zendesk

## Data Flow Patterns

### 1. Real-time Query Flow
```
User Input → API → Supervisor → Agent → LLM → Tools → Response
                                    ↓
                                  Cache (for 1 hour)
```

### 2. Scheduled Workflow Flow
```
Cron Trigger → n8n → Supervisor → Parallel Agents → Aggregate → Sheets
                                         ↓
                                    DB Log (audit)
```

### 3. RAG-Enhanced Support Flow
```
Question → Support Agent → Vector Search → Context + Question → LLM → Answer
                               ↓
                         ChromaDB (semantic search)
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Cloud Infrastructure                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │  GCP Cloud Run │  │ Railway / Fly  │  │ Streamlit Cloud│ │
│  │  ─────────────│  │  ─────────────│  │  ──────────────│ │
│  │  • n8n         │  │  • FastAPI     │  │  • Dashboard   │ │
│  │  • Agents      │  │  • Redis       │  │  • Auth        │ │
│  │  • ChromaDB    │  │                │  │                │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Vercel (Static Site)                         │ │
│  │            • Public landing page                        │ │
│  │            • Architecture diagrams                      │ │
│  │            • Demo video                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
├─────────────────────────────────────────────────────────┤
│ 1. API Authentication: Bearer tokens, rate limiting     │
│ 2. Data Encryption: TLS 1.3, at-rest encryption         │
│ 3. Secret Management: Environment variables, Vault      │
│ 4. Access Control: RBAC, least privilege                │
│ 5. Audit Logging: All API calls logged to PostgreSQL    │
│ 6. PII Anonymization: Automated redaction in logs       │
└─────────────────────────────────────────────────────────┘
```

## Scalability Metrics

| Component | Current Capacity | Scale Target | Strategy |
|-----------|-----------------|--------------|----------|
| **API** | 100 req/min | 10K req/min | Horizontal + CDN |
| **Agents** | 10 concurrent | 100 concurrent | Worker pool |
| **DB** | 100K records | 10M records | Sharding |
| **Cache** | 1GB | 10GB | Redis cluster |
