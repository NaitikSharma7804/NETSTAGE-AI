"""
Human Review API Router.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from ai.schemas.diagnosis import HumanReviewRequest, HumanReviewResponse
from backend.services.review_service import ReviewService
from backend.database.repositories import HumanReviewRepository

router = APIRouter(prefix="", tags=["Human Review"])


@router.post("/review", response_model=HumanReviewResponse)
def submit_review(request: HumanReviewRequest, db: Session = Depends(get_db)):
    """
    Submits a human review for an AI diagnosis (ACCEPT, EDIT, REJECT).
    """
    try:
        return ReviewService.process_review(request, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review processing error: {str(e)}")


@router.get("/reviews")
def list_reviews(db: Session = Depends(get_db)):
    """Lists all historical human review logs."""
    return HumanReviewRepository.get_all(db)