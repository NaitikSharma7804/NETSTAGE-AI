"""
Evidence Fusion and Conflict Detection Service.
Fuses deterministic rule engine findings with AI/LLM diagnostic output.
"""

from typing import List, Dict, Any, Tuple
from ai.schemas.diagnosis import DiagnosisResponse, EvidenceItem, ConfidenceLevel
from rule_engine.models import RuleCheckResult, RuleStatus, RuleSeverity


class EvidenceFusionService:
    """Fuses deterministic rule checks and LLM diagnoses into a unified assessment."""

    @staticmethod
    def fuse_evidence(
        diagnosis: DiagnosisResponse,
        rule_results: List[RuleCheckResult]
    ) -> Tuple[DiagnosisResponse, Dict[str, Any]]:
        """
        Combines rule results with AI diagnosis.
        Checks for rule-vs-AI agreement, conflicts, or confidence adjustments.
        """
        failed_rules = [r for r in rule_results if r.status == RuleStatus.FAIL]
        warning_rules = [r for r in rule_results if r.status == RuleStatus.WARNING]

        conflict_detected = False
        conflict_details = []
        agreement_points = []

        # Compare failed rules with AI root cause
        ai_cause_lower = diagnosis.root_cause.lower()
        for r in failed_rules:
            rule_cat = r.category.lower()
            rule_msg = r.message.lower()

            # Check if AI diagnosis mentions the failing concept or rule
            if rule_cat in ai_cause_lower or any(word in ai_cause_lower for word in r.rule_name.lower().split()):
                agreement_points.append(f"Rule [{r.rule_id}] directly corroborates AI diagnosis ({r.rule_name}).")
            else:
                # Potential conflict or additional unaddressed issue
                conflict_detected = True
                conflict_details.append(
                    f"Deterministic check failed [{r.rule_id}: {r.rule_name}], but AI focused on different root cause."
                )

        # Incorporate all deterministic findings into evidence list if not already present
        existing_sources = {e.source for e in diagnosis.evidence}
        for r in failed_rules + warning_rules:
            src_label = f"Rule Engine [{r.rule_id}]"
            if src_label not in existing_sources:
                diagnosis.evidence.append(
                    EvidenceItem(
                        source=src_label,
                        observation=r.message,
                        relevance=r.recommendation or "Deterministic signature detected in Cisco show output."
                    )
                )

        # Adjust confidence if severe conflict exists
        if conflict_detected and diagnosis.confidence == ConfidenceLevel.HIGH:
            diagnosis.confidence = ConfidenceLevel.MEDIUM

        fusion_metadata = {
            "deterministic_rule_count": len(rule_results),
            "failed_rule_count": len(failed_rules),
            "warning_rule_count": len(warning_rules),
            "agreement_points": agreement_points,
            "conflict_detected": conflict_detected,
            "conflict_details": conflict_details,
            "status": "CONFLICT" if conflict_detected else "ALIGNED"
        }

        return diagnosis, fusion_metadata