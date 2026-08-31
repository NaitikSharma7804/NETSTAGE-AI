"""Unit tests for Pydantic AI Response Schema Validation."""

import json
import pytest
from pydantic import ValidationError
from ai.response_validator import validate_ai_response, AIDiagnosisSchema


def test_valid_ai_response_validation():
    valid_json = json.dumps({
        "root_cause": "Subinterface GigabitEthernet0/0.30 administratively down",
        "confidence": 0.95,
        "osi_layer": "Layer 3",
        "evidence": ["show ip interface brief shows Gi0/0.30 down down"],
        "next_command": "show interface GigabitEthernet0/0.30",
        "fix_steps": ["interface GigabitEthernet0/0.30", "no shutdown"]
    })

    result = validate_ai_response(valid_json)
    assert isinstance(result, AIDiagnosisSchema)
    assert result.confidence == 0.95
    assert result.osi_layer == "Layer 3"
    assert len(result.fix_steps) == 2


def test_confidence_out_of_bounds_rejection():
    invalid_json = json.dumps({
        "root_cause": "Invalid confidence test",
        "confidence": 1.5,  # Invalid: > 1.0
        "osi_layer": "Layer 3",
        "evidence": ["Test evidence"],
        "next_command": "show ip route",
        "fix_steps": ["Fix step"]
    })

    with pytest.raises(ValidationError):
        validate_ai_response(invalid_json)


def test_missing_required_fields_rejection():
    malformed_json = json.dumps({
        "root_cause": "Missing fields test",
        "confidence": 0.8
        # missing osi_layer, evidence, next_command, fix_steps
    })

    with pytest.raises(ValidationError):
        validate_ai_response(malformed_json)
