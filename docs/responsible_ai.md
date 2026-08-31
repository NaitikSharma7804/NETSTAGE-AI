# NetSage AI - Responsible AI Governance

## Core Human-in-the-Loop Mandate
AI algorithms in network operations can experience hallucinations, overconfidence, and misinterpretations of complex multi-vendor CLI outputs. NetSage AI enforces four non-negotiable safety guardrails:

1. **Zero Autonomous Command Execution**: The AI is prohibited from modifying live routers, switches, or firewalls.
2. **Mandatory Human Review**: Every AI diagnostic proposition must be reviewed by a human engineer via **ACCEPT**, **EDIT**, or **REJECT** actions.
3. **Transparent Auditing of AI Mistakes**: NetSage AI deliberately showcases and logs scenarios where the AI was wrong.
4. **Closed-Loop Verification**: Even accepted fixes must be confirmed with ping or show command tests.

## 5 Documented Human Correction Scenarios

These are controlled lab-review scenarios, with matching entries in `data/reviews.csv`. They demonstrate the required correction workflow; they are not represented as production-network incidents.

### 1. Case `NS-DNS-004`: UDP 53 Blocked by Firewall
- **🤖 Flawed AI Diagnosis**: "Public DNS server 1.1.1.1 is offline across ISP link."
- **👤 Human Expert Correction**: "Firewall extended ACL OUTSIDE-IN permits TCP 53 but drops UDP 53 return DNS traffic."
- **🔍 Reviewer Reason**: Show access-lists showed rule 10 only permitting TCP 53 while UDP DNS queries hit rule 30 deny.

### 2. Case `NS-VLAN-005`: VTP Domain Mismatch
- **🤖 Flawed AI Diagnosis**: "Physical cabling defect between SW-Core and SW-Acc1."
- **👤 Human Expert Correction**: "VTP domain name case mismatch ('CISCO-LAB' vs 'cisco-lab') prevented database sync."
- **🔍 Reviewer Reason**: Physical link was up/up with 0 CRC errors. VTP status clearly displayed domain case mismatch.

### 3. Case `NS-DHCP-001`: Missing IP Helper-Address
- **🤖 Flawed AI Diagnosis**: "DHCP Server at 192.168.50.10 has exhausted its IP allocation pool."
- **👤 Human Expert Correction**: "Router subinterface Gi0/0.10 is missing 'ip helper-address 192.168.50.10'."
- **🔍 Reviewer Reason**: Broadcast DHCP DISCOVER packets cannot cross subinterfaces without a relay agent.

### 4. Case `NS-ADV-004`: BPDU Guard Err-Disable
- **🤖 Flawed AI Diagnosis**: "Transceiver hardware failure or bad RJ-45 termination on Fa0/11."
- **👤 Human Expert Correction**: "Spanning-Tree BPDU Guard put port Fa0/11 into err-disabled state after receiving BPDUs."
- **🔍 Reviewer Reason**: Syslog explicitly logged `%SPANTREE-2-BLOCK_BPDUGUARD` and interface status `err-disabled`.

### 5. Case `NS-ROUT-003`: OSPF MTU Mismatch
- **🤖 Flawed AI Diagnosis**: "OSPF Hello and Dead timer interval mismatch between R1 and R3."
- **👤 Human Expert Correction**: "MTU mismatch on Gi0/1 (1500 bytes on R1 vs 1400 bytes on R3) causes DBD drops in EXSTART."
- **🔍 Reviewer Reason**: MTU showed 1500 vs 1400, and syslog logged `Bad Length in DBD`.
