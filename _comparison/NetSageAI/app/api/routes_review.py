"""FastAPI Router for Human Reviews, Analytics, and Responsible AI logging."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ResponsibleAILogResponse, AnalyticsSummary
from app.services import review_service

router = APIRouter(prefix="/api", tags=["Reviews & Analytics"])


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def submit_human_review(review_data: ReviewCreate, db: Session = Depends(get_db)):
    """Submits mandatory human review (Accepted, Edited, Rejected) for an AI diagnosis."""
    if review_data.status not in ["Accepted", "Edited", "Rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'Accepted', 'Edited', or 'Rejected'.")

    review_obj = review_service.create_human_review(db, review_data)
    return review_obj


@router.get("/reviews", response_model=List[ReviewResponse])
def list_human_reviews(db: Session = Depends(get_db)):
    """Retrieves all human review history records."""
    return review_service.get_all_reviews(db)


@router.get("/analytics", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Computes system-wide analytics on cases, AI vs Human agreement, and issue severities."""
    return review_service.calculate_analytics_summary(db)


@router.get("/responsible-ai", response_model=List[ResponsibleAILogResponse])
def get_responsible_ai_logs():
    """Retrieves Responsible AI audit trail of human corrections and AI failure lessons."""
    logs = review_service.get_responsible_ai_logs()
    return [
        ResponsibleAILogResponse(
            case_id=row.get("case_id", ""),
            ai_diagnosis=row.get("ai_diagnosis", ""),
            human_decision=row.get("human_decision", ""),
            correction=row.get("correction", ""),
            reason=row.get("reason", ""),
            lesson=row.get("lesson", ""),
            record_type=row.get("record_type", "DEVELOPMENT_EXAMPLE")
        )
        for row in logs
    ]
