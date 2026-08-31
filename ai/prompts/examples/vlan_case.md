# Few-Shot Example: VLAN Misconfiguration

### Input
Symptom: Host PC-A connected to Switch SW1 port Fa0/5 cannot communicate in VLAN 20.
Show Output:
SW1# show vlan brief
1 default active Fa0/1, Fa0/2, Fa0/3, Fa0/4, Fa0/6
10 Sales active Fa0/7, Fa0/8

SW1# show interfaces FastEthernet0/5 status
Port Name Status Vlan Duplex Speed Type
Fa0/5 PC-A-Link inactive 20 auto auto 10/100BaseTX

### Output
```json
{
  "root_cause": "VLAN 20 does not exist in the switch VLAN database, causing access port Fa0/5 to remain in an inactive/down state.",
  "confidence": "high",
  "osi_layer": "Layer 2 (Data Link)",
  "affected_component": "SW1 / FastEthernet0/5 / VLAN Database",
  "evidence": [
    {
      "source": "show vlan brief",
      "observation": "VLAN 20 is not listed in active VLANs table",
      "relevance": "Access ports assigned to non-existent VLANs cannot forward frames."
    },
    {
      "source": "show interfaces FastEthernet0/5 status",
      "observation": "Port status is inactive with Vlan 20",
      "relevance": "Confirms the port is disabled at Layer 2 due to missing VLAN."
    }
  ],
  "next_command": "show vlan brief",
  "fix_steps": [
    "SW1(config)# vlan 20",
    "SW1(config-vlan)# name Engineering",
    "SW1(config-vlan)# exit"
  ],
  "alternative_causes": [
    "Interface Fa0/5 administratively shutdown (ruled out by status 'inactive')",
    "Bad physical cable (ruled out by link detection)"
  ]
}
```