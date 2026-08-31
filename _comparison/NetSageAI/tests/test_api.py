"""Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from database.database import Base, engine
from database.seed import seed_database
from app.main import app


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensures database tables are created and seeded before tests run."""
    Base.metadata.create_all(bind=engine)
    seed_database()


client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_get_cases_endpoint():
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)
    assert len(cases) >= 30


def test_get_single_case_endpoint():
    response = client.get("/api/cases/CASE-001")
    assert response.status_code == 200
    case_obj = response.json()
    assert case_obj["case_id"] == "CASE-001"


def test_run_diagnosis_endpoint():
    payload = {
        "case_id": "CASE-001",
        "symptom": "PC receives IP address but cannot reach server",
        "topology_note": "PC in VLAN 30 connected through switch to router",
        "show_output": "Gi0/0.30 is down. switchport access vlan 30 configured on Switch port Fa0/3.",
        "concept": "Routing"
    }
    response = client.post("/api/diagnose", json=payload)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert "rule_results" in data
    assert "ai_diagnosis" in data
    assert data["ai_diagnosis"]["root_cause"] != ""
    assert 0.0 <= data["ai_diagnosis"]["confidence"] <= 1.0


def test_human_review_workflow_endpoint():
    # 1. Run diagnosis first
    payload = {
        "symptom": "Interface down test",
        "show_output": "GigabitEthernet0/1 is administratively down down"
    }
    diag_resp = client.post("/api/diagnose", json=payload)
    assert diag_resp.status_code == 200
    diag_id = diag_resp.json()["id"]

    # 2. Submit human review
    review_payload = {
        "diagnosis_id": diag_id,
        "status": "Accepted",
        "final_human_diagnosis": "Interface GigabitEthernet0/1 administratively down",
        "reviewer_notes": "Verified via CLI show output",
        "reason": "Correct AI identification",
        "lesson": "Always check line protocol status"
    }
    rev_resp = client.post("/api/reviews", json=review_payload)
    assert rev_resp.status_code == 201
    rev_data = rev_resp.json()
    assert rev_data["status"] == "Accepted"
    assert rev_data["diagnosis_id"] == diag_id


def test_analytics_endpoint():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_cases" in data
    assert "agreement_rate" in data


def test_responsible_ai_endpoint():
    response = client.get("/api/responsible-ai")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert len(logs) >= 5
