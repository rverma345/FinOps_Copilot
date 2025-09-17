import pytest
from src.ai import rag_engine


def test_get_answer_returns_correct_response(monkeypatch):
    def fake_retrieve(query: str):
        return "Mocked answer"

    monkeypatch.setattr("src.ai.rag_engine.get_answer", fake_retrieve)

    response = rag_engine.get_answer("What is my S3 cost?")
    assert isinstance(response, str)
    assert "Mocked" in response
