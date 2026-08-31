# NetSage AI - Dataset Specification

NetSage AI includes 40 canonical troubleshooting scenarios stored in `data/cases.csv`.

## Domain Breakdown
1. **VLAN (5 cases)**: Inactive ports, missing VLAN database IDs, access port wrong VLAN, voice VLAN conflicts, router-on-a-stick subinterface encapsulation, VTP domain case mismatches.
2. **Gateway & Subnet (4 cases)**: Gateway outside host subnet, host/router mask mismatches, duplicate IP address collisions, host assigned network ID.
3. **DHCP & Relay (5 cases)**: Missing `ip helper-address`, DHCP pool exhaustion, missing gateway exclusions, Option 3 gateway typos, untrusted DHCP snooping uplinks.
4. **DNS Resolution (4 cases)**: Mistyped host DNS IP, disabled domain lookup, missing authoritative A-records, firewall ACL blocking UDP port 53.
5. **Routing & Protocols (6 cases)**: Missing default static routes, OSPF area ID mismatches, OSPF MTU mismatch in EXSTART, unreachable static route next-hops, passive interface on transit links, asymmetric stateful TCP resets.
6. **Access Control Lists (5 cases)**: Implicit deny drops, inverted wildcard masks, inbound vs outbound directional misapplication, standard ACL over-filtering near source, missing TCP `established` keyword for return sessions.
7. **NAT & PAT (4 cases)**: Missing `ip nat outside` interface boundary, omitted `overload` keyword in PAT, NAT source ACL missing subnet, static NAT port forwarding IP typo.
8. **Wireless LAN (3 cases)**: WPA2-PSK key mismatch, AP multi-SSID uplink access vs trunk mode, 2.4GHz radio administratively shutdown.
9. **Trunking & Interface (4 cases)**: 802.1Q Native VLAN mismatch, trunk allowed VLAN pruning, interface administratively shutdown, duplex mismatch with late collisions.
10. **Advanced Scenarios (5 cases)**: DTP dynamic auto negotiation lock, HSRP VIP mismatch, EtherChannel PAgP vs static mode mismatch, BPDU Guard err-disable, static route inverted subnet mask.