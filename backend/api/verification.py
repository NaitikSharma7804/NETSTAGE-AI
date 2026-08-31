"""
Fix Verification API Router.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from ai.schemas.diagnosis import VerificationRequest, VerificationResponse
from backend.services.verification_service import VerificationService
from backend.database.repositories import VerificationRepository

router = APIRouter(prefix="", tags=["Verification"])


@router.post("/verify", response_model=VerificationResponse)
def submit_verification(request: VerificationRequest, db: Session = Depends(get_db)):
    """
    Records outcome of a manual Cisco fix verification in Packet Tracer (PASS / FAIL).
    """
    try:
        return VerificationService.process_verification(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification recording error: {str(e)}")


@router.get("/verifications")
def list_verifications(db: Session = Depends(get_db)):
    """Lists all verification records."""
    return VerificationRepository.get_all(db)