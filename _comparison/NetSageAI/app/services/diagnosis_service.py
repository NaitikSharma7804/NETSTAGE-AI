"""Business logic service for running rules, AI diagnosis, and persisting diagnosis records."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from rules.checker import run_all_rules
from ai.diagnosis import AIDiagnosisEngine
from ai.evidence_grounding import evaluate_evidence_grounding
from ai.provider import get_llm_provider
from app.models.case import CaseModel
from app.models.diagnosis import DiagnosisModel
from app.schemas.diagnosis_schema import DiagnosisRequest, DiagnosisResponse, AIDiagnosisOutput


def run_case_diagnosis(db: Session, request: DiagnosisRequest) -> DiagnosisModel:
    """Runs deterministic rule checks, calls AI diagnosis engine, performs evidence grounding, and saves record."""
    
    # 1. Run deterministic Python rules
    rule_results = run_all_rules(
        symptom=request.symptom,
        topology_note=request.topology_note or "",
        show_output=request.show_output
    )

    # 2. Call AI Diagnosis Engine
    ai_engine = AIDiagnosisEngine()
    ai_result = ai_engine.run_diagnosis(
        symptom=request.symptom,
        topology_note=request.topology_note or "",
        show_output=request.show_output,
        rule_results=rule_results,
        concept=request.concept
    )

    # 3. Evidence Grounding Validation Layer
    grounding_res = evaluate_evidence_grounding(
        evidence_list=ai_result.evidence,
        symptom=request.symptom,
        topology_note=request.topology_note or "",
        show_output=request.show_output,
        rule_results=rule_results
    )

    # Detect dataset_status if linked to existing case
    ds_status = "SAMPLE"
    if request.case_id:
        c_obj = db.query(CaseModel).filter(CaseModel.case_id == request.case_id).first()
        if c_obj:
            ds_status = c_obj.dataset_status

    provider = get_llm_provider()

    # 4. Save diagnosis to DB with default 'Pending Review' status
    diagnosis_record = DiagnosisModel(
        case_id=request.case_id,
        symptom=request.symptom,
        topology_note=request.topology_note,
        show_output=request.show_output,
        root_cause=ai_result.root_cause,
        confidence=ai_result.confidence,
        osi_layer=ai_result.osi_layer,
        evidence=json.dumps(ai_result.evidence),
        next_command=ai_result.next_command,
        fix_steps=json.dumps(ai_result.fix_steps),
        rule_results=json.dumps(rule_results),
        review_status="Pending Review",
        dataset_status=ds_status,
        ai_mode=provider.mode,
        evidence_grounding_status=grounding_res["status"],
        grounded_evidence=json.dumps(grounding_res["grounded_items"])
    )

    db.add(diagnosis_record)
    db.commit()
    db.refresh(diagnosis_record)

    return diagnosis_record


def get_all_diagnoses(db: Session) -> List[DiagnosisModel]:
    """Retrieves all historical diagnoses."""
    return db.query(DiagnosisModel).order_by(DiagnosisModel.created_at.desc()).all()


def get_diagnosis_by_id(db: Session, diagnosis_id: int) -> Optional[DiagnosisModel]:
    """Retrieves diagnosis by database integer ID."""
    return db.query(DiagnosisModel).filter(DiagnosisModel.id == diagnosis_id).first()
