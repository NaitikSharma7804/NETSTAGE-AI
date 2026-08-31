"""
Human Review Service.
Records ACCEPT, EDIT, and REJECT actions with mandatory rationale tracking.
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session
from ai.schemas.diagnosis import HumanReviewRequest, HumanReviewResponse, ReviewStatus
from backend.database.repositories import HumanReviewRepository, DiagnosisRepository


class ReviewService:
    """Handles Human-in-the-Loop review submissions and audit recording."""

    @staticmethod
    def process_review(request: HumanReviewRequest, db: Session) -> HumanReviewResponse:
        rev_id = f"REV-{uuid.uuid4().hex[:6].upper()}"

        # Fetch diagnosis to capture predicted fault
        diag = DiagnosisRepository.get_by_id(db, request.diagnosis_id)
        predicted_fault = diag.root_cause if diag else ""
        case_id = request.case_id or (diag.case_id if diag else None)

        ai_agreement = (request.status == ReviewStatus.ACCEPTED)

        # Enforce validation for EDIT / REJECT
        if request.status in [ReviewStatus.EDITED, ReviewStatus.REJECTED]:
            if not request.reviewer_reason or len(request.reviewer_reason.strip()) < 5:
                raise ValueError("Reviewer reason is mandatory and must be at least 5 characters for EDITED or REJECTED diagnoses.")
            if not request.corrected_diagnosis or not request.corrected_diagnosis.strip():
                raise ValueError("A corrected diagnosis is mandatory for EDITED or REJECTED diagnoses.")

        db_rev = HumanReviewRepository.create(
            db=db,
            review_id=rev_id,
            diagnosis_id=request.diagnosis_id,
            case_id=case_id,
            status=request.status.value if hasattr(request.status, 'value') else str(request.status),
            reviewer_name=request.reviewer_name,
            ai_predicted_fault=predicted_fault,
            corrected_diagnosis=request.corrected_diagnosis or "",
            reviewer_reason=request.reviewer_reason,
            ai_agreement=ai_agreement
        )

        return HumanReviewResponse(
            review_id=db_rev.review_id,
            diagnosis_id=db_rev.diagnosis_id,
            case_id=db_rev.case_id,
            status=ReviewStatus(db_rev.status),
            reviewer_name=db_rev.reviewer_name,
            corrected_diagnosis=db_rev.corrected_diagnosis or "",
            reviewer_reason=db_rev.reviewer_reason,
            created_at=db_rev.created_at.isoformat() if db_rev.created_at else ""
        )
