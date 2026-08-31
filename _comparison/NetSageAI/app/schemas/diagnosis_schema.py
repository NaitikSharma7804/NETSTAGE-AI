"""Pydantic request/response schemas for Diagnosis."""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DiagnosisRequest(BaseModel):
    case_id: Optional[str] = None
    symptom: str = Field(..., min_length=3)
    topology_note: Optional[str] = ""
    show_output: str = Field(..., min_length=3)
    concept: Optional[str] = None


class RuleFindingSchema(BaseModel):
    rule: str
    status: str
    severity: str
    message: str


class AIDiagnosisOutput(BaseModel):
    root_cause: str
    confidence: float
    osi_layer: str
    evidence: List[str]
    next_command: str
    fix_steps: List[str]


class DiagnosisResponse(BaseModel):
    id: int
    case_id: Optional[str] = None
    symptom: str
    topology_note: Optional[str] = ""
    show_output: str
    rule_results: List[Dict[str, Any]]
    ai_diagnosis: AIDiagnosisOutput
    review_status: str = "Pending Review"
    dataset_status: str = "SAMPLE"
    ai_mode: str = "mock"
    evidence_grounding_status: str = "Unverified"
    grounded_evidence: List[Dict[str, Any]] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
