"""
Pydantic Schemas for AI Diagnosis, Human Review, and Fix Verification.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from rule_engine.models import RuleCheckResult


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OSILayer(str, Enum):
    LAYER_1 = "Layer 1 (Physical)"
    LAYER_2 = "Layer 2 (Data Link)"
    LAYER_3 = "Layer 3 (Network)"
    LAYER_4 = "Layer 4 (Transport)"
    LAYER_7 = "Layer 7 (Application)"


class EvidenceItem(BaseModel):
    source: str = Field(..., description="Cisco command or configuration source (e.g. 'show access-lists')")
    observation: str = Field(..., description="Exact finding or quote from output (e.g. 'implicit deny match count 128')")
    relevance: str = Field(..., description="Explanation of how this observation supports the diagnosis")


class DiagnosisRequest(BaseModel):
    case_id: Optional[str] = Field(None, description="Troubleshooting case identifier")
    symptom: str = Field(..., description="Observed network symptom")
    topology_note: str = Field("", description="Network topology notes")
    show_outputs: str = Field(..., description="Cisco CLI command outputs")
    target_ip: Optional[str] = Field(None, description="Optional host IP being investigated; this is context, not probe evidence")
    rule_results: Optional[List[RuleCheckResult]] = Field(default_factory=list, description="Findings from deterministic rule engine")

    @field_validator("target_ip")
    @classmethod
    def validate_target_ip(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return None
        from ipaddress import ip_address
        try:
            return str(ip_address(value.strip()))
        except ValueError as exc:
            raise ValueError("target_ip must be a valid IPv4 or IPv6 address") from exc


class DiagnosisResponse(BaseModel):
    diagnosis_id: str = Field(..., description="Unique diagnosis ID (e.g. DIAG-20260825-ABCD)")
    case_id: Optional[str] = Field(None, description="Associated case ID")
    symptom: str = Field("", description="Exact symptom submitted for this diagnosis")
    root_cause: str = Field(..., description="Primary diagnosed root cause")
    confidence: ConfidenceLevel = Field(..., description="Confidence rating: low, medium, or high")
    osi_layer: str = Field(..., description="Affected OSI layer")
    affected_component: str = Field(..., description="Specific network device, interface, protocol, or host affected")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Citations from CLI output supporting diagnosis")
    next_command: str = Field(..., description="Recommended next diagnostic Cisco show command")
    fix_steps: List[str] = Field(default_factory=list, description="Step-by-step Cisco CLI commands to resolve the fault")
    alternative_causes: List[str] = Field(default_factory=list, description="Other possible causes ruled out or requiring further evidence")
    ai_disclaimer: str = Field(
        "NetSage AI assists with diagnosis but does NOT execute changes. A certified human engineer must review and verify all recommendations.",
        description="Responsible AI human-in-the-loop notice"
    )
    raw_response: Optional[str] = Field(None, description="Raw LLM response string")


class ReviewStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"


class HumanReviewRequest(BaseModel):
    diagnosis_id: str = Field(..., description="ID of the diagnosis being reviewed")
    case_id: Optional[str] = Field(None, description="Case ID")
    status: ReviewStatus = Field(..., description="ACCEPTED, EDITED, or REJECTED")
    reviewer_name: str = Field("Network Engineer", description="Name/Role of the reviewer")
    corrected_diagnosis: Optional[str] = Field("", description="Human corrected root cause (required if EDITED or REJECTED)")
    reviewer_reason: str = Field(..., description="Detailed technical reason for acceptance, edit, or rejection")


class HumanReviewResponse(BaseModel):
    review_id: str
    diagnosis_id: str
    case_id: Optional[str]
    status: ReviewStatus
    reviewer_name: str
    corrected_diagnosis: str
    reviewer_reason: str
    created_at: str


class VerificationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class VerificationRequest(BaseModel):
    diagnosis_id: str = Field(..., description="Associated diagnosis ID")
    case_id: Optional[str] = Field(None, description="Case ID")
    status: VerificationStatus = Field(..., description="PASS or FAIL")
    verification_command: str = Field("ping / show output", description="Command used to verify fix")
    verification_output: str = Field(..., description="CLI output or observations confirming fix outcome")
    tester_notes: Optional[str] = Field("", description="Additional observations from verification")


class VerificationResponse(BaseModel):
    verification_id: str
    diagnosis_id: str
    case_id: Optional[str]
    status: VerificationStatus
    verification_command: str
    verification_output: str
    tester_notes: str
    created_at: str
