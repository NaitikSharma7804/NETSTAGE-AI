"""
Diagnosis & Validation API Router.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database.database import get_db
from ai.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse
from rule_engine.models import RuleEngineRun
from rule_engine.engine import rule_engine
from backend.services.diagnosis_service import DiagnosisService
from backend.database.repositories import DiagnosisRepository
from backend.services.ip_assessment_service import IPAssessmentService

router = APIRouter(prefix="", tags=["Diagnosis"])


@router.post("/diagnose")
async def diagnose(
    request: DiagnosisRequest,
    simulate_misdiagnosis: bool = Query(False, description="Simulate AI error for demo"),
    db: Session = Depends(get_db)
):
    """
    Primary Diagnosis Endpoint.
    1. Runs Deterministic Rule Engine
    2. Runs AI/LLM Reasoning
    3. Fuses Evidence & Resolves Conflicts
    4. Persists Diagnosis & Rule Findings
    """
    if not request.symptom.strip():
        raise HTTPException(status_code=400, detail="Symptom cannot be empty.")
    try:
        fused_diag, rule_run, fusion_meta = await DiagnosisService.diagnose_case(
            request=request,
            db=db,
            simulate_misdiagnosis=simulate_misdiagnosis
        )
        return {
            "diagnosis": fused_diag,
            "rule_engine": rule_run,
            "evidence_fusion": fusion_meta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis error: {str(e)}")


@router.post("/validate")
def validate_rules(request: DiagnosisRequest):
    """Runs deterministic Python rule engine without calling the LLM."""
    rule_run: RuleEngineRun = rule_engine.evaluate(
        show_outputs=request.show_outputs,
        topology_note=request.topology_note,
        symptom=request.symptom
    )
    return rule_run


@router.get("/ip-assessment/{target_ip:path}")
def assess_target_ip(target_ip: str):
    """Validate a target IP and prepare safe Cisco evidence-collection commands."""
    try:
        return IPAssessmentService.assess(target_ip)
    except ValueError:
        raise HTTPException(status_code=400, detail="target_ip must be a valid IPv4 or IPv6 address.")


@router.get("/diagnoses")
def list_diagnoses(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Lists historical AI diagnoses."""
    return DiagnosisRepository.get_all(db, limit=limit)
