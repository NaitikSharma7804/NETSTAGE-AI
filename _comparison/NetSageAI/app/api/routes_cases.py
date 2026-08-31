"""FastAPI Router for Networking Cases."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from app.schemas.case_schema import CaseResponse, CaseListResponse, CaseCreate
from app.services import case_service

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.get("", response_model=List[CaseResponse])
def list_cases(
    concept: Optional[str] = Query(None, description="Filter cases by concept (VLAN, Routing, DHCP, etc.)"),
    severity: Optional[str] = Query(None, description="Filter cases by severity (High, Medium, Low)"),
    db: Session = Depends(get_db)
):
    """Retrieves all Cisco troubleshooting cases with optional filtering."""
    cases = case_service.get_all_cases(db, concept=concept, severity=severity)
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Retrieves a single case by its unique string case_id (e.g. CASE-001)."""
    case_obj = case_service.get_case_by_id(db, case_id)
    if not case_obj:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
    return case_obj


@router.post("", response_model=CaseResponse, status_code=201)
def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    """Creates a new networking troubleshooting case."""
    existing = case_service.get_case_by_id(db, case_data.case_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Case ID '{case_data.case_id}' already exists.")
    return case_service.create_case(db, case_data)
