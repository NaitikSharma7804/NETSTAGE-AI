"""Pydantic Schema Validator for AI Diagnosis Output."""

from typing import List
from pydantic import BaseModel, Field, field_validator


class AIDiagnosisSchema(BaseModel):
    """Pydantic model enforcing strict structure and constraints on AI diagnosis output."""
    
    root_cause: str = Field(
        ...,
        description="Concise description of the identified network fault"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 (completely uncertain) and 1.0 (certain)"
    )
    osi_layer: str = Field(
        ...,
        description="OSI Layer associated with the issue (Layer 1, Layer 2, Layer 3, Layer 4, Layer 7)"
    )
    evidence: List[str] = Field(
        ...,
        min_length=1,
        description="List of concrete evidence points extracted from show outputs and rules"
    )
    next_command: str = Field(
        ...,
        description="Recommended Cisco CLI show/verification command to execute next"
    )
    fix_steps: List[str] = Field(
        ...,
        min_length=1,
        description="Ordered list of Cisco CLI configuration commands or actions to fix the issue"
    )

    @field_validator("confidence")

    def check_confidence_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence score must be strictly between 0.0 and 1.0")
        return round(v, 2)

    @field_validator("osi_layer")

    def normalize_osi_layer(cls, v: str) -> str:
        valid_layers = ["Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 7"]
        v_clean = v.strip().title()
        if not v_clean.startswith("Layer "):
            if v_clean.isdigit():
                v_clean = f"Layer {v_clean}"
            elif "Physical" in v_clean:
                v_clean = "Layer 1"
            elif "Data Link" in v_clean:
                v_clean = "Layer 2"
            elif "Network" in v_clean:
                v_clean = "Layer 3"
            elif "Transport" in v_clean:
                v_clean = "Layer 4"
            elif "Application" in v_clean:
                v_clean = "Layer 7"
        if v_clean not in valid_layers:
            # Default fallback to Layer 3 if unrecognized string
            return "Layer 3"
        return v_clean


def validate_ai_response(raw_json_str: str) -> AIDiagnosisSchema:
    """Validates raw JSON string from LLM against Pydantic schema."""
    return AIDiagnosisSchema.model_validate_json(raw_json_str)
