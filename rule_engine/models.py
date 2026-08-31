"""
Rule Engine Pydantic Data Models.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "NOT_CHECKED"


class RuleSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleCheckResult(BaseModel):
    rule_id: str = Field(..., description="Unique rule code, e.g., VLAN_001, GW_001")
    rule_name: str = Field(..., description="Short descriptive rule name")
    category: str = Field(..., description="Category tag e.g. VLAN, IP, Routing, ACL")
    status: RuleStatus = Field(..., description="PASS, FAIL, WARNING, or NOT_CHECKED")
    severity: RuleSeverity = Field(RuleSeverity.INFO, description="Severity if failed")
    message: str = Field(..., description="Detailed diagnostic explanation")
    evidence: str = Field("", description="Specific command output excerpt supporting the finding")
    recommendation: str = Field("", description="Deterministic fix recommendation")
    finding: str = Field("", description="Human-readable deterministic finding")
    expected: str = Field("", description="Expected valid configuration or state when known")
    actual: str = Field("", description="Actual observed configuration or state when known")

    @model_validator(mode="after")
    def populate_finding(self):
        if not self.finding:
            self.finding = self.message
        return self


class RuleEngineRun(BaseModel):
    total_rules_evaluated: int = 0
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    results: List[RuleCheckResult] = []
