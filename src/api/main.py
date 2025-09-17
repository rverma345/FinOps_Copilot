# api/main.py
import logging
import time
import uuid
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

from src.analytics.kpis import six_month_trend, top_n_cost_drivers, monthly_cost_by_service
from src.analytics import recommendations
from src.ai import rag_engine

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="FinOps Copilot API", description="API for FinOps KPIs, Recommendations, and RAG-powered Q&A")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request ID & latency
@app.middleware("http")
async def add_request_id_and_latency(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    request.state.request_id = request_id
    logger.info(f"[{request_id}] Start {request.method} {request.url}")

    response = await call_next(request)

    duration = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)
    logger.info(f"[{request_id}] End {request.method} {request.url} - {response.status_code} - {duration:.3f}s")
    return response


# ---------------- Models ---------------- #
class QuestionRequest(BaseModel):
    question: str
    month: Optional[str] = None

class KPIResponse(BaseModel):
    six_month_trend: List[Dict[str, Any]]
    top_5_cost_drivers: List[Dict[str, Any]]
    monthly_cost_by_service: List[Dict[str, Any]]

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    data_type: str
    structured_data: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    recommendation_type: str
    details: List[Dict[str, Any]]

class APIResponse(BaseModel):
    status: str
    data: Optional[Union[KPIResponse, AskResponse, RecommendationResponse, Dict[str, Any]]] = None
    error: Optional[str] = None


#Endpoints 
@app.get("/kpis", response_model=APIResponse)
def get_kpis():
    try:
        six_month_df = six_month_trend()
        if six_month_df.empty:
            raise HTTPException(status_code=404, detail="No data available")

        latest_month = six_month_df["invoice_month"].iloc[-1]
        response = KPIResponse(
            six_month_trend=six_month_df.to_dict("records"),
            top_5_cost_drivers=top_n_cost_drivers(latest_month, 5).to_dict("records"),
            monthly_cost_by_service=monthly_cost_by_service(latest_month).to_dict("records"),
        )
        return APIResponse(status="success", data=response)
    except Exception as e:
        logger.exception("Error in /kpis")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=APIResponse)
def ask_question(request: QuestionRequest):
    try:
        # --- Validate empty question ---
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        month = request.month or "2025-05"
        answer, retrieved_docs = rag_engine.get_answer(request.question)

        structured_data = {"documents_retrieved": len(retrieved_docs)}
        sources = [doc.page_content for doc in retrieved_docs]

        response = AskResponse(
            answer=answer,
            sources=sources,
            data_type="rag",
            structured_data=structured_data
        )
        return APIResponse(status="success", data=response)
    except HTTPException:
        # Pass through HTTP exceptions (like our 400)
        raise
    except Exception as e:
        logger.exception("Error in /ask")
        raise HTTPException(status_code=500, detail=str(e))@app.post("/ask", response_model=APIResponse)


@app.get("/recommendations", response_model=APIResponse)
def get_recommendations(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        idle_resources = recommendations.find_idle_resources(month=month)
        response = RecommendationResponse(
            recommendation_type="Idle Resources",
            details=idle_resources.to_dict("records")
        )
        return APIResponse(status="success", data=response)
    except Exception as e:
        logger.exception("Error in /recommendations")
        raise HTTPException(status_code=500, detail=str(e))
