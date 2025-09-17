# tests/test_api.py
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api.main import app

client = TestClient(app)

# -----------------------------
# /kpis endpoint tests
# -----------------------------
@patch('src.analytics.kpis.six_month_trend')
@patch('src.analytics.kpis.top_n_cost_drivers')
@patch('src.analytics.kpis.monthly_cost_by_service')
def test_get_kpis_success(mock_monthly, mock_top, mock_trend):
    """Test the /kpis endpoint with mocked KPI data."""
    mock_trend.return_value = pd.DataFrame({'invoice_month': ['2024-05'], 'total_cost': [100.0]})
    mock_top.return_value = pd.DataFrame({'resource_id': ['i-123'], 'total_cost': [50.0]})
    mock_monthly.return_value = pd.DataFrame({'service': ['Amazon EC2'], 'total_cost': [100.0]})

    response = client.get("/kpis")
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert 'six_month_trend' in data['data']
    assert 'top_5_cost_drivers' in data['data']
    assert 'monthly_cost_by_service' in data['data']

# -----------------------------
# /ask endpoint tests
# -----------------------------
@patch('src.ai.rag_engine.get_answer')
def test_ask_question_success(mock_get_answer):
    """Test the /ask endpoint with a valid question."""
    class MockDoc:
        def __init__(self, content):
            self.page_content = content

    mock_get_answer.return_value = ("A mock answer from the AI.", [MockDoc("Source 1"), MockDoc("Source 2")])

    response = client.post("/ask", json={"question": "Why did my spend increase?"})
    assert response.status_code == 200
    data = response.json()
    assert data['data']['answer'] == "A mock answer from the AI."
    assert data['data']['sources'] == ["Source 1", "Source 2"]

def test_ask_question_empty_body():
    """Test /ask with empty JSON body."""
    response = client.post("/ask", json={})
    assert response.status_code == 422  # FastAPI validation error

def test_ask_question_empty_string():
    """Test /ask with empty question string."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400

# /recommendations endpoint tests

@patch('src.analytics.recommendations.find_idle_resources')
def test_get_recommendations_success(mock_find_idle):
    """Test /recommendations endpoint."""
    mock_find_idle.return_value = pd.DataFrame({
        'resource_id': ['i-123'],
        'total_cost': [5.0],
        'tags_json': ['{}'],
        'recommendation': ['Consider terminating it.']
    })

    response = client.get("/recommendations?month=2024-05")
    assert response.status_code == 200
    data = response.json()
    assert data['data']['recommendation_type'] == 'Idle Resources'
    assert len(data['data']['details']) == 1
    assert data['data']['details'][0]['resource_id'] == 'i-123'

def test_recommendations_invalid_month():
    """Test /recommendations with invalid month format."""
    response = client.get("/recommendations?month=202405")
    assert response.status_code == 422
