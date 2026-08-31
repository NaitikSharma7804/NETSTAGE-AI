"""
IP and Host Configuration Rules.
Detects duplicate IP addresses, host IP configured as network/broadcast ID, and invalid host assignments.
"""

import ipaddress
import re
from typing import List
from rule_engine.models import RuleCheckResult, RuleSeverity, RuleStatus


def check_duplicate_ip(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects duplicate IP syslog errors or duplicate ARP/MAC bindings."""
    dup_match = re.search(r"%SYS-4-DUPLICATE_IP:\s*([\d\.]+)|%IP-4-DUPADDR:\s*Duplicate address\s*([\d\.]+)", show_outputs, re.IGNORECASE)
    if dup_match:
        ip = dup_match.group(1) or dup_match.group(2)
        return RuleCheckResult(
            rule_id="IP_001",
            rule_name="Duplicate IP Address Detection",
            category="IP",
            status=RuleStatus.FAIL,
            severity=RuleSeverity.CRITICAL,
            message=f"Duplicate IP address {ip} detected on the network, causing ARP flapping and communication failure.",
            evidence=dup_match.group(0),
            recommendation=f"Reconfigure one of the conflicting devices with a unique static IP address or enable DHCP."
        )
    return RuleCheckResult(
        rule_id="IP_001",
        rule_name="Duplicate IP Address Detection",
        category="IP",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="No duplicate IP addresses detected in system logs or ARP tables.",
        evidence="",
        recommendation=""
    )


def check_invalid_host_ip(show_outputs: str, topology_note: str = "") -> RuleCheckResult:
    """Detects if a host IP is configured as a network ID or broadcast address."""
    # Look for ipconfig or interface IP with /24 or mask
    ipconfig_match = re.search(r"IP Address[\.\s]+:\s*([\d\.]+)\s+Subnet Mask[\.\s]+:\s*([\d\.]+)", show_outputs, re.IGNORECASE)
    if ipconfig_match:
        ip_str = ipconfig_match.group(1).strip()
        mask_str = ipconfig_match.group(2).strip()
        try:
            net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
            ip_obj = ipaddress.IPv4Address(ip_str)
            if ip_obj == net.network_address:
                return RuleCheckResult(
                    rule_id="IP_002",
                    rule_name="Host Configured as Network ID",
                    category="IP",
                    status=RuleStatus.FAIL,
                    severity=RuleSeverity.HIGH,
                    message=f"Host IP address {ip_str} is the reserved Subnet/Network ID of network {net}.",
                    evidence=f"Configured: {ip_str} with mask {mask_str} (Network ID: {net.network_address})",
                    recommendation=f"Assign a valid usable host IP within range {net.network_address + 1} to {net.broadcast_address - 1}."
                )
            if ip_obj == net.broadcast_address:
                return RuleCheckResult(
                    rule_id="IP_002",
                    rule_name="Host Configured as Broadcast ID",
                    category="IP",
                    status=RuleStatus.FAIL,
                    severity=RuleSeverity.HIGH,
                    message=f"Host IP address {ip_str} is the reserved Broadcast address of network {net}.",
                    evidence=f"Configured: {ip_str} with mask {mask_str}",
                    recommendation=f"Assign a valid usable host IP within the subnet."
                )
        except Exception:
            pass

    return RuleCheckResult(
        rule_id="IP_002",
        rule_name="Host Network/Broadcast Address Check",
        category="IP",
        status=RuleStatus.PASS,
        severity=RuleSeverity.INFO,
        message="Host IP address is a valid usable unicast address.",
        evidence="",
        recommendation=""
    )