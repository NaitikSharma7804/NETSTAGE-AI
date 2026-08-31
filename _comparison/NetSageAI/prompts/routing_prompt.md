# Routing Troubleshooting Guidance

Focus on Layer 3 routing concepts:
- Static routes (`ip route <dest> <mask> <next-hop|interface>`)
- Default Gateway / Gateway of last resort (`ip default-gateway`, `0.0.0.0 0.0.0.0`)
- Inter-VLAN subinterfaces (`interface Gi0/0.<vlan>`, `encapsulation dot1Q <vlan>`)
- OSPF configuration & adjacency timers (Hello/Dead mismatch, Area mismatch, Passive-interface)
- EIGRP configuration (AS number mismatch, Network advertisement statements)
- Interface IP/subnet mask mismatches
