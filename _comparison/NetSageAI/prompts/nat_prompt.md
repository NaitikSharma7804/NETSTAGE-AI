# NAT Troubleshooting Guidance

Focus on Layer 3 Network Address Translation:
- `ip nat inside` on internal LAN interfaces
- `ip nat outside` on external WAN interface
- Dynamic NAT / PAT Overload (`ip nat inside source list <acl> interface <if> overload`)
- ACL matching internal LAN source IPs correctly
- Static NAT mappings (`ip nat inside source static <local> <global>`)
- Verification via `show ip nat translations` and `show ip nat statistics`
