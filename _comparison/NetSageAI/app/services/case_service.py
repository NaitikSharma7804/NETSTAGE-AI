"""Business logic service for managing networking cases."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.case import CaseModel
from app.schemas.case_schema import CaseCreate


def get_all_cases(db: Session, concept: Optional[str] = None, severity: Optional[str] = None) -> List[CaseModel]:
    """Retrieves all cases, optionally filtered by concept or severity."""
    query = db.query(CaseModel)
    if concept:
        query = query.filter(CaseModel.concept == concept)
    if severity:
        query = query.filter(CaseModel.severity == severity)
    return query.all()


def get_case_by_id(db: Session, case_id: str) -> Optional[CaseModel]:
    """Retrieves a single case by case_id string (e.g., CASE-001)."""
    return db.query(CaseModel).filter(CaseModel.case_id == case_id).first()


def create_case(db: Session, case_data: CaseCreate) -> CaseModel:
    """Creates a new case in database."""
    db_case = CaseModel(**case_data.model_dump())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case
