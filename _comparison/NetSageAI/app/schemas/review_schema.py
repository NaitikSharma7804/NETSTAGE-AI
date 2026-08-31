"""Pydantic request/response schemas for Human Reviews and Analytics."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    diagnosis_id: int
    case_id: Optional[str] = None
    status: str = Field(..., description="Accepted, Edited, or Rejected")
    reviewer_notes: Optional[str] = ""
    final_human_diagnosis: str
    reason: Optional[str] = ""
    lesson: Optional[str] = ""


class ReviewResponse(BaseModel):
    id: int
    diagnosis_id: int
    case_id: Optional[str] = None
    status: str
    reviewer_notes: Optional[str] = ""
    original_ai_response: str
    final_human_diagnosis: str
    reason: Optional[str] = ""
    lesson: Optional[str] = ""
    record_type: str = "REAL_TEAM_REVIEW"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponsibleAILogResponse(BaseModel):
    case_id: str
    ai_diagnosis: str
    human_decision: str
    correction: str
    reason: str
    lesson: str
    record_type: str = "DEVELOPMENT_EXAMPLE"


class AnalyticsSummary(BaseModel):
    total_cases: int
    diagnoses_run: int
    pending_review_count: int
    accepted_count: int
    edited_count: int
    rejected_count: int
    agreement_rate: float
    real_human_corrections: int
    high_severity_count: int
    by_concept: Dict[str, int]
    by_severity: Dict[str, int]
    by_osi_layer: Dict[str, int]
