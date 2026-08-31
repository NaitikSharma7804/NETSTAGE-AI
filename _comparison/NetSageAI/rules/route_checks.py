"""Deterministic checks for Routing, static routes, OSPF timers, EIGRP AS numbers."""

import re
from typing import Dict, List, Any


def check_routing_configuration(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Checks for missing routes, gateway of last resort, OSPF hello mismatches, EIGRP AS mismatches."""
    results = []
    text = f"{symptom}\n{topology_note}\n{show_output}"

    # Check for Gateway of last resort is not set or missing static route
    if "gateway of last resort is not set" in show_output.lower() and ("external" in text.lower() or "internet" in text.lower() or "hq" in text.lower()):
        results.append({
            "rule": "route_default_missing",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Gateway of last resort is not set; missing default static route (0.0.0.0/0)."
        })

    # Check for OSPF Hello timer mismatch
    hello_times = re.findall(r'hello\s+(\d+)', text, re.IGNORECASE)
    if len(set(hello_times)) > 1 or ("ospf" in text.lower() and "init" in text.lower()):
        results.append({
            "rule": "route_ospf_hello_mismatch",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "OSPF Hello timer mismatch detected between neighbor interfaces on link segment."
        })

    # Check for EIGRP AS mismatch
    eigrp_as = re.findall(r'router eigrp\s+(\d+)', text, re.IGNORECASE)
    if len(set(eigrp_as)) > 1 or ("eigrp" in text.lower() and "neighbor" in text.lower() and "empty" in text.lower()):
        results.append({
            "rule": "route_eigrp_as_mismatch",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "EIGRP Autonomous System (AS) number mismatch detected between router instances."
        })

    # Check missing static route
    if "no static route" in text.lower() or ("show ip route" in show_output.lower() and "cannot reach" in text.lower() and len(show_output.splitlines()) < 8):
        results.append({
            "rule": "route_missing_static",
            "status": "FAIL",
            "severity": "HIGH",
            "message": "Target network prefix is absent from IP routing table."
        })

    return results
