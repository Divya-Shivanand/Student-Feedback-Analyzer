# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_submit_and_stats():
    payload = {"feedback":"This course is excellent and well structured."}
    r = client.post("/feedback", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "sentiment" in body
    assert "keywords" in body

    r2 = client.get("/stats")
    assert r2.status_code == 200
    stats = r2.json()
    assert "total_feedbacks" in stats
