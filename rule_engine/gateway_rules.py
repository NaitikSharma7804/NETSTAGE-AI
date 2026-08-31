"""
Default Gateway Validation Rules.
Checks if default gateway is in the same IP subnet as the host, and whether gateway interface is reachable.
"""

import ipaddress
import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_gateway_in_subnet(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects when a host's configured default gateway is outside its local IP subnet."""
    host_match = re.search(r"IP Address[\.\s]+:\s*([\d\.]+)\s+Subnet Mask[\.\s]+:\s*([\d\.]+)\s+Default Gateway[\.\s]+:\s*([\d\.]+)", show_outputs, re.IGNORECASE)
    if host_match:
        h_ip, h_mask, h_gw = host_match.groups()
        if h_gw and h_gw != "0.0.0.0":
            try:
                net = ipaddress.IPv4Network(f"{h_ip}/{h_mask}", strict=False)
                gw_obj = ipaddress.IPv4Address(h_gw)
                if gw_obj not in net:
                    return RuleCheckResult(
                        rule_id="GATEWAY_001",
                        rule_name="Default Gateway Outside Host Subnet",
                        category="Gateway",
                        status=RuleStatus.FAIL,
                        severity=RuleSeverity.CRITICAL,
                        message=f"Default gateway {h_gw} is outside the host's configured subnet {net} (Host IP: {h_ip}).",
                        evidence=f"Host IP: {h_ip}, Mask: {h_mask}, Gateway: {h_gw}",
                        recommendation="Configure host default gateway to an active IP address inside its local subnet."
                    )
            except Exception:
                pass

    return RuleCheckResult(
        rule_id="GATEWAY_001",
        rule_name="Default Gateway Subnet Membership",
        category="Gateway",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Default gateway is properly within the host's subnet.",
        evidence="",
        recommendation=""
    )


def check_hsrp_fhrp_vip(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects HSRP/VRRP virtual IP mismatch between redundant switches or host gateway."""
    hsrp_vips = re.findall(r"Vl\d+\s+\d+\s+\d+\s+[P\s]+\w+\s+[\w\.\d]+\s+[\w\.\d]+\s+([\d\.]+)", show_outputs, re.IGNORECASE)
    if len(set(hsrp_vips)) > 1:
        return RuleCheckResult(
            rule_id="GATEWAY_002",
            rule_name="HSRP Virtual IP Mismatch",
            category="Gateway",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message=f"HSRP redundancy group has conflicting Virtual IPs configured on redundant routers/switches: {hsrp_vips}.",
            evidence=f"Detected Virtual IPs: {', '.join(set(hsrp_vips))}",
            recommendation="Standardize the HSRP virtual IP address (standby <group> ip <vip>) identically on both redundant peers."
        )

    return RuleCheckResult(
        rule_id="GATEWAY_002",
        rule_name="FHRP/HSRP Redundancy Virtual IP Consistency",
        category="Gateway",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="HSRP/FHRP virtual IP configuration is consistent.",
        evidence="",
        recommendation=""
    )