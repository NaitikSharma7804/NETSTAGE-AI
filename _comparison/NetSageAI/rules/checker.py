"""Master Deterministic Rule Checker for NetSage AI.

Combines rule modules to execute deterministic checks on Cisco network artifacts.
"""

from typing import Dict, List, Any
from rules.interface_checks import check_interface_status
from rules.ip_checks import check_duplicate_ips
from rules.subnet_checks import check_subnet_masks
from rules.gateway_checks import check_gateway_configuration
from rules.vlan_checks import check_vlan_configuration
from rules.route_checks import check_routing_configuration


def run_all_rules(symptom: str, topology_note: str, show_output: str) -> List[Dict[str, Any]]:
    """Runs all deterministic Python checks and returns structured rule findings."""
    all_findings = []

    # 1. Interface checks
    all_findings.extend(check_interface_status(show_output, symptom, topology_note))

    # 2. Duplicate IP checks
    all_findings.extend(check_duplicate_ips(show_output, symptom, topology_note))

    # 3. Subnet checks
    all_findings.extend(check_subnet_masks(show_output, symptom, topology_note))

    # 4. Gateway checks
    all_findings.extend(check_gateway_configuration(show_output, symptom, topology_note))

    # 5. VLAN checks
    all_findings.extend(check_vlan_configuration(show_output, symptom, topology_note))

    # 6. Route checks
    all_findings.extend(check_routing_configuration(show_output, symptom, topology_note))

    # If no failures detected, return an informational check status
    if not all_findings:
        all_findings.append({
            "rule": "deterministic_syntax_check",
            "status": "PASS",
            "severity": "INFO",
            "message": "No basic deterministic rule violations flagged in raw CLI output."
        })

    return all_findings
