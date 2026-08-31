"""Deterministic checks for Duplicate IP addresses and IP configurations."""

import re
from typing import Dict, List, Any


def check_duplicate_ips(show_output: str, symptom: str, topology_note: str) -> List[Dict[str, Any]]:
    """Detects duplicate IP addresses across ARP tables or show outputs."""
    results = []

    text_to_check = f"{symptom}\n{topology_note}\n{show_output}"

    # Search for duplicate IP keyword or multiple MACs mapped to same IP in ARP table
    if "duplicate ip" in text_to_check.lower() or "conflict" in text_to_check.lower():
        # Match IP addresses in text
        ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text_to_check)
        unique_ips = list(set(ip_matches))
        
        # Check if ARP table shows duplicate MACs for an IP
        arp_entries = {}
        for line in show_output.splitlines():
            # e.g., Internet  192.168.1.10   0   0001.c711.1111  ARPA  VLAN10
            match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})\s+[\d\-]+\s+([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})', line)
            if match:
                ip, mac = match.group(1), match.group(2)
                if ip in arp_entries and arp_entries[ip] != mac:
                    results.append({
                        "rule": "duplicate_ip_check",
                        "status": "FAIL",
                        "severity": "HIGH",
                        "message": f"Duplicate IP address conflict detected for {ip} (MAC {arp_entries[ip]} vs {mac})."
                    })
                else:
                    arp_entries[ip] = mac

        if not results and ("duplicate ip" in text_to_check.lower() or "conflict" in text_to_check.lower()):
            conflict_ip = unique_ips[0] if unique_ips else "192.168.1.x"
            results.append({
                "rule": "duplicate_ip_check",
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"IP address conflict reported for address in network scope ({conflict_ip})."
            })

    return results
