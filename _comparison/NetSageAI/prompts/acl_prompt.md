# ACL Troubleshooting Guidance

Focus on Layer 4 / Layer 3 Access Control Lists:
- Standard ACLs (`access-list <1-99> permit/deny`)
- Extended ACLs (`access-list <100-199> permit/deny <proto> <src> <dst> eq <port>`)
- Inbound vs Outbound application (`ip access-group <id> in|out`)
- VTY Line restriction (`access-class <id> in`)
- Implicit deny at end of ACL rules
- Wildcard mask precision
