"""
Data Access Repository for NetSage AI.
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.models.case import (
    CaseModel,
    DiagnosisModel,
    RuleResultModel,
    HumanReviewModel,
    VerificationModel,
    LLMRunModel,
)
from ai.schemas.diagnosis import DiagnosisResponse, EvidenceItem
from rule_engine.models import RuleCheckResult


class CaseRepository:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[CaseModel]:
        return db.query(CaseModel).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_case_id(db: Session, case_id: str) -> Optional[CaseModel]:
        return db.query(CaseModel).filter(CaseModel.case_id == case_id).first()

    @staticmethod
    def create(db: Session, case_dict: Dict[str, Any]) -> CaseModel:
        db_case = CaseModel(**case_dict)
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        return db_case

    @staticmethod
    def count(db: Session) -> int:
        return db.query(CaseModel).count()


class DiagnosisRepository:
    @staticmethod
    def create(
        db: Session,
        diag: DiagnosisResponse,
        rule_results: Optional[List[RuleCheckResult]] = None
    ) -> DiagnosisModel:
        db_diag = DiagnosisModel(
            diagnosis_id=diag.diagnosis_id,
            case_id=diag.case_id,
            root_cause=diag.root_cause,
            confidence=diag.confidence.value if hasattr(diag.confidence, 'value') else str(diag.confidence),
            osi_layer=diag.osi_layer,
            affected_component=diag.affected_component,
            evidence_json=json.dumps([e.model_dump() for e in diag.evidence]),
            next_command=diag.next_command,
            fix_steps_json=json.dumps(diag.fix_steps),
            alternative_causes_json=json.dumps(diag.alternative_causes),
            raw_response=diag.raw_response or ""
        )
        db.add(db_diag)
        db.flush()

        if rule_results:
            for r in rule_results:
                rr_model = RuleResultModel(
                    diagnosis_id=diag.diagnosis_id,
                    rule_id=r.rule_id,
                    rule_name=r.rule_name,
                    category=r.category,
                    status=r.status.value if hasattr(r.status, 'value') else str(r.status),
                    severity=r.severity.value if hasattr(r.severity, 'value') else str(r.severity),
                    message=r.message,
                    evidence=r.evidence or "",
                    recommendation=r.recommendation or ""
                )
                db.add(rr_model)

        db.commit()
        db.refresh(db_diag)
        return db_diag

    @staticmethod
    def get_by_id(db: Session, diagnosis_id: str) -> Optional[DiagnosisModel]:
        return db.query(DiagnosisModel).filter(DiagnosisModel.diagnosis_id == diagnosis_id).first()

    @staticmethod
    def get_all(db: Session, limit: int = 100) -> List[DiagnosisModel]:
        return db.query(DiagnosisModel).order_by(DiagnosisModel.created_at.desc()).limit(limit).all()


class HumanReviewRepository:
    @staticmethod
    def create(
        db: Session,
        review_id: str,
        diagnosis_id: str,
        case_id: Optional[str],
        status: str,
        reviewer_name: str,
        ai_predicted_fault: str,
        corrected_diagnosis: str,
        reviewer_reason: str,
        ai_agreement: bool
    ) -> HumanReviewModel:
        rev = HumanReviewModel(
            review_id=review_id,
            diagnosis_id=diagnosis_id,
            case_id=case_id,
            status=status,
            reviewer_name=reviewer_name,
            ai_predicted_fault=ai_predicted_fault,
            corrected_diagnosis=corrected_diagnosis,
            reviewer_reason=reviewer_reason,
            ai_agreement=ai_agreement
        )
        db.add(rev)
        db.commit()
        db.refresh(rev)
        return rev

    @staticmethod
    def get_all(db: Session) -> List[HumanReviewModel]:
        return db.query(HumanReviewModel).order_by(HumanReviewModel.created_at.desc()).all()


class VerificationRepository:
    @staticmethod
    def create(
        db: Session,
        verification_id: str,
        diagnosis_id: str,
        case_id: Optional[str],
        status: str,
        verification_command: str,
        verification_output: str,
        tester_notes: str = ""
    ) -> VerificationModel:
        verif = VerificationModel(
            verification_id=verification_id,
            diagnosis_id=diagnosis_id,
            case_id=case_id,
            status=status,
            verification_command=verification_command,
            verification_output=verification_output,
            tester_notes=tester_notes
        )
        db.add(verif)
        db.commit()
        db.refresh(verif)
        return verif

    @staticmethod
    def get_all(db: Session) -> List[VerificationModel]:
        return db.query(VerificationModel).order_by(VerificationModel.created_at.desc()).all()


class LLMRunRepository:
    @staticmethod
    def log_run(
        db: Session,
        run_id: str,
        provider: str,
        model: str,
        prompt_version: str,
        case_id: Optional[str] = None,
        execution_time_ms: int = 0,
        status: str = "SUCCESS",
        error_message: str = ""
    ) -> LLMRunModel:
        run = LLMRunModel(
            run_id=run_id,
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            case_id=case_id,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run