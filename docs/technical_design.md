# Technical Design – AI Cost & Insights Copilot

## 1. Architecture

The system is built as a **modular AI-native analytics app** with three main layers:  

- **Data Layer**  
  - Stores pre-processed billing and resource metadata in a **SQLite warehouse (`warehouse.db`)**.  
  - Vector store (Chroma) persists embeddings for RAG queries.  

- **Application Layer**  
  - **FastAPI** service provides APIs for KPIs, recommendations, and Q&A.  
  - **Analytics module** computes KPIs (monthly cost trends, service breakdowns, anomalies).  
  - **AI module** implements RAG using embeddings + Chroma vector DB for natural language queries.  
  - **Recommendation engine** detects savings opportunities (e.g., idle resources, missing tags).  

- **Presentation Layer**  
  - **Streamlit UI** offers KPI dashboards and a chat interface to interact with the AI Copilot.  
  - Charts and tables are dynamically generated for numeric/analytical queries.  

### Architecture Diagram

```
                ┌───────────────────────────┐
                │        Streamlit UI       │
                │ (KPI view + Chat interface)│
                └─────────────┬─────────────┘
                              │ REST calls
                              ▼
                ┌───────────────────────────┐
                │         FastAPI API        │
                │  /kpi  /ask  /recommend    │
                └─────────────┬─────────────┘
             ┌────────────────┼─────────────────┐
             ▼                ▼                 ▼
   ┌────────────────┐  ┌───────────────┐  ┌──────────────┐
   │ Analytics (KPIs)│  │ AI (RAG Q&A) │  │ Recommendations│
   └───────┬─────────┘  └──────┬────────┘  └──────┬───────┘
           │                   │                  │
           ▼                   ▼                  ▼
   ┌──────────────┐    ┌───────────────┐  ┌──────────────┐
   │ SQLite (DB)  │    │ Chroma Vector │  │ Heuristic     │
   │ billing + res│    │ Store         │  │ Rules Engine  │
   └──────────────┘    └───────────────┘  └──────────────┘
```

---

## 2. Data Model

### Database schema (SQLite)

- **billing**  
  - `invoice_month` (TEXT)  
  - `account_id` (TEXT)  
  - `subscription` (TEXT)  
  - `service` (TEXT)  
  - `resource_group` (TEXT)  
  - `resource_id` (TEXT)  
  - `region` (TEXT)  
  - `usage_qty` (REAL)  
  - `unit_cost` (REAL)  
  - `cost` (REAL)  

- **resources**  
  - `resource_id` (TEXT, PK)  
  - `owner` (TEXT)  
  - `env` (TEXT)  
  - `tags_json` (TEXT/JSON)  

### Vector Store (Chroma)

- Embeddings for **billing data summaries** and **FinOps tips docs**.  
- Supports retrieval for RAG Q&A queries.  

---

## 3. Trade-offs

- **SQLite vs Postgres**  
  - Chose SQLite for simplicity and portability (runs locally without setup).  
  - Trade-off: limited concurrency, but acceptable for single-user prototype.  

- **Chroma vs FAISS**  
  - Chroma chosen for persistence + ease of integration with LangChain.  
  - FAISS is faster at scale but lacks built-in persistence.  

- **Pre-generated DB vs Runtime ingestion**  
  - Chose to pre-generate `warehouse.db` for reproducibility.  
  - Trade-off: No live ingestion, but ensures `docker compose up` always works.  

- **Streamlit vs React**  
  - Streamlit used for speed and Python-native data viz.  
  - React offers richer UX but adds frontend complexity.  

---

## 4. Risks & Mitigations

- **Data quality issues** (nulls, duplicates, negative costs)  
  - Mitigation: Built-in ETL checks before populating DB.  

- **RAG grounding quality** (retrieved chunks may be irrelevant)  
  - Mitigation: Use Recall@k evaluation and few-shot prompting.  

- **Scaling bottlenecks** (SQLite, single-node Chroma)  
  - Mitigation: Can migrate to Postgres + managed vector DB if needed.  

- **Prompt injection attacks** (malicious queries)  
  - Mitigation: Add input validation + simple guardrails.  

---

## 5. Alternatives Considered

- **Database**: Could have used Postgres for scalability.  
- **Vector store**: FAISS as an alternative to Chroma.  
- **LLM hosting**: OpenAI API vs local LLaMA/Ollama. Currently using OpenAI (pluggable).  
- **UI**: Flask + templates or React. Streamlit chosen for rapid prototyping.  
 
