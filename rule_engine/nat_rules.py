"""
NAT (Network Address Translation) and PAT Validation Rules.
Detects missing 'ip nat outside', omitted 'overload' keywords, and mismatched NAT source ACLs.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_missing_nat_outside(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects missing 'ip nat outside' statement when inside is configured."""
    has_outside_none = bool(re.search(r"Outside interfaces:\s*\n\s*none", show_outputs, re.IGNORECASE))
    has_inside = bool(re.search(r"Inside interfaces:\s*\n\s*GigabitEthernet|ip nat inside", show_outputs, re.IGNORECASE))

    if has_outside_none and has_inside:
        return RuleCheckResult(
            rule_id="NAT_001",
            rule_name="Missing IP NAT Outside Interface",
            category="NAT",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message="NAT translation is failing because the WAN/outside interface is missing the 'ip nat outside' command ('Outside interfaces: none').",
            evidence="show ip nat statistics: Outside interfaces: none",
            recommendation="Apply 'ip nat outside' to the WAN/internet-facing interface."
        )

    return RuleCheckResult(
        rule_id="NAT_001",
        rule_name="NAT Inside/Outside Interface Boundary Check",
        category="NAT",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="NAT inside/outside boundaries are configured properly or not present.",
        evidence="",
        recommendation=""
    )


def check_missing_nat_overload(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects NAT statement missing the 'overload' keyword for Port Address Translation (PAT)."""
    nat_line = re.search(r"ip nat inside source list\s+\d+\s+interface\s+[\w\d\/]+(\s+overload)?", show_outputs, re.IGNORECASE)
    if nat_line and not nat_line.group(1):
        return RuleCheckResult(
            rule_id="NAT_002",
            rule_name="Omitted 'overload' Keyword in Dynamic NAT",
            category="NAT",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message="The 'overload' keyword is missing from 'ip nat inside source list ...', causing single-IP dynamic 1-to-1 NAT exhaustion instead of PAT.",
            evidence=nat_line.group(0),
            recommendation="Append 'overload' to the dynamic NAT statement: '... interface <iface> overload'."
        )

    return RuleCheckResult(
        rule_id="NAT_002",
        rule_name="NAT Port Address Translation (Overload) Check",
        category="NAT",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="NAT overload is enabled or dynamic 1-to-1 NAT is not incorrectly configured.",
        evidence="",
        recommendation=""
    )