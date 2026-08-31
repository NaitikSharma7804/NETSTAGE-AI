"""
DHCP and DHCP Relay Validation Rules.
Detects missing IP helper-address on subinterfaces, DHCP pool exhaustion, and missing excluded addresses.
"""

import re
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_missing_dhcp_helper(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects missing ip helper-address when client is in a separate VLAN/subnet from central DHCP server."""
    apipa = bool(re.search(r"169\.254\.\d+\.\d+", show_outputs))
    has_subifs = bool(re.search(r"interface\s+GigabitEthernet[\d\/\.]+\.\d+", show_outputs))
    has_helper = bool(re.search(r"ip helper-address", show_outputs, re.IGNORECASE))
    is_central_dhcp = bool(re.search(r"DHCP Server|helper-address|relay", topology_note + " " + show_outputs, re.IGNORECASE))

    if apipa and has_subifs and not has_helper and is_central_dhcp:
        return RuleCheckResult(
            rule_id="DHCP_001",
            rule_name="Missing IP Helper-Address (DHCP Relay)",
            category="DHCP",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message="Client received APIPA address (169.254.x.x) and router subinterface is missing 'ip helper-address <dhcp-server-ip>' to relay broadcast requests across subnets.",
            evidence="Client IP: 169.254.x.x (APIPA) | Router subinterfaces lack 'ip helper-address'",
            recommendation="Configure 'ip helper-address <DHCP_Server_IP>' on the client's router subinterface."
        )

    return RuleCheckResult(
        rule_id="DHCP_001",
        rule_name="DHCP Relay Helper-Address Check",
        category="DHCP",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="DHCP relay configuration is valid or not required.",
        evidence="",
        recommendation=""
    )


def check_dhcp_pool_exhaustion(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects DHCP pool utilization at 100% with no available leases."""
    util_match = re.search(r"Utilization mark \(high\/low\)\s*:\s*(100\s*\/\s*\d+)", show_outputs, re.IGNORECASE)
    total_match = re.search(r"Total addresses\s*:\s*(\d+)\s+Leased addresses\s*:\s*(\d+)", show_outputs, re.IGNORECASE)

    if util_match or (total_match and total_match.group(1) == total_match.group(2)):
        total = total_match.group(1) if total_match else "Max"
        return RuleCheckResult(
            rule_id="DHCP_002",
            rule_name="DHCP Pool Exhaustion",
            category="DHCP",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.HIGH,
            message=f"DHCP pool is 100% exhausted ({total} addresses leased out of {total}), preventing new clients from obtaining IP leases.",
            evidence=f"DHCP Pool utilization: 100% ({total}/{total} leased)",
            recommendation="Expand the DHCP pool subnet mask or configure a larger IP range."
        )

    return RuleCheckResult(
        rule_id="DHCP_002",
        rule_name="DHCP Pool Capacity Check",
        category="DHCP",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="DHCP pool has available capacity for leases.",
        evidence="",
        recommendation=""
    )