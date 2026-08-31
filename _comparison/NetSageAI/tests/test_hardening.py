"""Automated Unit & Integration Tests for NetSage AI Post-Audit Hardening Features."""

import pytest
from fastapi.testclient import TestClient
from database.database import Base, engine
from database.seed import seed_database
from app.main import app
from ai.evidence_grounding import evaluate_evidence_grounding
from ai.provider import get_llm_provider, MockLLMProvider


@pytest.fixture(autouse=True)
def setup_db():
    """Seeds database for hardening tests."""
    Base.metadata.create_all(bind=engine)
    seed_database()


client = TestClient(app)


def test_health_reports_actual_provider():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "mode" in data
    assert data["mode"] in ["live", "offline"]
    provider = get_llm_provider()
    assert data["llm_provider"] == provider.provider_name
    assert data["mode"] == provider.mode


def test_mock_mode_visible():
    provider = MockLLMProvider()
    assert provider.provider_name == "mock"
    assert provider.mode == "offline"


def test_new_diagnosis_is_pending_review():
    payload = {
        "symptom": "Host cannot reach gateway",
        "show_output": "GigabitEthernet0/0 is administratively down down"
    }
    response = client.post("/api/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["review_status"] == "Pending Review"
    assert data["dataset_status"] == "SAMPLE"


def test_accept_review_changes_status():
    diag_resp = client.post("/api/diagnose", json={"symptom": "Gateway ping fail", "show_output": "Gi0/0 down down"})
    diag_id = diag_resp.json()["id"]

    rev_payload = {
        "diagnosis_id": diag_id,
        "status": "Accepted",
        "final_human_diagnosis": "Gi0/0 down down"
    }
    rev_resp = client.post("/api/reviews", json=rev_payload)
    assert rev_resp.status_code == 201

    get_resp = client.get(f"/api/diagnoses/{diag_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["review_status"] == "Accepted"


def test_edit_review_changes_status():
    diag_resp = client.post("/api/diagnose", json={"symptom": "VLAN issue", "show_output": "switchport access vlan 1"})
    diag_id = diag_resp.json()["id"]

    rev_payload = {
        "diagnosis_id": diag_id,
        "status": "Edited",
        "final_human_diagnosis": "Wrong access VLAN assigned"
    }
    rev_resp = client.post("/api/reviews", json=rev_payload)
    assert rev_resp.status_code == 201

    get_resp = client.get(f"/api/diagnoses/{diag_id}")
    assert get_resp.json()["review_status"] == "Edited"


def test_reject_review_changes_status():
    diag_resp = client.post("/api/diagnose", json={"symptom": "Route issue", "show_output": "ip route 0.0.0.0"})
    diag_id = diag_resp.json()["id"]

    rev_payload = {
        "diagnosis_id": diag_id,
        "status": "Rejected",
        "final_human_diagnosis": "Incorrect AI route assumption"
    }
    rev_resp = client.post("/api/reviews", json=rev_payload)
    assert rev_resp.status_code == 201

    get_resp = client.get(f"/api/diagnoses/{diag_id}")
    assert get_resp.json()["review_status"] == "Rejected"


def test_evidence_grounding_verified():
    evidence_list = ["GigabitEthernet0/0 is administratively down"]
    symptom = "Interface down"
    topology = "R1 Gi0/0"
    show_output = "GigabitEthernet0/0 is administratively down down"
    rules = [{"rule": "interface_admin_down", "status": "FAIL", "severity": "HIGH", "message": "Gi0/0 admin down"}]

    res = evaluate_evidence_grounding(evidence_list, symptom, topology, show_output, rules)
    assert res["status"] == "Verified"
    assert len(res["grounded_items"]) == 1
    assert res["grounded_items"][0]["grounded"] is True


def test_evidence_grounding_unverified():
    evidence_list = ["Router CPU usage exceeded 99% due to BGP update storm"]
    symptom = "Slow ping"
    topology = "Simple link"
    show_output = "GigabitEthernet0/0 is up up"
    rules = []

    res = evaluate_evidence_grounding(evidence_list, symptom, topology, show_output, rules)
    assert res["status"] == "Unverified"
    assert res["grounded_items"][0]["grounded"] is False


def test_sample_dataset_status():
    response = client.get("/api/cases/CASE-001")
    assert response.status_code == 200
    assert response.json()["dataset_status"] == "SAMPLE"


def test_real_review_logging():
    diag_resp = client.post("/api/diagnose", json={"symptom": "Log test", "show_output": "Gi0/0 down"})
    diag_id = diag_resp.json()["id"]

    rev_resp = client.post("/api/reviews", json={
        "diagnosis_id": diag_id,
        "status": "Edited",
        "final_human_diagnosis": "Real team correction test",
        "reason": "AI missed subinterface state"
    })
    assert rev_resp.status_code == 201
    assert rev_resp.json()["record_type"] == "REAL_TEAM_REVIEW"


def test_agreement_rate_uses_reviewed_cases_only():
    analytics_resp = client.get("/api/analytics")
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert "pending_review_count" in data
    assert "agreement_rate" in data
    assert "real_human_corrections" in data
