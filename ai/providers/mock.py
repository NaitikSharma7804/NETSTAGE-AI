"""
High-Fidelity Deterministic Mock LLM Provider.
Enables 100% offline operation, demo presentations, and automated testing.
"""

import csv
import os
import uuid
from typing import Dict, Any, Optional
from ai.providers.base import LLMProvider
from ai.schemas.diagnosis import (
    ConfidenceLevel,
    DiagnosisRequest,
    DiagnosisResponse,
    EvidenceItem,
)
from rule_engine.models import RuleStatus


class MockLLMProvider(LLMProvider):
    """Deterministic Mock AI Diagnostic Provider."""

    def __init__(self, model_name: str = "mock-netsage-v1", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.case_catalog: Dict[str, Dict[str, str]] = {}
        self._load_catalog()

    def _load_catalog(self):
        cases_file = os.path.join("data", "cases.csv")
        if os.path.exists(cases_file):
            try:
                with open(cases_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.case_catalog[row["case_id"]] = row
            except Exception:
                pass

    def is_available(self) -> bool:
        return True

    async def generate_diagnosis(self, request: DiagnosisRequest, simulate_misdiagnosis: bool = False) -> DiagnosisResponse:
        """Generates realistic structured diagnosis for known cases or ad-hoc input."""
        cid = request.case_id or ""
        diag_id = f"DIAG-{cid if cid else 'ADHOC'}-{uuid.uuid4().hex[:6].upper()}"

        # 1. Check if this is a known case from dataset
        if cid and cid in self.case_catalog:
            case_data = self.case_catalog[cid]

            # Intentional demo misdiagnosis cases for responsible AI demonstration
            if simulate_misdiagnosis:
                if cid == "NS-DNS-004":
                    return DiagnosisResponse(
                        diagnosis_id=diag_id,
                        case_id=cid,
                        root_cause="Public DNS server 1.1.1.1 is offline or unreachable across the ISP WAN link.",
                        confidence=ConfidenceLevel.HIGH,
                        osi_layer="Layer 7 (Application / DNS)",
                        affected_component="External DNS Server 1.1.1.1",
                        evidence=[
                            EvidenceItem(
                                source="symptom",
                                observation="Public internet FQDN resolution fails",
                                relevance="Suggests external DNS resolver is non-responsive."
                            )
                        ],
                        next_command="ping 1.1.1.1",
                        fix_steps=["Contact ISP or switch primary DNS to 8.8.8.8"],
                        alternative_causes=["Local DNS server failure", "WAN interface down"]
                    )
                elif cid == "NS-VLAN-005":
                    return DiagnosisResponse(
                        diagnosis_id=diag_id,
                        case_id=cid,
                        root_cause="Physical cabling defect or SFP failure between SW-Core and SW-Acc1.",
                        confidence=ConfidenceLevel.MEDIUM,
                        osi_layer="Layer 1 (Physical)",
                        affected_component="Trunk Cable Gi0/1",
                        evidence=[
                            EvidenceItem(
                                source="symptom",
                                observation="VLAN 40 not appearing on SW-Acc1",
                                relevance="Assuming trunk link dropped packets."
                            )
                        ],
                        next_command="show interfaces Gi0/1 status",
                        fix_steps=["Replace physical patch cable between core and access switch."],
                        alternative_causes=["VTP configuration revision lock", "Trunk pruning"]
                    )

            # Standard accurate diagnosis based on catalog
            fix_steps = [s.strip() for s in case_data.get("expected_fix", "").split("\n") if s.strip()]
            if not fix_steps:
                fix_steps = ["Verify configuration with show running-config", "Apply remediation in Packet Tracer"]

            evidence_items = [
                EvidenceItem(
                    source="show command outputs",
                    observation=f"Matched fault signature: {case_data.get('expected_fault', '')[:100]}...",
                    relevance="Observation directly correlates with the reported connectivity failure."
                )
            ]

            if request.target_ip:
                evidence_items.append(
                    EvidenceItem(
                        source="target IP input",
                        observation=f"User identified {request.target_ip} as the host under investigation; no probe was executed by NetSage.",
                        relevance="Provides host context only and must be corroborated with Cisco command output."
                    )
                )

            # Incorporate any failed rule engine results as explicit evidence
            if request.rule_results:
                for r in request.rule_results:
                    if r.status in [RuleStatus.FAIL, RuleStatus.WARNING]:
                        evidence_items.append(
                            EvidenceItem(
                                source=f"Deterministic Rule [{r.rule_id}] {r.rule_name}",
                                observation=r.message,
                                relevance=r.recommendation or "Validated by deterministic rule engine."
                            )
                        )

            return DiagnosisResponse(
                diagnosis_id=diag_id,
                case_id=cid,
                root_cause=case_data.get("expected_fault", "Identified configuration anomaly in network device."),
                confidence=ConfidenceLevel.HIGH,
                osi_layer=case_data.get("osi_layer", "Layer 3 (Network)"),
                affected_component=case_data.get("concept", "Network Device"),
                evidence=evidence_items,
                next_command=case_data.get("expected_next_command", "show running-config"),
                fix_steps=fix_steps,
                alternative_causes=[
                    "Transient hardware link flapping (ruled out by interface uptime)",
                    "Mismatched MTU on adjacent nodes (verified standard MTU 1500)"
                ]
            )

        # 2. Ad-hoc custom case diagnosis using Rule Engine findings and heuristic analysis
        failed_rules = [r for r in (request.rule_results or []) if r.status == RuleStatus.FAIL]
        warning_rules = [r for r in (request.rule_results or []) if r.status == RuleStatus.WARNING]

        evidence_items = []
        for r in failed_rules + warning_rules:
            evidence_items.append(
                EvidenceItem(
                    source=f"Rule Engine: {r.rule_name} ({r.rule_id})",
                    observation=r.message,
                    relevance=r.evidence or r.recommendation
                )
            )

        if not evidence_items and not request.show_outputs.strip():
            evidence_items.append(
                EvidenceItem(
                    source="submitted evidence",
                    observation="No Cisco show-command output was supplied.",
                    relevance="Only symptom-based triage is possible until Cisco evidence is collected."
                )
            )
        elif not evidence_items:
            evidence_items.append(
                EvidenceItem(
                    source="show_outputs",
                    observation="Examined show command lines against baseline Cisco behaviors",
                    relevance="Heuristic inspection of provided network symptoms"
                )
            )

        if request.target_ip:
            evidence_items.append(
                EvidenceItem(
                    source="target IP input",
                    observation=f"User identified {request.target_ip} as the host under investigation; no probe was executed by NetSage.",
                    relevance="Provides host context only and must be corroborated with Cisco command output."
                )
            )

        if failed_rules:
            primary_fail = failed_rules[0]
            root_cause = primary_fail.message
            fix_steps = [primary_fail.recommendation] if primary_fail.recommendation else ["Review Cisco running-config"]
            confidence = ConfidenceLevel.HIGH
            osi_layer = "Layer 3 (Network)" if primary_fail.category in ["IP", "Subnet", "Gateway", "Routing"] else "Layer 2 (Data Link)"
        else:
            root_cause = f"Potential configuration or routing discrepancy related to symptom: {request.symptom[:80]}"
            fix_steps = ["Check interface status: show ip interface brief", "Check routing: show ip route"]
            confidence = ConfidenceLevel.MEDIUM
            osi_layer = "Layer 3 (Network)"

        return DiagnosisResponse(
            diagnosis_id=diag_id,
            case_id=cid or None,
            root_cause=root_cause,
            confidence=confidence,
            osi_layer=osi_layer,
            affected_component="Detected Cisco Network Topology",
            evidence=evidence_items,
            next_command="show running-config",
            fix_steps=fix_steps,
            alternative_causes=["Physical link failure", "Access control restriction"]
        )
