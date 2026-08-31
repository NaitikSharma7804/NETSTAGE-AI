"""Pydantic request/response schemas for Cases."""

from typing import List
from pydantic import BaseModel, ConfigDict


class CaseBase(BaseModel):
    case_id: str
    symptom: str
    topology_note: str
    show_output: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: str
    dataset_status: str = "SAMPLE"


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CaseListResponse(BaseModel):
    total: int
    cases: List[CaseResponse]
