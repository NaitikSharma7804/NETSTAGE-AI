# DHCP Troubleshooting Guidance

Focus on Layer 7 / Layer 3 DHCP concepts:
- DHCP Pool definition (`ip dhcp pool <name>`)
- Default router parameter (`default-router <ip>`)
- Excluded addresses (`ip dhcp excluded-address`)
- IP Helper Address (`ip helper-address <server-ip>` on router subinterfaces)
- DHCP Relay Agent functionality across subnets
- APIPA address assignment (169.254.x.x) on host indicates DHCP failure
