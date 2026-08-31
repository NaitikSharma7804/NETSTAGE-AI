"""Deterministic checks for Cisco interface status."""

import re
from typing import Dict, List, Any


def check_interface_status(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Detects interfaces that are administratively down or down/down."""
    results = []

    # Regex for 'show ip interface brief' lines: Interface IP-Address OK? Method Status Protocol
    # Example: GigabitEthernet0/0 192.168.1.1 YES manual administratively down down
    # Example: FastEthernet0/1 unassigned YES unset down down
    admin_down_pattern = re.compile(
        r'(\b[A-Za-z0-9/\.:\-]+\b)\s+([\d\.]+|unassigned)\s+\w+\s+\w+\s+(administratively down)\s+(down)',
        re.IGNORECASE
    )

    line_down_pattern = re.compile(
        r'(\b[A-Za-z0-9/\.:\-]+\b)\s+([\d\.]+|unassigned)\s+\w+\s+\w+\s+(down)\s+(down)',
        re.IGNORECASE
    )

    err_disabled_pattern = re.compile(
        r'(\b[A-Za-z0-9/\.:\-]+\b).*(err-disabled|errdisabled)',
        re.IGNORECASE
    )

    for line in show_output.splitlines():
        match_admin = admin_down_pattern.search(line)
        if match_admin:
            iface = match_admin.group(1)
            results.append({
                "rule": "interface_admin_down",
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"Interface {iface} is administratively down (shutdown command applied)."
            })
            continue

        match_err = err_disabled_pattern.search(line)
        if match_err:
            iface = match_err.group(1)
            results.append({
                "rule": "interface_err_disabled",
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"Interface {iface} is in err-disabled state due to security violation or error."
            })
            continue

        match_down = line_down_pattern.search(line)
        if match_down:
            iface = match_down.group(1)
            results.append({
                "rule": "interface_line_down",
                "status": "FAIL",
                "severity": "MEDIUM",
                "message": f"Interface {iface} physical link or line protocol is down."
            })

    if not results and ("down" in symptom.lower() or "cable" in symptom.lower()):
        # Informational pass
        results.append({
            "rule": "interface_status_pass",
            "status": "PASS",
            "severity": "INFO",
            "message": "No administratively down interfaces found in provided output."
        })

    return results
