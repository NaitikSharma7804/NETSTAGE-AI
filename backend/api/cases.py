"""
Cases API Router.
"""

import csv
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.case import CaseModel
from backend.database.repositories import CaseRepository

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("")
def list_cases(
    concept: Optional[str] = None,
    severity: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lists all troubleshooting cases with optional filtering."""
    query = db.query(CaseModel)
    if concept:
        query = query.filter(CaseModel.concept == concept)
    if severity:
        query = query.filter(CaseModel.severity == severity)
    if difficulty:
        query = query.filter(CaseModel.difficulty == difficulty)

    cases = query.limit(limit).all()
    if not cases and os.path.exists("data/cases.csv"):
        # Read directly from canonical CSV
        results = []
        with open("data/cases.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if concept and row.get("concept") != concept:
                    continue
                if severity and row.get("severity") != severity:
                    continue
                if difficulty and row.get("difficulty") != difficulty:
                    continue
                results.append(row)
        return results[:limit]

    return cases


@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Retrieves a single troubleshooting case by ID."""
    case = CaseRepository.get_by_case_id(db, case_id)
    if not case and os.path.exists("data/cases.csv"):
        with open("data/cases.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("case_id") == case_id:
                    return row
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
    return case


@router.post("")
def create_case(case_data: dict, db: Session = Depends(get_db)):
    """Creates a new custom troubleshooting case."""
    required = ["case_id", "title", "symptom", "show_outputs", "expected_fault", "concept"]
    for r in required:
        if r not in case_data or not str(case_data[r]).strip():
            raise HTTPException(status_code=400, detail=f"Missing required field '{r}'.")

    existing = CaseRepository.get_by_case_id(db, case_data["case_id"])
    if existing:
        raise HTTPException(status_code=409, detail=f"Case ID '{case_data['case_id']}' already exists.")

    new_case = CaseRepository.create(db, case_data)
    return new_case