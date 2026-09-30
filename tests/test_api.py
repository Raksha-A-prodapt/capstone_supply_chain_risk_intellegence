"""Integration tests for FastAPI backend endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["dataset_records"] >= 100_000

def test_api_suppliers(client):
    res = client.get("/api/suppliers")
    assert res.status_code == 200
    suppliers = res.json()
    assert len(suppliers) == 25
    assert "supplier_risk_score" in suppliers[0]

def test_api_query(client):
    res = client.post("/api/query", json={"query": "Which suppliers have the highest delivery risk?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "answer" in data
    assert "guardrails" in data
    assert "agent_trace" in data

def test_api_simulate(client):
    res = client.post("/api/simulate", json={"supplier_id": "SUP-023", "delay_days": 7})
    assert res.status_code == 200
    data = res.json()
    assert data["simulation_type"] == "WHAT_IF_SUPPLIER_DISRUPTION"
    assert data["affected_products_count"] > 0
    assert "estimated_financial_exposure_usd" in data
