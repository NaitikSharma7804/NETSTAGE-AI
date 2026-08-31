REVIEWS = [
    {
        "review_id": "REV-001",
        "case_id": "NS-ACL-001",
        "diagnosis_id": "DIAG-NS-ACL-001-AUTO",
        "reviewer_name": "Senior Network Specialist - Alex Morgan",
        "status": "ACCEPTED",
        "ai_predicted_fault": "Outbound ACL 'BLOCK-OLD' on Gi0/0.10 only permits 192.168.20.0/24; VLAN 30 is dropped by implicit deny.",
        "corrected_diagnosis": "",
        "reviewer_reason": "AI accurately identified the implicit deny on standard ACL BLOCK-OLD as the root cause of packet drops from VLAN 30 to VLAN 10.",
        "ai_agreement": "TRUE",
        "created_at": "2026-08-20T09:15:00Z"
    },
    {
        "review_id": "REV-002",
        "case_id": "NS-VLAN-001",
        "diagnosis_id": "DIAG-NS-VLAN-001-AUTO",
        "reviewer_name": "Senior Network Specialist - Alex Morgan",
        "status": "ACCEPTED",
        "ai_predicted_fault": "VLAN 20 does not exist in the switch VLAN database, causing access port Fa0/5 to remain inactive/down.",
        "corrected_diagnosis": "",
        "reviewer_reason": "Correct diagnosis. The VLAN database output clearly omitted VLAN 20, causing port status 'inactive'.",
        "ai_agreement": "TRUE",
        "created_at": "2026-08-20T10:00:00Z"
    },
    # --- CORRECTION 1: AI claimed DNS failure, Human corrected to ACL issue ---
    {
        "review_id": "REV-003",
        "case_id": "NS-DNS-004",
        "diagnosis_id": "DIAG-NS-DNS-004-AUTO",
        "reviewer_name": "Lead Network Architect - Dr. Elena Vance",
        "status": "EDITED",
        "ai_predicted_fault": "Public DNS server 1.1.1.1 is offline or unreachable across the ISP WAN link.",
        "corrected_diagnosis": "Firewall extended ACL 'OUTSIDE-IN' permits TCP 53 but denies UDP 53 return traffic required for standard DNS queries.",
        "reviewer_reason": "AI hallucinated an external server outage without checking the show access-lists output, which showed rule 10 only permitting TCP 53 while UDP DNS responses hit rule 30 deny.",
        "ai_agreement": "FALSE",
        "created_at": "2026-08-20T11:30:00Z"
    },
    # --- CORRECTION 2: AI claimed Cable Fault / Physical Down, Human corrected to VTP domain mismatch ---
    {
        "review_id": "REV-004",
        "case_id": "NS-VLAN-005",
        "diagnosis_id": "DIAG-NS-VLAN-005-AUTO",
        "reviewer_name": "Junior Instructor - Priya Patel",
        "status": "REJECTED",
        "ai_predicted_fault": "Physical cabling defect between SW-Core and SW-Acc1 causing port shutdown.",
        "corrected_diagnosis": "VTP domain name case mismatch ('CISCO-LAB' vs 'cisco-lab') prevented VLAN 40 database synchronization.",
        "reviewer_reason": "Completely rejected AI hypothesis. Trunk link was up/up with 0 errors. VTP status clearly displayed domain case mismatch and revision 0.",
        "ai_agreement": "FALSE",
        "created_at": "2026-08-20T14:10:00Z"
    },
    # --- CORRECTION 3: AI claimed DHCP Pool Exhaustion, Human corrected to Missing IP Helper-Address ---
    {
        "review_id": "REV-005",
        "case_id": "NS-DHCP-001",
        "diagnosis_id": "DIAG-NS-DHCP-001-AUTO",
        "reviewer_name": "Senior Network Specialist - Alex Morgan",
        "status": "EDITED",
        "ai_predicted_fault": "DHCP Server at 192.168.50.10 has exhausted its IP allocation pool for VLAN 10.",
        "corrected_diagnosis": "Router subinterface Gi0/0.10 is missing the 'ip helper-address 192.168.50.10' DHCP relay configuration.",
        "reviewer_reason": "AI assumed server pool exhaustion without checking intermediate router configuration. Broadcast DHCP DISCOVER packets cannot cross subinterfaces without a relay agent.",
        "ai_agreement": "FALSE",
        "created_at": "2026-08-21T09:45:00Z"
    },
    # --- CORRECTION 4: AI claimed Transceiver Hardware Failure, Human corrected to BPDU Guard Err-Disable ---
    {
        "review_id": "REV-006",
        "case_id": "NS-ADV-004",
        "diagnosis_id": "DIAG-NS-ADV-004-AUTO",
        "reviewer_name": "Lead Network Architect - Dr. Elena Vance",
        "status": "EDITED",
        "ai_predicted_fault": "Transceiver hardware failure or bad RJ-45 termination on FastEthernet0/11.",
        "corrected_diagnosis": "Spanning-Tree BPDU Guard shut down port Fa0/11 into err-disabled state after receiving BPDUs from an attached mini-switch.",
        "reviewer_reason": "AI missed the clear syslog message %SPANTREE-2-BLOCK_BPDUGUARD and status err-disabled. Corrected to BPDU Guard trigger.",
        "ai_agreement": "FALSE",
        "created_at": "2026-08-21T13:20:00Z"
    },
    # --- CORRECTION 5: AI claimed OSPF Dead Timer Mismatch, Human corrected to MTU Mismatch in EXSTART ---
    {
        "review_id": "REV-007",
        "case_id": "NS-ROUT-003",
        "diagnosis_id": "DIAG-NS-ROUT-003-AUTO",
        "reviewer_name": "Senior Network Specialist - Alex Morgan",
        "status": "EDITED",
        "ai_predicted_fault": "OSPF Hello and Dead timer interval mismatch between R1 and R3.",
        "corrected_diagnosis": "MTU mismatch on Gi0/1 (1500 bytes on R1 vs 1400 bytes on R3) causes OSPF DBD packet rejection, stalling adjacency in EXSTART.",
        "reviewer_reason": "Show interfaces showed MTU 1500 vs 1400, and show log explicitly flagged 'Bad Length in DBD'. OSPF timers were identical.",
        "ai_agreement": "FALSE",
        "created_at": "2026-08-22T10:15:00Z"
    },
    {
        "review_id": "REV-008",
        "case_id": "NS-GW-001",
        "diagnosis_id": "DIAG-NS-GW-001-AUTO",
        "reviewer_name": "Junior Instructor - Priya Patel",
        "status": "ACCEPTED",
        "ai_predicted_fault": "Host default gateway is configured as 10.1.20.1, outside the host subnet 10.1.10.0/24.",
        "corrected_diagnosis": "",
        "reviewer_reason": "Accurate deterministic diagnosis.",
        "ai_agreement": "TRUE",
        "created_at": "2026-08-22T11:00:00Z"
    },
    {
        "review_id": "REV-009",
        "case_id": "NS-NAT-001",
        "diagnosis_id": "DIAG-NS-NAT-001-AUTO",
        "reviewer_name": "Senior Network Specialist - Alex Morgan",
        "status": "ACCEPTED",
        "ai_predicted_fault": "WAN interface GigabitEthernet0/1 is missing 'ip nat outside' configuration.",
        "corrected_diagnosis": "",
        "reviewer_reason": "Directly confirmed by show ip nat statistics showing Outside interfaces: none.",
        "ai_agreement": "TRUE",
        "created_at": "2026-08-22T15:30:00Z"
    },
    {
        "review_id": "REV-010",
        "case_id": "NS-TRUNK-001",
        "diagnosis_id": "DIAG-NS-TRUNK-001-AUTO",
        "reviewer_name": "Lead Network Architect - Dr. Elena Vance",
        "status": "ACCEPTED",
        "ai_predicted_fault": "Native VLAN mismatch across trunk link (VLAN 1 on SW1 vs VLAN 99 on SW2).",
        "corrected_diagnosis": "",
        "reviewer_reason": "CDP log and show interfaces trunk clearly prove the native VLAN discrepancy.",
        "ai_agreement": "TRUE",
        "created_at": "2026-08-23T09:00:00Z"
    }
]