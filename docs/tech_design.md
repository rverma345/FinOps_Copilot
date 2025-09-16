# 🛠️ Technical Design Document (TDD)

## 1. System Overview
The **AI Cost & Insights Copilot** is a cloud cost analytics tool that:
- Ingests monthly cloud usage & cost data (CSV/JSON).
- Stores data in a relational database (SQLite/Postgres).
- Computes KPIs (spend by service, resource group, unit-cost trends).
- Runs quality checks to ensure data integrity.
- Uses **Retrieval-Augmented Generation (RAG)** to enable natural-language Q&A.
- Surfaces actionable recommendations (e.g., idle resources).
- Provides both an **API (FastAPI)** and a **UI (Streamlit)** for interaction.

---

## 2. High-Level Architecture
**Components:**
1. **Data Ingestion (ETL)**
   - Input: CSV/JSON with billing & resource metadata.
   - Load into SQLite/Postgres.
   - Perform cleaning and validation (nulls, negatives, duplicates).

2. **Data Storage**
   - Two main tables:
     - **billing** → cloud usage & cost.
     - **resources** → metadata such as owner, env, tags.

3. **Analytics & KPIs**
   - Monthly spend by service, resource group, region.
   - 6-month cost trend.
   - Top N cost drivers.
   - Unit-cost changes.
   - Quality checks.

4. **AI Layer (RAG Q&A)**
   - Vector store: FAISS/Chroma.
   - Embeddings from billing, resources, and FinOps tips.
   - LLM (OpenAI/Azure/Open-Source).
   - Prompts: system + few-shot + fallback.

5. **Recommendation Engine**
   - Heuristic-based rules:
     - Idle resources (usage_qty = 0).
     - Sudden unit-cost spikes.
     - Missing owner tags.

6. **Service Layer (API)**
   - **FastAPI Endpoints:**
     - `/kpi?month=YYYY-MM` → returns KPIs.
     - `/ask` → takes `{question}` and returns `{answer, sources, suggestions}`.

7. **UI Layer**
   - **Streamlit** for:
     - KPI Dashboard.
     - Chat interface for Q&A.

8. **Infrastructure**
   - Dockerized (API + DB + vector store).
   - Config via `.env`.
   - Logging, metrics, and security guards.

---

## 3. Data Model

### Billing Table
| Column          | Type     | Description |
|-----------------|----------|-------------|
| invoice_month   | DATE     | Billing month |
| account_id      | STRING   | Cloud account identifier |
| subscription    | STRING   | Subscription/project name |
| service         | STRING   | Cloud service (VM, Storage, DB, etc.) |
| resource_group  | STRING   | Group/project |
| resource_id     | STRING   | Unique resource identifier |
| region          | STRING   | Cloud region |
| usage_qty       | FLOAT    | Usage quantity |
| unit_cost       | FLOAT    | Cost per unit |
| cost            | FLOAT    | Total cost |

### Resources Table
| Column      | Type   | Description |
|-------------|--------|-------------|
| resource_id | STRING | Unique resource identifier |
| owner       | STRING | Owner of the resource |
| env         | STRING | Environment (dev/test/prod) |
| tags_json   | JSON   | Additional tags/metadata |

---

## 4. Trade-offs & Decisions
- **SQLite vs Postgres** → Start with SQLite for local simplicity, allow Postgres for scalability.
- **Vector Store (FAISS vs Chroma)** → Chroma for ease-of-use, FAISS for performance on larger datasets.
- **LLM Choice** → Default to OpenAI GPT-4 for quality; fallback to open-source (LLaMA/Ollama) for cost control.
- **UI Framework (Streamlit vs React)** → Streamlit chosen for speed; React could be a future upgrade.
- **Recommendation Rules** → Heuristic-based first (fast, simple); ML-based anomaly detection could be future work.

---

## 5. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large data volumes | Slow queries | Use indexing, move to Postgres |
| High LLM cost | Expensive | Caching + lightweight prompts |
| Incorrect answers | Low trust | Show retrieved sources + confidence |
| Prompt injection | Security risk | Guardrails, content filters |
| Docker build issues | Deploy failure | CI/CD testing + sample `.env.example` |

---

## 6. Alternatives Considered
- **Direct SQL-based analytics (no AI)** → Fast but lacks natural-language flexibility.
- **Cloud-native tools (AWS Cost Explorer, Azure Cost Mgmt)** → Too vendor-specific; not flexible.
- **Heavy BI tools (Power BI, Tableau)** → Require expertise, not conversational.
