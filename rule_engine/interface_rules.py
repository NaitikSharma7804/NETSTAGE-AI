"""
Interface Physical and Data Link State Rules.
Detects administratively down interfaces, duplex mismatches, err-disabled ports, and physical collision anomalies.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_interface_administratively_down(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects interfaces in 'administratively down' state."""
    admin_down_matches = re.findall(r"([\w\d\/\.]+)\s+[\w\.\d]+\s+YES\s+\w+\s+administratively down\s+down", show_outputs, re.IGNORECASE)
    if not admin_down_matches:
        admin_down_matches = re.findall(r"([\w\d\/\.]+)\s+is administratively down,\s+line protocol is down", show_outputs, re.IGNORECASE)

    if admin_down_matches:
        ifaces = ", ".join(set(admin_down_matches))
        return RuleCheckResult(
            rule_id="INT_001",
            rule_name="Interface Administratively Shutdown",
            category="Interface",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message=f"Interface(s) {ifaces} are administratively shutdown ('shutdown' command active in configuration).",
            evidence=f"Status: administratively down on {ifaces}",
            recommendation=f"Enable interface: 'interface <name>' -> 'no shutdown'."
        )

    return RuleCheckResult(
        rule_id="INT_001",
        rule_name="Interface Administrative Status Check",
        category="Interface",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="No interfaces are administratively shutdown.",
        evidence="",
        recommendation=""
    )


def check_duplex_mismatch(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects duplex mismatch (Half-Duplex vs Full-Duplex or late collisions)."""
    late_colls = re.search(r"(\d+)\s+late collisions?", show_outputs, re.IGNORECASE)
    half_match = re.search(r"Half-duplex,\s*100Mb\/s", show_outputs, re.IGNORECASE)
    full_match = re.search(r"Full-duplex,\s*100Mb\/s", show_outputs, re.IGNORECASE)

    if half_match and (full_match or (late_colls and int(late_colls.group(1)) > 50)):
        col_count = late_colls.group(1) if late_colls else "Significant"
        return RuleCheckResult(
            rule_id="INT_002",
            rule_name="Duplex Mismatch and Late Collisions",
            category="Interface",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Duplex mismatch detected: One side is operating in Half-Duplex with {col_count} late collisions while peer is Full-Duplex.",
            evidence=f"Half-duplex detected with {col_count} late collisions",
            recommendation="Configure both link endpoints to 'duplex full' or set both to 'duplex auto'."
        )

    return RuleCheckResult(
        rule_id="INT_002",
        rule_name="Interface Duplex & Collision Check",
        category="Interface",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Interface duplex settings are consistent; no late collision anomalies found.",
        evidence="",
        recommendation=""
    )


def check_err_disabled_port(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects ports in err-disabled state from BPDU guard or security violations."""
    err_match = re.search(r"(\w+\d+(?:\/\d+)*)\s+[\w\-]+\s+err-disabled", show_outputs, re.IGNORECASE)
    bpdu_match = re.search(r"%SPANTREE-2-BLOCK_BPDUGUARD|%PM-4-ERR_DISABLE:\s*bpduguard error", show_outputs, re.IGNORECASE)

    if err_match or bpdu_match:
        port = err_match.group(1) if err_match else "detected port"
        reason = "BPDU Guard triggered by unauthorized switch/BPDU frames" if bpdu_match else "error condition"
        return RuleCheckResult(
            rule_id="INT_003",
            rule_name="Port in Err-Disabled State",
            category="Interface",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Port {port} is in 'err-disabled' state due to {reason}.",
            evidence=bpdu_match.group(0) if bpdu_match else f"Port {port} status: err-disabled",
            recommendation=f"Remove the offending device, then recover port on {port} with 'shutdown' followed by 'no shutdown'."
        )

    return RuleCheckResult(
        rule_id="INT_003",
        rule_name="Err-Disabled Port Status Check",
        category="Interface",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="No switch ports are in err-disabled state.",
        evidence="",
        recommendation=""
    )