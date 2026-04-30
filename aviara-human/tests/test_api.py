import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import API_KEY

client = TestClient(app)
headers = {"x-api-key": API_KEY}

lead = {
    "name": "John Doe",
    "email": "john@techcorp.com",
    "company": "TechCorp"
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_enrich_success():
    resp = client.post("/enrich", json=lead, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "linkedin_url" in data
    assert "company_size" in data
    assert "industry" in data


def test_enrich_bad_email():
    resp = client.post("/enrich", json={**lead, "email": "not-an-email"}, headers=headers)
    assert resp.status_code == 422


def test_enrich_no_auth():
    resp = client.post("/enrich", json=lead)
    assert resp.status_code == 422  # missing header


def test_enrich_wrong_key():
    resp = client.post("/enrich", json=lead, headers={"x-api-key": "wrong"})
    assert resp.status_code == 401


def test_classify_sales():
    resp = client.post(
        "/classify",
        json={"message": "I'm interested in learning more about your services"},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] in ["sales_enquiry", "demo_request"]
    assert 0 <= data["confidence"] <= 1


def test_classify_demo():
    resp = client.post(
        "/classify",
        json={"message": "Can I schedule a demo?"},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["intent"] == "demo_request"


def test_classify_pricing():
    resp = client.post(
        "/classify",
        json={"message": "What are your pricing plans?"},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["intent"] == "pricing_enquiry"


def test_classify_spam():
    resp = client.post(
        "/classify",
        json={"message": "!!!###$$$"},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["intent"] == "spam"
