"""Safe, offline assessment of a user-supplied target IP address.

This service deliberately does not send probes or make configuration changes.  A
single IP address is useful context, but it cannot prove reachability without a
source device, credentials, and captured network evidence.
"""

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict


class IPAssessmentService:
    """Build evidence-collection guidance for a target address."""

    @staticmethod
    def assess(target_ip: str) -> Dict[str, Any]:
        address = ip_address(target_ip.strip())
        is_unicast = not (
            address.is_multicast
            or address.is_unspecified
            or address.is_loopback
            or (isinstance(address, IPv4Address) and int(address) == 0xFFFFFFFF)
        )

        if address.is_loopback:
            scope = "loopback"
        elif address.is_unspecified:
            scope = "unspecified"
        elif address.is_multicast:
            scope = "multicast"
        elif address.is_link_local:
            scope = "link-local"
        elif address.is_private:
            scope = "private"
        elif address.is_global:
            scope = "public"
        else:
            scope = "reserved or special-use"

        commands = [
            f"ping {address}",
            f"show ip arp {address}" if isinstance(address, IPv4Address) else f"show ipv6 neighbors | include {address}",
            f"show ip route {address}" if isinstance(address, IPv4Address) else f"show ipv6 route {address}",
            "show ip interface brief",
        ]
        if address.is_link_local:
            commands.insert(0, "show ipv6 interface brief")

        finding = (
            "Address is a valid unicast diagnostic target; collect the listed commands from the relevant Cisco device."
            if is_unicast
            else "Address is not a normal unicast host target. Verify the intended host address before troubleshooting."
        )
        return {
            "target_ip": str(address),
            "ip_version": address.version,
            "scope": scope,
            "is_unicast_target": is_unicast,
            "finding": finding,
            "recommended_commands": commands,
            "safety_note": "No ping, scan, login, or configuration change was executed. Paste command output into NetSage for evidence-based diagnosis.",
        }
