# Few-Shot Example: ACL Implicit Deny

### Input
Symptom: PC in VLAN 30 can ping gateway 192.168.30.1 but cannot reach server 192.168.10.50 in VLAN 10.
Show Output:
R1# show access-lists
Standard IP access list BLOCK-OLD
    10 permit 192.168.20.0, wildcard bits 0.0.0.255 (42 matches)
    (implicit deny any matches: 128)

R1# show running-config interface GigabitEthernet0/0.10
interface GigabitEthernet0/0.10
 ip access-group BLOCK-OLD out

### Output 
```json
{
  "root_cause": "Outbound standard ACL BLOCK-OLD on subinterface Gi0/0.10 only permits 192.168.20.0/24; packets from VLAN 30 (192.168.30.0/24) are blocked by the implicit deny any rule.",
  "confidence": "high",
  "osi_layer": "Layer 3 (Network)",
  "affected_component": "R1 / GigabitEthernet0/0.10 / ACL BLOCK-OLD",
  "evidence": [
    {
      "source": "show access-lists",
      "observation": "Standard IP access list BLOCK-OLD only permits 192.168.20.0/24 with 128 implicit deny matches",
      "relevance": "VLAN 30 packets attempting to exit Gi0/0.10 towards the server hit the implicit deny."
    },
    {
      "source": "show running-config interface Gi0/0.10",
      "observation": "ip access-group BLOCK-OLD out applied to VLAN 10 interface",
      "relevance": "Proves the ACL is filtering egress traffic destined to the server."
    }
  ],
  "next_command": "show access-lists BLOCK-OLD",
  "fix_steps": [
    "R1(config)# ip access-list standard BLOCK-OLD",
    "R1(config-std-nacl)# 20 permit 192.168.30.0 0.0.0.255",
    "R1(config-std-nacl)# exit"
  ],
  "alternative_causes": [
    "Routing issue between VLAN 30 and VLAN 10 (ruled out because connected routes exist)",
    "Server 192.168.10.50 offline (ruled out by ACL drop match counters)"
  ]
}
```