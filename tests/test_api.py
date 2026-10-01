"""Integration tests for FastAPI backend endpoints."""

import pytest
from fastapi.testclient import TestClient
from api import storage
from api.main import app
from config.settings import settings

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test-state.sqlite3")
    with TestClient(app) as test_client:
        response = test_client.post("/api/auth/login", json={
            "email": settings.AUTH_USERNAME,
            "password": settings.AUTH_PASSWORD,
        })
        assert response.status_code == 200
        yield test_client

def test_login_protects_api_routes():
    unauthenticated = TestClient(app)
    assert unauthenticated.get("/api/health").status_code == 401

    invalid = unauthenticated.post("/api/auth/login", json={
        "email": settings.AUTH_USERNAME,
        "password": "incorrect-password",
    })
    assert invalid.status_code == 401

    valid = unauthenticated.post("/api/auth/login", json={
        "email": settings.AUTH_USERNAME,
        "password": settings.AUTH_PASSWORD,
    })
    assert valid.status_code == 200
    assert unauthenticated.get("/api/auth/me").json()["user"] == settings.AUTH_USERNAME

    unauthenticated.post("/api/auth/logout")
    assert unauthenticated.get("/api/auth/me").status_code == 401

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

def test_saved_queries_are_persisted(client):
    created = client.post("/api/saved-queries", json={"query": "Which suppliers are high risk?"})
    assert created.status_code == 201
    query_id = created.json()["id"]
    assert client.get("/api/saved-queries").json()[0]["query"] == "Which suppliers are high risk?"
    assert client.delete(f"/api/saved-queries/{query_id}").json() == {"deleted": True}

def test_incidents_can_be_acknowledged(client):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    incidents = response.json()
    assert incidents

    open_incident = next(item for item in incidents if item["status"] == "OPEN")
    acknowledged = client.post(f"/api/incidents/{open_incident['id']}/acknowledge")
    assert acknowledged.status_code == 200
    assert acknowledged.json()["status"] == "ACKNOWLEDGED"
    assert acknowledged.json()["acknowledged_by"] == settings.AUTH_USERNAME
