# backend/app/tests/test_engine.py
from fastapi.testclient import TestClient
from ..main import app   # ← relative import from the parent package

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_engine_run():
    r = client.post(
        "/api/engine/run",
        json={"text": "OAuth 2.0 flows with GraphQL", "phase": "prepublish"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "recommended" in data and "external" in data
