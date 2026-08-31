"""
End-to-End Troubleshooting & Diagnosis Orchestrator Service.
"""

import time
import uuid
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from ai.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse, ConfidenceLevel, EvidenceItem
from rule_engine.engine import rule_engine
from rule_engine.models import RuleEngineRun
from backend.services.ai_service import AIService
from backend.services.evidence_service import EvidenceFusionService
from backend.database.repositories import DiagnosisRepository, LLMRunRepository, CaseRepository
from backend.services.ip_assessment_service import IPAssessmentService


class DiagnosisService:
    """Orchestrates validation, AI inference, evidence fusion, and persistence."""

    @staticmethod
    async def diagnose_case(
        request: DiagnosisRequest,
        db: Optional[Session] = None,
        simulate_misdiagnosis: bool = False
    ) -> Tuple[DiagnosisResponse, RuleEngineRun, Dict[str, Any]]:
        start_time = time.time()

        # Step 1: Run Deterministic Rule Engine
        rule_run: RuleEngineRun = rule_engine.evaluate(
            show_outputs=request.show_outputs,
            topology_note=request.topology_note,
            symptom=request.symptom
        )
        request.rule_results = rule_run.results

        # Step 2: Invoke AI Diagnostic Provider
        provider = AIService.get_provider()
        
        # Check if mock provider with simulate_misdiagnosis option
        if hasattr(provider, 'generate_diagnosis') and simulate_misdiagnosis:
            try:
                ai_diag: DiagnosisResponse = await provider.generate_diagnosis(request, simulate_misdiagnosis=True)
            except TypeError:
                ai_diag: DiagnosisResponse = await provider.generate_diagnosis(request)
        else:
            ai_diag: DiagnosisResponse = await provider.generate_diagnosis(request)

        # Step 3: Evidence Fusion
        fused_diag, fusion_meta = EvidenceFusionService.fuse_evidence(ai_diag, rule_run.results)
        # Preserve the exact user input for review and dashboard state after reruns.
        fused_diag.symptom = request.symptom

        if not request.show_outputs.strip():
            # A symptom-only result is permitted for triage, but is explicitly not
            # evidence-backed and may never be represented as high confidence.
            fused_diag.confidence = ConfidenceLevel.LOW
            fused_diag.evidence.append(EvidenceItem(
                source="submitted evidence",
                observation="No Cisco show-command output was supplied.",
                relevance="Diagnosis is limited to symptom-based triage; collect the recommended command output before applying a fix."
            ))
            fusion_meta["evidence_limited"] = True
            fusion_meta["status"] = "LIMITED_EVIDENCE"

        # A target address is context only. Keep its assessment separate from actual
        # CLI evidence so the UI never implies that NetSage probed the network.
        if request.target_ip:
            fusion_meta["target_ip_assessment"] = IPAssessmentService.assess(request.target_ip)

        # Step 4: Persist in Database if session available
        elapsed_ms = int((time.time() - start_time) * 1000)
        if db:
            DiagnosisRepository.create(db, fused_diag, rule_run.results)
            LLMRunRepository.log_run(
                db=db,
                run_id=f"RUN-{uuid.uuid4().hex[:8].upper()}",
                provider=provider.__class__.__name__,
                model=provider.model_name,
                prompt_version="v1.2.0",
                case_id=request.case_id,
                execution_time_ms=elapsed_ms,
                status="SUCCESS"
            )

        return fused_diag, rule_run, fusion_meta
