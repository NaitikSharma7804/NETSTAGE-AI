"""
Routing Protocol and Static Route Validation Rules.
Detects missing default static routes, OSPF area mismatches, MTU mismatches (EXSTART), passive interface errors, and unreachable next-hops.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_missing_default_route(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects when internet access fails and gateway of last resort is not set."""
    gateway_not_set = re.search(r"Gateway of last resort is not set", show_outputs, re.IGNORECASE)
    has_internet_traffic = bool(re.search(r"8\.8\.8\.8|208\.67\.222\.222|internet|WAN", show_outputs + " " + topology_note, re.IGNORECASE))

    if gateway_not_set and has_internet_traffic:
        return RuleCheckResult(
            rule_id="ROUT_001",
            rule_name="Missing Default Route (Gateway of Last Resort Not Set)",
            category="Routing",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message="No default route exists in the routing table ('Gateway of last resort is not set'), causing packets for external/internet destinations to be dropped.",
            evidence="show ip route: Gateway of last resort is not set",
            recommendation="Configure default static route: 'ip route 0.0.0.0 0.0.0.0 <next-hop-ip | exit-interface>'."
        )

    return RuleCheckResult(
        rule_id="ROUT_001",
        rule_name="Default Route Availability Check",
        category="Routing",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Default route is configured or not required for local routing.",
        evidence="",
        recommendation=""
    )


def check_ospf_area_mismatch(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects OSPF area mismatches between interconnected routers."""
    areas = re.findall(r"Internet Address\s+[\d\.\/]+,\s*Area\s+(\d+)", show_outputs, re.IGNORECASE)
    if len(set(areas)) > 1:
        return RuleCheckResult(
            rule_id="ROUT_002",
            rule_name="OSPF Area ID Mismatch",
            category="Routing",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"OSPF Area ID mismatch detected across interconnect link: Router interfaces configured in different areas ({set(areas)}).",
            evidence=f"Configured Areas: {', '.join(set(areas))}",
            recommendation="Configure both interconnected router interfaces to the same OSPF Area (e.g. Area 0)."
        )

    return RuleCheckResult(
        rule_id="ROUT_002",
        rule_name="OSPF Area ID Consistency Check",
        category="Routing",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="OSPF Area IDs are consistent across interfaces.",
        evidence="",
        recommendation=""
    )


def check_ospf_mtu_mismatch(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects OSPF adjacency stuck in EXSTART/EXCHANGE due to MTU mismatch."""
    exstart = re.search(r"EXSTART\/", show_outputs, re.IGNORECASE)
    mtus = re.findall(r"MTU\s+(\d+)\s+bytes", show_outputs, re.IGNORECASE)

    if exstart and len(set(mtus)) > 1:
        return RuleCheckResult(
            rule_id="ROUT_003",
            rule_name="OSPF MTU Mismatch (Stuck in EXSTART)",
            category="Routing",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"OSPF adjacency stuck in EXSTART state due to interface MTU mismatch across the link (MTUs detected: {set(mtus)}).",
            evidence=f"State: EXSTART, Detected MTUs: {', '.join(set(mtus))}",
            recommendation="Set identical MTU on both interfaces ('ip mtu 1500') or configure 'ip ospf mtu-ignore'."
        )

    return RuleCheckResult(
        rule_id="ROUT_003",
        rule_name="OSPF MTU & Adjacency State Check",
        category="Routing",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="No OSPF MTU mismatch or EXSTART state lock detected.",
        evidence="",
        recommendation=""
    )


def check_unreachable_next_hop(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects static route next-hop not present in routing table (recursive failure)."""
    not_in_table = re.search(r"show ip route ([\d\.]+)\s+%\s+Network not in table", show_outputs, re.IGNORECASE)
    static_via = re.search(r"S\s+[\d\.\/]+\s+\[\d+\/\d+\]\s+via\s+([\d\.]+)", show_outputs, re.IGNORECASE)

    if not_in_table and static_via and not_in_table.group(1) == static_via.group(1):
        nh = not_in_table.group(1)
        return RuleCheckResult(
            rule_id="ROUT_004",
            rule_name="Static Route Next-Hop Unreachable",
            category="Routing",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"Static route next-hop IP {nh} is unreachable and does not exist in the routing table (recursive lookup failure).",
            evidence=f"via {nh} -> % Network not in table",
            recommendation=f"Update static route next-hop to a directly connected router interface IP on the transit network."
        )

    return RuleCheckResult(
        rule_id="ROUT_004",
        rule_name="Static Route Next-Hop Reachability Check",
        category="Routing",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Static route next-hop is reachable or no static route anomalies found.",
        evidence="",
        recommendation=""
    )