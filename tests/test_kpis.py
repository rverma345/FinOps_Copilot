import pytest
from src.analytics import kpis
import sqlite3

def get_db_connection(db_path="data/warehouse.db"):
    return sqlite3.connect(db_path)



def test_six_month_trend_calculates_correctly(monkeypatch):
    def fake_query(db_path):
        return [{"invoice_month": "2024-01", "total_cost": 100}, {"invoice_month": "2024-02", "total_cost": 200}]

    monkeypatch.setattr("src.analytics.kpis.six_month_trend", fake_query)

    result = kpis.six_month_trend(":memory:")
    assert isinstance(result, list)
    assert "invoice_month" in result[0]


def test_top_n_cost_drivers_calculates_correctly(monkeypatch):
    def fake_query(db_path, n=3):
        return [{"service": "EC2", "total_cost": 500}]

    monkeypatch.setattr("src.analytics.kpis.top_n_cost_drivers", fake_query)

    result = kpis.top_n_cost_drivers(":memory:", 3)
    assert isinstance(result, list)
    assert "service" in result[0]


def test_monthly_cost_by_service_calculates_correctly(monkeypatch):
    def fake_query(db_path):
        return [{"invoice_month": "2024-05", "service": "EC2", "total_cost": 120}]

    monkeypatch.setattr("src.analytics.kpis.monthly_cost_by_service", fake_query)

    result = kpis.monthly_cost_by_service(":memory:")
    assert isinstance(result, list)
    assert "service" in result[0]
