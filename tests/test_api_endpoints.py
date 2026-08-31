"""
Integration Tests for FastAPI Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_list_cases_endpoint():
    resp = client.get("/cases")
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) >= 30


def test_get_single_case_endpoint():
    resp = client.get("/cases/NS-VLAN-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["case_id"] == "NS-VLAN-001"
    assert data["concept"] == "VLAN"


def test_diagnose_endpoint():
    payload = {
        "case_id": "NS-ACL-001",
        "symptom": "PC in VLAN 30 cannot reach server in VLAN 10",
        "topology_note": "PC-30 -> SW1 -> R1 -> Server-10",
        "show_outputs": "show access-lists BLOCK-OLD\n10 permit 192.168.20.0 0.0.0.255\nimplicit deny matches: 128",
        "target_ip": "192.168.10.10"
    }
    resp = client.post("/diagnose", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "diagnosis" in data
    assert "rule_engine" in data
    assert "evidence_fusion" in data
    assert data["diagnosis"]["case_id"] == "NS-ACL-001"
    assert data["evidence_fusion"]["target_ip_assessment"]["target_ip"] == "192.168.10.10"


def test_target_ip_assessment_endpoint_is_safe_and_validates_input():
    resp = client.get("/ip-assessment/192.168.30.10")
    assert resp.status_code == 200
    assert resp.json()["is_unicast_target"] is True
    assert "No ping" in resp.json()["safety_note"]
    assert client.get("/ip-assessment/not-an-ip").status_code == 400


def test_human_review_endpoints():
    # 1. Accept
    payload = {
        "diagnosis_id": "DIAG-TEST-ACCEPT",
        "case_id": "NS-VLAN-001",
        "status": "ACCEPTED",
        "reviewer_name": "Senior Specialist",
        "reviewer_reason": "Verified against show vlan brief"
    }
    resp = client.post("/review", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACCEPTED"

    # 2. List reviews
    resp_list = client.get("/reviews")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1


def test_fix_verification_endpoint():
    payload = {
        "diagnosis_id": "DIAG-TEST-VERIF",
        "case_id": "NS-VLAN-001",
        "status": "PASS",
        "verification_command": "ping 192.168.20.1",
        "verification_output": "5/5 success rate is 100 percent"
    }
    resp = client.post("/verify", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "PASS"


def test_analytics_and_responsible_ai_endpoints():
    resp_a = client.get("/analytics")
    assert resp_a.status_code == 200
    assert "metrics" in resp_a.json()

    resp_rai = client.get("/responsible-ai")
    assert resp_rai.status_code == 200
    assert "corrected_cases" in resp_rai.json()
    assert len(resp_rai.json()["corrected_cases"]) >= 5
