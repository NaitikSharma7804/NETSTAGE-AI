"""Deterministic checks for VLAN configurations, trunks, allowed lists, and database presence."""

import re
from typing import Dict, List, Any


def check_vlan_configuration(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Validates VLAN assignment, database existence, and trunk allowed VLAN lists."""
    results = []
    text = f"{symptom}\n{topology_note}\n{show_output}"

    # Check for missing VLAN in trunk allowed list
    if "switchport trunk allowed vlan" in show_output.lower():
        # Match allowed VLAN numbers
        match = re.search(r'switchport trunk allowed vlan\s+([\d,\-]+)', show_output, re.IGNORECASE)
        if match:
            allowed = match.group(1)
            # Find VLAN referenced in topology or symptom
            vlan_ref = re.search(r'vlan\s+(\d+)', text, re.IGNORECASE)
            if vlan_ref:
                target_vlan = vlan_ref.group(1)
                # Check if target_vlan is in allowed string
                if target_vlan not in allowed.split(','):
                    results.append({
                        "rule": "vlan_trunk_allowed_check",
                        "status": "FAIL",
                        "severity": "HIGH",
                        "message": f"VLAN {target_vlan} is missing from trunk allowed VLAN list ({allowed})."
                    })

    # Check for VLAN missing in VLAN database (show vlan brief)
    if "show vlan" in text.lower() or "vlan 00" in text.lower() or "vlan" in symptom.lower():
        vlan_matches = re.findall(r'VLAN\s*(\d+)', text, re.IGNORECASE)
        if vlan_matches:
            target_vlan = vlan_matches[0]
            if "does not exist" in text.lower() or "missing" in text.lower() or ("show vlan" in show_output.lower() and f"00{target_vlan}" not in show_output and f" {target_vlan} " not in show_output):
                results.append({
                    "rule": "vlan_database_check",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "message": f"VLAN {target_vlan} is not present in switch VLAN database."
                })

    # Check for wrong access VLAN
    if "access vlan 1" in show_output.lower() and ("vlan 10" in text.lower() or "vlan 20" in text.lower() or "vlan 30" in text.lower()):
        results.append({
            "rule": "vlan_access_check",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": "Switchport interface left in default VLAN 1 instead of target access VLAN."
        })

    return results
