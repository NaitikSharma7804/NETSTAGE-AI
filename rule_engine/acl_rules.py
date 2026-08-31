"""
Access Control List (ACL) Validation Rules.
Detects implicit/explicit denies, inverted wildcard masks, missing TCP established keywords, and incorrect ACL placement/direction.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_acl_inverted_wildcard_mask(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects inverted wildcard masks in ACLs (e.g. using 255.255.255.0 instead of 0.0.0.255)."""
    bad_mask = re.search(r"permit\s+(?:tcp|udp|ip)\s+[\d\.]+\s+(255\.255\.255\.0|255\.255\.0\.0|255\.0\.0\.0)", show_outputs, re.IGNORECASE)
    if bad_mask:
        return RuleCheckResult(
            rule_id="ACL_001",
            rule_name="Inverted Wildcard Mask in Access List",
            category="ACL",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Access list uses a standard subnet mask ({bad_mask.group(1)}) instead of a Cisco inverse wildcard mask (e.g. 0.0.0.255), preventing expected traffic matching.",
            evidence=bad_mask.group(0),
            recommendation="Replace subnet mask with corresponding wildcard mask (e.g. replace 255.255.255.0 with 0.0.0.255)."
        )

    return RuleCheckResult(
        rule_id="ACL_001",
        rule_name="ACL Wildcard Mask Syntax Check",
        category="ACL",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="ACL wildcard mask syntax is valid.",
        evidence="",
        recommendation=""
    )


def check_acl_implicit_or_explicit_deny(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects active deny hits or implicit denies dropping legitimate traffic."""
    deny_matches = re.search(r"(?:deny\s+ip\s+any\s+any|\(implicit deny any matches:\s*(\d+)\)|\(\d+\s+matches\)\s*deny)", show_outputs, re.IGNORECASE)
    has_acl_drop = bool(re.search(r"access-list|ip access-group|BLOCK-", show_outputs, re.IGNORECASE))

    if deny_matches and has_acl_drop:
        return RuleCheckResult(
            rule_id="ACL_002",
            rule_name="ACL Packet Filtering / Deny Match",
            category="ACL",
            status=RuleStatus.WARNING,
            severity=RuleSeverity.HIGH,
            message="Access Control List contains active deny statements or implicit deny drops affecting traversing packets.",
            evidence=deny_matches.group(0),
            recommendation="Review ACL entries with 'show access-lists' and add permit statements for required source/destination subnets."
        )

    return RuleCheckResult(
        rule_id="ACL_002",
        rule_name="ACL Deny & Packet Filter Check",
        category="ACL",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="No unintended ACL packet drops or deny matches identified.",
        evidence="",
        recommendation=""
    )


def check_acl_missing_established(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects perimeter firewall ACL missing 'established' keyword for return TCP traffic."""
    inbound_wan_acl = re.search(r"interface\s+GigabitEthernet[\d\/]+\s+[\w\s\.\/]+ip access-group\s+[\w\-]+\s+in", show_outputs, re.IGNORECASE)
    has_tcp_established = bool(re.search(r"permit tcp .* established", show_outputs, re.IGNORECASE))
    has_high_deny = bool(re.search(r"deny ip any any \(\d+ matches\)", show_outputs, re.IGNORECASE))

    if inbound_wan_acl and not has_tcp_established and has_high_deny and "web" in (show_outputs + topology_note).lower():
        return RuleCheckResult(
            rule_id="ACL_003",
            rule_name="Missing 'established' Keyword in Inbound WAN ACL",
            category="ACL",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message="Inbound ACL on perimeter interface filters return TCP traffic without permitting established connections ('permit tcp any ... established').",
            evidence="Inbound ACL active on WAN without 'established' rule; high deny match count",
            recommendation="Add 'permit tcp any <internal-subnet> <wildcard> established' to permit stateful return TCP traffic."
        )

    return RuleCheckResult(
        rule_id="ACL_003",
        rule_name="Stateful Return Traffic ACL Check",
        category="ACL",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Inbound ACL allows established return TCP sessions or no stateful return issue detected.",
        evidence="",
        recommendation=""
    )