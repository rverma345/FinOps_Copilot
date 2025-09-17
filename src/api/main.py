# api/main.py
import logging
import time
import uuid
import re
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from src.analytics.kpis import six_month_trend, top_n_cost_drivers, monthly_cost_by_service
from src.analytics import recommendations
from src.ai import rag_engine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FinOps Copilot API",
    description="API for FinOps KPIs, recommendations, and RAG-powered Q&A."
)

# Allow CORS (for Streamlit/frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request ID and latency
@app.middleware("http")
async def add_request_id_and_latency(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Start request {request.method} {request.url}")
    request.state.request_id = request_id

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(f"[{request_id}] End request {request.method} {request.url} - status {response.status_code} - duration {duration:.3f}s")
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)
    return response

# Request / Response Models
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

class RecommendationResponse(BaseModel):
    recommendation_type: str
    details: List[Dict[str, Any]]

class APIResponse(BaseModel):
    status: str
    data: Optional[Union[KPIResponse, AskResponse, RecommendationResponse, Dict[str, Any]]] = None
    error: Optional[str] = None

# KPI endpoint
@app.get("/kpis", response_model=APIResponse, summary="Get core FinOps KPIs")
def get_kpis():
    try:
        six_month_df = six_month_trend()
        if six_month_df.empty:
            raise HTTPException(status_code=404, detail="No data available to compute KPIs.")

        latest_month = six_month_df['invoice_month'].iloc[-1]

        response = KPIResponse(
            six_month_trend=six_month_df.to_dict('records'),
            top_5_cost_drivers=top_n_cost_drivers(latest_month, 5).to_dict('records'),
            monthly_cost_by_service=monthly_cost_by_service(latest_month).to_dict('records')
        )
        return APIResponse(status="success", data=response)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Error in /kpis")
        raise HTTPException(status_code=500, detail="Failed to compute KPIs.")

# Ask endpoint
@app.post("/ask", response_model=APIResponse, summary="Ask a natural language question")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        start_time = time.time()
        answer, retrieved_docs = rag_engine.get_answer(request.question)
        elapsed = time.time() - start_time

        logger.info(f"RAG query processed in {elapsed:.3f}s - retrieved {len(retrieved_docs)} documents")

        response = AskResponse(
            answer=answer,
            sources=[doc.page_content for doc in retrieved_docs]
        )
        return APIResponse(status="success", data=response)
    except Exception as e:
        logger.exception("Error in /ask")
        raise HTTPException(status_code=500, detail="Failed to process question.")

# Recommendations endpoint
@app.get("/recommendations", response_model=APIResponse)
def get_recommendations(month: str = Query(...)):
    if not re.match(r'^\d{4}-\d{2}$', month):
        raise HTTPException(status_code=422, detail="Month must be in YYYY-MM format")
    
    try:
        idle_resources = recommendations.find_idle_resources(month=month)
        response = RecommendationResponse(
            recommendation_type="Idle Resources",
            details=idle_resources.to_dict('records')
        )
        return APIResponse(status="success", data=response)
    except Exception as e:
        logger.exception("Error in /recommendations")
        raise HTTPException(status_code=500, detail=str(e))
