"""Evidence Grounding Validation Engine for NetSage AI.

Inspects AI evidence statements and verifies whether they are grounded in:
1. Symptom & Topology notes
2. Cisco IOS show command outputs
3. Deterministic rule findings
"""

import re
from typing import List, Dict, Any


def GroundEvidenceItem(
    evidence_text: str,
    symptom: str,
    topology_note: str,
    show_output: str,
    rule_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Verifies a single evidence statement against case sources."""
    if not evidence_text or not evidence_text.strip():
        return {"evidence": evidence_text, "grounded": False, "source": None}

    ev_clean = evidence_text.strip().lower()

    # 1. Check against Deterministic Rule Findings
    for r in rule_results:
        rule_name = r.get("rule", "").lower()
        msg = r.get("message", "").lower()
        if rule_name in ev_clean or any(word in ev_clean for word in msg.split() if len(word) > 4):
            return {"evidence": evidence_text, "grounded": True, "source": "rule_findings"}

    # 2. Check against Cisco CLI Show Output
    show_clean = show_output.lower() if show_output else ""
    # Extract interface names (e.g., gi0/0.30, fa0/1)
    ifaces = re.findall(r'\b(?:gi|fa|se|gigabitethernet|fastethernet|serial)[\d/\.:\-]+\b', ev_clean)
    # Extract IP addresses
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', ev_clean)
    # Extract VLAN IDs
    vlans = re.findall(r'vlan\s*(\d+)', ev_clean)

    # Check key technical tokens
    tokens_found = 0
    total_tokens = 0

    if ifaces:
        total_tokens += len(ifaces)
        for iface in ifaces:
            if iface in show_clean or iface.replace("gigabitethernet", "gi").replace("fastethernet", "fa") in show_clean:
                tokens_found += 1

    if ips:
        total_tokens += len(ips)
        for ip in ips:
            if ip in show_clean or ip in (symptom.lower() + topology_note.lower()):
                tokens_found += 1

    if vlans:
        total_tokens += len(vlans)
        for v in vlans:
            if v in show_clean or f"vlan {v}" in (symptom.lower() + topology_note.lower()):
                tokens_found += 1

    # Check general phrase overlap (words > 3 chars)
    ev_words = [w for w in re.findall(r'\w+', ev_clean) if len(w) > 3 and w not in ["show", "output", "configured", "interface"]]
    matching_words = [w for w in ev_words if w in show_clean or w in symptom.lower() or w in topology_note.lower()]

    if total_tokens > 0 and tokens_found > 0:
        return {"evidence": evidence_text, "grounded": True, "source": "show_output"}

    if ev_words and (len(matching_words) / len(ev_words)) >= 0.35:
        source_name = "show_output" if any(w in show_clean for w in matching_words) else "symptom_topology"
        return {"evidence": evidence_text, "grounded": True, "source": source_name}

    return {"evidence": evidence_text, "grounded": False, "source": None}


def evaluate_evidence_grounding(
    evidence_list: List[str],
    symptom: str,
    topology_note: str,
    show_output: str,
    rule_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluates all evidence items and determines overall grounding status."""
    if not evidence_list:
        return {
            "status": "Unverified",
            "grounded_items": []
        }

    grounded_items = []
    grounded_count = 0

    for ev in evidence_list:
        g_res = GroundEvidenceItem(ev, symptom, topology_note, show_output, rule_results)
        grounded_items.append(g_res)
        if g_res["grounded"]:
            grounded_count += 1

    total = len(evidence_list)
    if grounded_count == total and total > 0:
        overall_status = "Verified"
    elif grounded_count > 0:
        overall_status = "Partially Verified"
    else:
        overall_status = "Unverified"

    return {
        "status": overall_status,
        "grounded_items": grounded_items
    }
