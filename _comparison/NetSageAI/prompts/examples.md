# NetSage AI - Worked Troubleshooting Examples

## Example 1: Missing Inter-VLAN Subinterface (Layer 3 Routing)

### Input:
- **Symptom**: PC in VLAN 30 cannot reach Server in VLAN 10.
- **Topology**: PC on Switch SW1 Fa0/3 (VLAN 30), Router R1 connected via trunk Gi0/0.
- **Show Output**:
  ```text
  R1# show ip interface brief
  GigabitEthernet0/0       192.168.1.1     YES manual up        up
  GigabitEthernet0/0.10    192.168.10.1    YES manual up        up
  ```
- **Deterministic Rule Results**:
  ```json
  [{"rule": "vlan_route_check", "status": "FAIL", "severity": "HIGH", "message": "Subinterface for VLAN 30 is missing on router R1."}]
  ```

### AI Response:
```json
{
  "root_cause": "Missing subinterface GigabitEthernet0/0.30 on Router R1 for VLAN 30 inter-VLAN routing.",
  "confidence": 0.95,
  "osi_layer": "Layer 3",
  "evidence": [
    "show ip interface brief shows only subinterface Gi0/0.10 configured.",
    "Rule engine detected no subinterface configured for VLAN 30 IP subnet."
  ],
  "next_command": "show running-config interface GigabitEthernet0/0",
  "fix_steps": [
    "interface GigabitEthernet0/0.30",
    "encapsulation dot1Q 30",
    "ip address 192.168.30.1 255.255.255.0",
    "no shutdown"
  ]
}
```

---

## Example 2: Interface Shutdown (Layer 1 / Physical)

### Input:
- **Symptom**: Host cannot reach default gateway 10.1.1.1.
- **Topology**: Host connected directly to Router R1 Gi0/1.
- **Show Output**:
  ```text
  R1# show ip interface brief
  GigabitEthernet0/1       10.1.1.1        YES manual administratively down down
  ```
- **Deterministic Rule Results**:
  ```json
  [{"rule": "interface_check", "status": "FAIL", "severity": "HIGH", "message": "Interface GigabitEthernet0/1 is administratively down."}]
  ```

### AI Response:
```json
{
  "root_cause": "Interface GigabitEthernet0/1 is administratively shut down.",
  "confidence": 0.98,
  "osi_layer": "Layer 1",
  "evidence": [
    "show ip interface brief shows GigabitEthernet0/1 state as 'administratively down down'."
  ],
  "next_command": "show interface GigabitEthernet0/1",
  "fix_steps": [
    "interface GigabitEthernet0/1",
    "no shutdown"
  ]
}
```

---

## Example 3: DHCP Pool Missing Default Gateway (Layer 7 DHCP)

### Input:
- **Symptom**: Host receives IP address 192.168.1.15 via DHCP but cannot ping external addresses.
- **Topology**: Host connected to Router R1 running DHCP server.
- **Show Output**:
  ```text
  R1# show running-config | section dhcp
  ip dhcp pool LAN_POOL
   network 192.168.1.0 255.255.255.0
   dns-server 8.8.8.8
  ```
- **Deterministic Rule Results**:
  ```json
  [{"rule": "gateway_check", "status": "FAIL", "severity": "HIGH", "message": "DHCP pool LAN_POOL is missing default-router configuration."}]
  ```

### AI Response:
```json
{
  "root_cause": "DHCP pool LAN_POOL does not advertise a default gateway to DHCP clients.",
  "confidence": 0.92,
  "osi_layer": "Layer 7",
  "evidence": [
    "show running-config shows ip dhcp pool LAN_POOL without default-router command."
  ],
  "next_command": "show ip dhcp binding",
  "fix_steps": [
    "ip dhcp pool LAN_POOL",
    "default-router 192.168.1.1"
  ]
}
```
