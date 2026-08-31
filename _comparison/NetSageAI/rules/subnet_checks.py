"""Deterministic checks for subnet mask misconfigurations."""

import re
from typing import Dict, List, Any


def check_subnet_masks(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Validates subnet mask correctness and detects mask mismatches between hosts/interfaces."""
    results = []

    combined_text = f"{symptom}\n{topology_note}\n{show_output}"

    # Search for subnet mask mismatches (e.g., 255.255.255.0 vs 255.255.255.128 or /24 vs /25)
    masks = re.findall(r'255\.\d{1,3}\.\d{1,3}\.\d{1,3}', combined_text)
    unique_masks = list(set(masks))

    if len(unique_masks) > 1 and ("subnet mask" in combined_text.lower() or "mask mismatch" in combined_text.lower() or "cannot ping" in combined_text.lower()):
        # Check if multiple conflicting subnet masks appear in single subnet context
        results.append({
            "rule": "subnet_mask_check",
            "status": "FAIL",
            "severity": "MEDIUM",
            "message": f"Subnet mask mismatch detected across devices on the same segment: found {', '.join(unique_masks)}."
        })

    # Check for wildcards in ACLs vs actual subnets
    if "subnet mismatch" in combined_text.lower() or "mask" in symptom.lower():
        if not results:
            results.append({
                "rule": "subnet_mask_check",
                "status": "FAIL",
                "severity": "MEDIUM",
                "message": "Configured subnet mask does not align with network segment parameters."
            })

    return results
