# 💰 FinOps Copilot

FinOps Copilot is a cloud cost analytics and recommendation platform using **FastAPI**, **Streamlit**, and **Chroma vector DB**. Users can view KPIs, ask questions in natural language, and get answers with sources.

---

## 🏗️ Architecture

* **API (FastAPI)**

  * Provides endpoints for KPIs and RAG-based Q\&A.
  * Endpoints:

    * `GET /kpi?month=YYYY-MM` → Returns KPIs for the specified month.
    * `POST /ask` → Accepts `{ "question": "..." }` and returns `{ answer, sources }`.
  * Uses **SQLite** for synthetic cloud usage data.
  * Integrates **OpenAI embeddings** and **Chroma vector DB** for retrieval.

* **Frontend (Streamlit)**

  * Minimal dashboard to view KPIs and ask questions.
  * Connects to FastAPI for live data.
  * Chat interface for natural language queries.

* **Vector DB (Chroma)**

  * Stores document chunks and synthetic data for RAG pipeline.
  * Persistent storage configured in Docker volume.

* **Database (SQLite)**

  * Stores synthetic cloud usage data (`billing` and `resources` tables).

---

## 📦 Requirements

* **Docker** & **Docker Compose**
* `.env` file in root directory with:

  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  ```

---

## 🏁 Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/finops-copilot.git
   cd finops-copilot
   ```

2. Create `.env` in the root:

   ```env
   OPENAI_API_KEY=YOUR_OPENAI_KEY
   ```

3. Build and run Docker containers:

   ```bash
   docker-compose up --build
   ```

4. Access services:

   * **Streamlit UI** → [http://localhost:8501](http://localhost:8501)
   * **FastAPI Docs** → [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Chroma Dashboard** → [http://localhost:8001](http://localhost:8001)

---

## 🗂️ Project Structure

finops-copilot/
├── .gitignore
├── .env.example                  # Example env file with placeholder for OPENAI_API_KEY
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── data/
│   ├── processed/
│   │   ├── warehouse.db          # Pre-generated SQLite DB with sample data
│   │   └── vector_store/         # Persisted Chroma vector store
│   └── raw/                      # Optional raw CSV/JSON data (ignored in git)
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── embeddings.py         # Ingest DB/docs into Chroma
│   │   ├──evaluate.py
│   │   ├──evaluation_results.csv
│   │   └── rag_engine.py         # RAG pipeline for Q&A
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── kpis.py               # KPI calculations
│   │   └── recommendations.py    # Recommendation rules
│   └── data/
│       ├── __init__.py
│       ├──ingestion.py
│       ├──quality_checks.py
│       ├──transformations.py
│       └──run_etl.py
├── ui/
│   ├── app.py                     # Streamlit app
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_etl.py
    ├── test_kpi.py
    └── test_retreiver.py


## ⚙️ Docker Configuration

* **Dockerfile** builds Python 3.12 image, installs dependencies, and runs Streamlit or API.
* **docker-compose.yml** configures three services:

  * `api` → FastAPI backend (port 8000)
  * `streamlit` → UI frontend (port 8501)
  * `chroma` → Vector DB (port 8001)
* Volumes persist data across container restarts.
* Internal Docker networking allows `streamlit` to call `http://api:8000`.

---

## 🚀 Usage

### FastAPI Endpoints

* **KPI Example**:

  ```bash
  curl "http://localhost:8000/kpi?month=2025-09"
  ```

* **Ask Example**:

  ```bash
  curl -X POST http://localhost:8000/ask \
       -H "Content-Type: application/json" \
       -d '{"question": "What is my monthly cost for May 2025?"}'
  ```

### Streamlit UI

* Accessible at [http://localhost:8501](http://localhost:8501)
* Features:

  * KPI viewer
  * Chat box for RAG-powered questions

---

## ⚠️ Troubleshooting

* **Streamlit cannot reach FastAPI**:

  * Inside Docker, use `http://api:8000` instead of `localhost`.

* **OpenAI embeddings fail**:

  * Make sure `OPENAI_API_KEY` is in `.env` and loaded in both `api` and `streamlit` containers.

* **Ports already in use**:

  * Update `docker-compose.yml` if `8000` or `8501` is occupied.

* **Vector store not found**:

  * Ensure `data/processed/vector_store` exists or re-run ingestion scripts.

* **RAG returns empty results**:

  * Make sure documents and synthetic data are ingested into Chroma.

---

## 🔧 Commands

* Build containers:

  ```bash
  docker-compose build
  ```

* Run containers:

  ```bash
  docker-compose up
  ```

* Stop containers:

  ```bash
  docker-compose down
  ```

* Re-run ingestion scripts:

  ```bash
  docker exec -it api-1 python src/etl/run_ingestion.py
  ```

---

## 💡 Notes

* Streamlit inside Docker listens on `0.0.0.0:8501` → access via `localhost:8501`.
* FastAPI listens on `0.0.0.0:8000` → Streamlit must call `http://api:8000` inside Docker network.
* Chroma persists data in `chroma_data` volume.

---

## 📝 License

MIT License © 2025 Rohan Verma
