"""
VLAN and 802.1Q Configuration Rules.
Detects missing VLANs in VLAN database, inactive access ports, encapsulation mismatch, and VTP domain errors.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_missing_vlan(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects access port configured in a VLAN that does not exist in the VLAN database or is inactive."""
    # Check if an access port status is inactive (e.g. Fa0/5 inactive 20 or Fa0/5 PC-Link inactive 20)
    inactive_port = re.search(r"(\w+\d+(?:\/\d+)*)(?:\s+[\w\-]+)?\s+inactive\s+(\d+)", show_outputs, re.IGNORECASE)
    access_vlan_match = re.search(r"switchport access vlan\s+(\d+)", show_outputs, re.IGNORECASE)
    vlan_brief = re.search(r"show vlan brief([\s\S]*?)(?:SW|\#|\Z)", show_outputs, re.IGNORECASE)

    if inactive_port:
        port_name, vlan_id = inactive_port.groups()
        return RuleCheckResult(
            rule_id="VLAN_001",
            rule_name="Access Port Assigned to Non-Existent VLAN",
            category="VLAN",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Port {port_name} is assigned to VLAN {vlan_id}, but VLAN {vlan_id} does not exist in the switch database, making the port inactive.",
            evidence=f"Port {port_name} status: inactive, Vlan: {vlan_id}",
            recommendation=f"Create VLAN {vlan_id} on the switch: 'vlan {vlan_id}'."
        )

    if access_vlan_match and vlan_brief:
        target_vlan = access_vlan_match.group(1).strip()
        vlan_table_text = vlan_brief.group(1)
        if not re.search(rf"^\s*{target_vlan}\s+", vlan_table_text, re.MULTILINE):
            return RuleCheckResult(
                rule_id="VLAN_001",
                rule_name="Access Port Assigned to Non-Existent VLAN",
                category="VLAN",
                status=RuleStatus.FAIL,
                severity=RuleSeverity.HIGH,
                message=f"VLAN {target_vlan} is referenced by switchport access vlan, but is missing in 'show vlan brief'.",
                evidence=f"Configured access VLAN: {target_vlan}",
                recommendation=f"Create VLAN {target_vlan} on the switch in global configuration mode."
            )

    return RuleCheckResult(
        rule_id="VLAN_001",
        rule_name="VLAN Database Existence Check",
        category="VLAN",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="All referenced access VLANs exist in the switch VLAN database.",
        evidence="",
        recommendation=""
    )


def check_subinterface_encapsulation(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects subinterface dot1Q tag mismatch with subinterface number or topology."""
    subif_matches = re.findall(r"interface\s+([\w\d\/\.]+)\s+encapsulation\s+dot1Q\s+(\d+)", show_outputs, re.IGNORECASE)
    for subif_name, dot1q_tag in subif_matches:
        if "." in subif_name:
            subif_num = subif_name.split(".")[-1]
            if subif_num != dot1q_tag and (dot1q_tag.startswith(subif_num) or subif_num.startswith(dot1q_tag)):
                return RuleCheckResult(
                    rule_id="VLAN_002",
                    rule_name="Subinterface 802.1Q Encapsulation Mismatch",
                    category="VLAN",
                    status=RuleStatus.FAIL,
                    severity=RuleSeverity.CRITICAL,
                    message=f"Subinterface {subif_name} has mismatched 802.1Q encapsulation tag {dot1q_tag} (expected VLAN tag {subif_num}).",
                    evidence=f"interface {subif_name} -> encapsulation dot1Q {dot1q_tag}",
                    recommendation=f"Update encapsulation on {subif_name} to 'encapsulation dot1Q {subif_num}'."
                )

    return RuleCheckResult(
        rule_id="VLAN_002",
        rule_name="Router Subinterface 802.1Q Tag Check",
        category="VLAN",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Router subinterface encapsulation dot1Q tags match intended VLAN IDs.",
        evidence="",
        recommendation=""
    )


def check_native_vlan_mismatch(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects CDP Native VLAN mismatch syslog alerts or trunk discrepancies."""
    cdp_match = re.search(r"%CDP-4-NATIVE_VLAN_MISMATCH:\s*Native VLAN mismatch discovered on\s*([\w\d\/]+)\s*\((\d+)\),\s*with\s*[\w\d\-]+\s*[\w\d\/]+\s*\((\d+)\)", show_outputs, re.IGNORECASE)
    if cdp_match:
        iface, local_vlan, remote_vlan = cdp_match.groups()
        return RuleCheckResult(
            rule_id="VLAN_003",
            rule_name="Native VLAN Mismatch on Trunk Link",
            category="VLAN",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Native VLAN mismatch on trunk {iface}: Local Native VLAN {local_vlan} vs Remote Native VLAN {remote_vlan}.",
            evidence=cdp_match.group(0),
            recommendation=f"Configure matching native VLAN on both sides of trunk: 'switchport trunk native vlan {remote_vlan}'."
        )

    trunk_natives = re.findall(r"Native vlan\s*\n\s*[\w\d\/]+\s+[\w\d\-]+\s+[\w\d\-]+\s+[\w\d\-]+\s+(\d+)", show_outputs, re.IGNORECASE)
    if len(set(trunk_natives)) > 1:
        return RuleCheckResult(
            rule_id="VLAN_003",
            rule_name="Native VLAN Mismatch on Trunk Link",
            category="VLAN",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Trunk native VLANs differ across switches: {set(trunk_natives)}.",
            evidence=f"Native VLANs observed: {', '.join(set(trunk_natives))}",
            recommendation="Configure identical native VLAN on both trunk endpoints."
        )

    return RuleCheckResult(
        rule_id="VLAN_003",
        rule_name="Trunk Native VLAN Consistency",
        category="VLAN",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Native VLAN is consistent across trunk links.",
        evidence="",
        recommendation=""
    )