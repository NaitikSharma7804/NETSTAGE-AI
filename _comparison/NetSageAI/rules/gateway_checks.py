"""Deterministic checks for Default Gateway misconfigurations and DHCP pool options."""

import re
from typing import Dict, List, Any


def check_gateway_configuration(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Checks host default gateway settings, ip default-gateway, and ip dhcp pool default-router."""
    results = []
    text = f"{symptom}\n{topology_note}\n{show_output}"

    # Check for DHCP pool missing default-router
    if "ip dhcp pool" in show_output.lower() and "default-router" not in show_output.lower():
        results.append({
            "rule": "gateway_dhcp_check",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "DHCP server pool is missing the default-router parameter, preventing clients from acquiring default gateway."
        })

    # Check host gateway mismatch
    if "gateway" in text.lower() and ("mismatch" in text.lower() or "cannot reach" in text.lower() or "different" in text.lower()):
        # Try extracting gateway IP from show output / ipconfig
        gateway_matches = re.findall(r'(?:gateway|Gateway)[:\s]+(\d{1,3}(?:\.\d{1,3}){3})', text, re.IGNORECASE)
        interface_ips = re.findall(r'(?:ip address|interface)[:\s]+(\d{1,3}(?:\.\d{1,3}){3})', text, re.IGNORECASE)

        if gateway_matches and interface_ips and gateway_matches[0] not in interface_ips:
            results.append({
                "rule": "gateway_mismatch_check",
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"Configured default gateway ({gateway_matches[0]}) does not match router interface IP."
            })
        elif "gateway" in symptom.lower() and "mismatch" in symptom.lower():
            results.append({
                "rule": "gateway_mismatch_check",
                "status": "FAIL",
                "severity": "HIGH",
                "message": "Default gateway configuration on host does not match the active router interface address."
            })

    return results
