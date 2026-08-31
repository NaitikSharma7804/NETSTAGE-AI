# Evidence Analysis Prompt Component

Analyze the provided Cisco show outputs against observed symptoms:
1. Examine Interface status (up/up, up/down, administratively down, err-disabled).
2. Examine IP addressing, subnet masks, and default gateways for subnet boundary validity.
3. Examine VLAN databases and 802.1Q encapsulation tags on trunk and subinterfaces.
4. Examine Routing tables (RIB) for missing default routes (Gateway of last resort), OSPF adjacencies, and unreachable next-hops.
5. Examine Access Control Lists (ACLs) for implicit denies, inverted wildcard masks, and directional placement.
6. Isolate the exact command output line that reveals the root cause.