"""
Fix Verification Service.
Records PASS / FAIL outcomes after manual Cisco configuration changes.
"""

import uuid
from sqlalchemy.orm import Session
from ai.schemas.diagnosis import VerificationRequest, VerificationResponse, VerificationStatus
from backend.database.repositories import VerificationRepository


class VerificationService:
    """Handles fix outcome recording and verification tracking."""

    @staticmethod
    def process_verification(request: VerificationRequest, db: Session) -> VerificationResponse:
        v_id = f"VERIF-{uuid.uuid4().hex[:6].upper()}"

        db_v = VerificationRepository.create(
            db=db,
            verification_id=v_id,
            diagnosis_id=request.diagnosis_id,
            case_id=request.case_id,
            status=request.status.value if hasattr(request.status, 'value') else str(request.status),
            verification_command=request.verification_command,
            verification_output=request.verification_output,
            tester_notes=request.tester_notes or ""
        )

        return VerificationResponse(
            verification_id=db_v.verification_id,
            diagnosis_id=db_v.diagnosis_id,
            case_id=db_v.case_id,
            status=VerificationStatus(db_v.status),
            verification_command=db_v.verification_command,
            verification_output=db_v.verification_output,
            tester_notes=db_v.tester_notes or "",
            created_at=db_v.created_at.isoformat() if db_v.created_at else ""
        )