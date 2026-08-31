"""
End-to-End Human-in-the-Loop Workflow Integration Test.
BROKEN NETWORK -> DETERMINISTIC RULES -> AI INFERENCE -> EVIDENCE FUSION -> HUMAN REVIEW (ACCEPT/EDIT/REJECT) -> FIX -> VERIFICATION
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_full_troubleshoot_workflow_accept():
    # Step 1: Broken Network Case
    case_resp = client.get("/cases/NS-GW-001")
    assert case_resp.status_code == 200
    c_data = case_resp.json()

    # Step 2: Request Diagnosis
    diag_payload = {
        "case_id": c_data["case_id"],
        "symptom": c_data["symptom"],
        "topology_note": c_data["topology_note"],
        "show_outputs": c_data["show_outputs"]
    }
    diag_resp = client.post("/diagnose", json=diag_payload)
    assert diag_resp.status_code == 200
    diag_json = diag_resp.json()["diagnosis"]
    diag_id = diag_json["diagnosis_id"]

    # Step 3: Human Review - ACCEPT
    rev_payload = {
        "diagnosis_id": diag_id,
        "case_id": c_data["case_id"],
        "status": "ACCEPTED",
        "reviewer_name": "Senior Specialist",
        "reviewer_reason": "Verified gateway subnet anomaly."
    }
    rev_resp = client.post("/review", json=rev_payload)
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "ACCEPTED"

    # Step 4: Fix Applied in Packet Tracer & Verified
    verif_payload = {
        "diagnosis_id": diag_id,
        "case_id": c_data["case_id"],
        "status": "PASS",
        "verification_command": "ping 10.1.10.1",
        "verification_output": "Reply from 10.1.10.1: bytes=32 time<1ms TTL=255 (0% loss)"
    }
    verif_resp = client.post("/verify", json=verif_payload)
    assert verif_resp.status_code == 200
    assert verif_resp.json()["status"] == "PASS"


def test_full_troubleshoot_workflow_human_correction_edit():
    # Demonstrates Responsible AI Human Correction flow
    diag_payload = {
        "case_id": "NS-DNS-004",
        "symptom": "Public internet FQDN resolution fails",
        "topology_note": "Internal DNS -> R1 -> Public DNS 1.1.1.1",
        "show_outputs": "show access-lists OUTSIDE-IN\n10 permit tcp any host 10.0.0.53 eq domain\n30 deny ip any any (1420 matches)"
    }
    # Simulate misdiagnosis
    diag_resp = client.post("/diagnose?simulate_misdiagnosis=true", json=diag_payload)
    assert diag_resp.status_code == 200
    diag_json = diag_resp.json()["diagnosis"]
    diag_id = diag_json["diagnosis_id"]

    # Human detects AI error and EDITS diagnosis
    rev_payload = {
        "diagnosis_id": diag_id,
        "case_id": "NS-DNS-004",
        "status": "EDITED",
        "reviewer_name": "Lead Network Architect",
        "corrected_diagnosis": "Firewall ACL 'OUTSIDE-IN' permits TCP 53 but drops UDP 53 return DNS traffic.",
        "reviewer_reason": "Show access-lists showed rule 10 only permitted TCP; UDP queries hit deny rule 30."
    }
    rev_resp = client.post("/review", json=rev_payload)
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "EDITED"
    assert "Firewall ACL" in rev_resp.json()["corrected_diagnosis"]


def test_reject_requires_a_human_correction_and_reason():
    response = client.post("/review", json={
        "diagnosis_id": "DIAG-TEST-REJECT",
        "case_id": "NS-ACL-001",
        "status": "REJECTED",
        "reviewer_reason": "The evidence contradicts the proposed root cause."
    })
    assert response.status_code == 400
    assert "corrected diagnosis" in response.json()["detail"].lower()


def test_reject_with_correction_is_recorded():
    response = client.post("/review", json={
        "diagnosis_id": "DIAG-TEST-REJECT-VALID",
        "case_id": "NS-ACL-001",
        "status": "REJECTED",
        "corrected_diagnosis": "ACL deny rule blocks the required traffic.",
        "reviewer_reason": "The submitted access-list evidence records deny matches for the flow."
    })
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"
