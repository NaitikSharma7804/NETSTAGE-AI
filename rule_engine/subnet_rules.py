"""
Subnet Mask and Boundary Validation Rules.
"""

import ipaddress
import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_subnet_mask_mismatch(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects mask mismatches between host configuration and default gateway."""
    host_match = re.search(r"IP Address[\.\s]+:\s*([\d\.]+)\s+Subnet Mask[\.\s]+:\s*([\d\.]+)\s+Default Gateway[\.\s]+:\s*([\d\.]+)", show_outputs, re.IGNORECASE)
    router_match = re.search(r"interface\s+([\w\/\.]+)\s+ip address\s+([\d\.]+)\s+([\d\.]+)", show_outputs, re.IGNORECASE)

    if host_match and router_match:
        h_ip, h_mask, h_gw = host_match.groups()
        r_iface, r_ip, r_mask = router_match.groups()
        if h_gw == r_ip and h_mask != r_mask:
            return RuleCheckResult(
                rule_id="SUBNET_001",
                rule_name="Host and Router Subnet Mask Mismatch",
                category="Subnet",
                status=RuleStatus.FAIL,
                severity=RuleSeverity.HIGH,
                message=f"Subnet mask mismatch: Host configured with mask {h_mask} while router interface {r_iface} uses mask {r_mask}.",
                evidence=f"Host: {h_ip}/{h_mask} -> Router {r_iface}: {r_ip}/{r_mask}",
                recommendation=f"Update host subnet mask to match router {r_iface} mask ({r_mask})."
            )

    return RuleCheckResult(
        rule_id="SUBNET_001",
        rule_name="Subnet Mask Consistency Check",
        category="Subnet",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Host and router subnet masks are consistent or not conflicting.",
        evidence="",
        recommendation=""
    )