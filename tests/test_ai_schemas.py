"""
Unit Tests for Pydantic AI and HITL Schemas.
"""

import pytest
from pydantic import ValidationError
from ai.schemas.diagnosis import (
    ConfidenceLevel,
    DiagnosisRequest,
    DiagnosisResponse,
    EvidenceItem,
    HumanReviewRequest,
    ReviewStatus,
    VerificationRequest,
    VerificationStatus
)


def test_valid_diagnosis_schema():
    diag = DiagnosisResponse(
        diagnosis_id="DIAG-TEST-001",
        case_id="NS-ACL-001",
        root_cause="Outbound ACL implicit deny blocks VLAN 30",
        confidence=ConfidenceLevel.HIGH,
        osi_layer="Layer 3 (Network)",
        affected_component="R1 Gi0/0.10",
        evidence=[
            EvidenceItem(
                source="show access-lists",
                observation="implicit deny matches 128",
                relevance="Proves traffic drop"
            )
        ],
        next_command="show access-lists",
        fix_steps=["permit 192.168.30.0 0.0.0.255"],
        alternative_causes=["Server offline"]
    )
    assert diag.confidence == ConfidenceLevel.HIGH
    assert len(diag.evidence) == 1
    assert "NetSage AI" in diag.ai_disclaimer


def test_invalid_confidence_schema():
    with pytest.raises(ValidationError):
        DiagnosisResponse(
            diagnosis_id="DIAG-ERR",
            root_cause="Some issue",
            confidence="absolute_certainty",  # invalid
            osi_layer="Layer 3",
            affected_component="R1",
            next_command="show ip route"
        )


def test_target_ip_is_normalized_and_invalid_values_rejected():
    request = DiagnosisRequest(
        symptom="Host cannot reach its gateway",
        show_outputs="show ip interface brief",
        target_ip="192.168.1.10"
    )
    assert request.target_ip == "192.168.1.10"

    with pytest.raises(ValidationError):
        DiagnosisRequest(symptom="Host unreachable", show_outputs="show ip route", target_ip="not-an-ip")


def test_human_review_request_valid():
    rev = HumanReviewRequest(
        diagnosis_id="DIAG-TEST-001",
        status=ReviewStatus.ACCEPTED,
        reviewer_name="Alex Morgan",
        reviewer_reason="Accurate"
    )
    assert rev.status == ReviewStatus.ACCEPTED


def test_verification_request_valid():
    verif = VerificationRequest(
        diagnosis_id="DIAG-TEST-001",
        status=VerificationStatus.PASS,
        verification_command="ping 192.168.10.50",
        verification_output="5/5 success"
    )
    assert verif.status == VerificationStatus.PASS
