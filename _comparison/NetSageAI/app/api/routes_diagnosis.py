"""FastAPI Router for AI Diagnosis."""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from app.schemas.diagnosis_schema import DiagnosisRequest, DiagnosisResponse, AIDiagnosisOutput
from app.services import diagnosis_service

router = APIRouter(prefix="/api", tags=["Diagnosis"])


@router.post("/diagnose", response_model=DiagnosisResponse)
def run_diagnosis(request: DiagnosisRequest, db: Session = Depends(get_db)):
    """Runs deterministic rule checks + AI diagnosis engine and returns structured diagnosis."""
    try:
        diagnosis_model = diagnosis_service.run_case_diagnosis(db, request)

        # Deserialize JSON strings for response schema
        rule_res = json.loads(diagnosis_model.rule_results) if diagnosis_model.rule_results else []
        ev_list = json.loads(diagnosis_model.evidence) if diagnosis_model.evidence else []
        fix_list = json.loads(diagnosis_model.fix_steps) if diagnosis_model.fix_steps else []

        ai_out = AIDiagnosisOutput(
            root_cause=diagnosis_model.root_cause,
            confidence=diagnosis_model.confidence,
            osi_layer=diagnosis_model.osi_layer,
            evidence=ev_list,
            next_command=diagnosis_model.next_command,
            fix_steps=fix_list
        )

        grounded_ev = json.loads(diagnosis_model.grounded_evidence) if diagnosis_model.grounded_evidence else []

        return DiagnosisResponse(
            id=diagnosis_model.id,
            case_id=diagnosis_model.case_id,
            symptom=diagnosis_model.symptom,
            topology_note=diagnosis_model.topology_note,
            show_output=diagnosis_model.show_output,
            rule_results=rule_res,
            ai_diagnosis=ai_out,
            review_status=getattr(diagnosis_model, "review_status", "Pending Review"),
            dataset_status=getattr(diagnosis_model, "dataset_status", "SAMPLE"),
            ai_mode=getattr(diagnosis_model, "ai_mode", "mock"),
            evidence_grounding_status=getattr(diagnosis_model, "evidence_grounding_status", "Unverified"),
            grounded_evidence=grounded_ev,
            created_at=diagnosis_model.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")


@router.get("/diagnoses", response_model=List[DiagnosisResponse])
def list_diagnoses(db: Session = Depends(get_db)):
    """Retrieves all past diagnosis runs."""
    records = diagnosis_service.get_all_diagnoses(db)
    responses = []
    for d in records:
        rule_res = json.loads(d.rule_results) if d.rule_results else []
        ev_list = json.loads(d.evidence) if d.evidence else []
        fix_list = json.loads(d.fix_steps) if d.fix_steps else []
        grounded_ev = json.loads(d.grounded_evidence) if d.grounded_evidence else []

        ai_out = AIDiagnosisOutput(
            root_cause=d.root_cause,
            confidence=d.confidence,
            osi_layer=d.osi_layer,
            evidence=ev_list,
            next_command=d.next_command,
            fix_steps=fix_list
        )
        responses.append(DiagnosisResponse(
            id=d.id,
            case_id=d.case_id,
            symptom=d.symptom,
            topology_note=d.topology_note,
            show_output=d.show_output,
            rule_results=rule_res,
            ai_diagnosis=ai_out,
            review_status=getattr(d, "review_status", "Pending Review"),
            dataset_status=getattr(d, "dataset_status", "SAMPLE"),
            ai_mode=getattr(d, "ai_mode", "mock"),
            evidence_grounding_status=getattr(d, "evidence_grounding_status", "Unverified"),
            grounded_evidence=grounded_ev,
            created_at=d.created_at
        ))
    return responses


@router.get("/diagnoses/{diagnosis_id}", response_model=DiagnosisResponse)
def get_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    """Retrieves diagnosis by database integer ID."""
    d = diagnosis_service.get_diagnosis_by_id(db, diagnosis_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Diagnosis #{diagnosis_id} not found.")

    rule_res = json.loads(d.rule_results) if d.rule_results else []
    ev_list = json.loads(d.evidence) if d.evidence else []
    fix_list = json.loads(d.fix_steps) if d.fix_steps else []
    grounded_ev = json.loads(d.grounded_evidence) if d.grounded_evidence else []

    ai_out = AIDiagnosisOutput(
        root_cause=d.root_cause,
        confidence=d.confidence,
        osi_layer=d.osi_layer,
        evidence=ev_list,
        next_command=d.next_command,
        fix_steps=fix_list
    )

    return DiagnosisResponse(
        id=d.id,
        case_id=d.case_id,
        symptom=d.symptom,
        topology_note=d.topology_note,
        show_output=d.show_output,
        rule_results=rule_res,
        ai_diagnosis=ai_out,
        review_status=getattr(d, "review_status", "Pending Review"),
        dataset_status=getattr(d, "dataset_status", "SAMPLE"),
        ai_mode=getattr(d, "ai_mode", "mock"),
        evidence_grounding_status=getattr(d, "evidence_grounding_status", "Unverified"),
        grounded_evidence=grounded_ev,
        created_at=d.created_at
    )
