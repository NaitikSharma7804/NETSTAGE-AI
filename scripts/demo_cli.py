"""
NetSage AI Interactive Terminal Demo Runner.
Demonstrates the full end-to-end pipeline in the CLI:
Symptom -> Rule Engine -> AI Diagnosis -> Evidence Fusion -> Human Review -> Fix -> Verification -> Database
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("."))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.database.database import SessionLocal, engine, Base
from backend.services.diagnosis_service import DiagnosisService
from backend.services.review_service import ReviewService
from backend.services.verification_service import VerificationService
from ai.schemas.diagnosis import DiagnosisRequest, HumanReviewRequest, VerificationRequest, ReviewStatus, VerificationStatus
from rule_engine.models import RuleStatus


def print_banner():
    print("""
================================================================================
                       NETSAGE AI CLI DEMONSTRATOR
         "AI-Assisted Network Troubleshooting with Human Review"
================================================================================
    """)


async def run_scenario_demo(case_id: str = "NS-ACL-001", simulate_misdiagnosis: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print(f"\n[STEP 1] Loading Troubleshooting Scenario: {case_id}")
    
    # Load case
    import csv
    with open("data/cases.csv", "r", encoding="utf-8") as f:
        cases = {row["case_id"]: row for row in csv.DictReader(f)}
    
    case = cases.get(case_id)
    if not case:
        print(f"Error: Case {case_id} not found.")
        return

    print(f"Title       : {case['title']}")
    print(f"Concept     : {case['concept']} | Severity: {case['severity']} | Difficulty: {case['difficulty']}")
    print(f"Topology    : {case['topology_note']}")
    print(f"Symptom     : {case['symptom']}")
    print("\n--- CISCO SHOW COMMAND EVIDENCE ---")
    print(case['show_outputs'])
    print("-----------------------------------")

    print("\n[STEP 2] Running Deterministic Rule Engine & AI Inference...")
    req = DiagnosisRequest(
        case_id=case_id,
        symptom=case['symptom'],
        topology_note=case['topology_note'],
        show_outputs=case['show_outputs']
    )

    fused_diag, rule_run, fusion_meta = await DiagnosisService.diagnose_case(
        req, db=db, simulate_misdiagnosis=simulate_misdiagnosis
    )

    print(f"\n[RULE ENGINE RESULTS] Total Evaluated: {rule_run.total_rules_evaluated}")
    for r in rule_run.results:
        if r.status in [RuleStatus.FAIL, RuleStatus.WARNING]:
            print(f"  ❌ [{r.status.value}] {r.rule_id}: {r.rule_name} -> {r.message}")

    print("\n[AI STRUCTURED DIAGNOSIS]")
    print(f"  Diagnosis ID       : {fused_diag.diagnosis_id}")
    print(f"  Confidence Level   : {fused_diag.confidence.value.upper()}")
    print(f"  OSI Layer          : {fused_diag.osi_layer}")
    print(f"  Root Cause         : {fused_diag.root_cause}")
    print(f"  Next Check Command : {fused_diag.next_command}")
    print("  Fix Steps:")
    for step in fused_diag.fix_steps:
        print(f"    - {step}")

    print("\n[STEP 3] HUMAN-IN-THE-LOOP SAFETY GATE")
    print("  Decision Options: [1] ACCEPT  [2] EDIT  [3] REJECT")
    
    if simulate_misdiagnosis:
        print("  -> Simulating Human Expert Correction (EDIT)...")
        status = ReviewStatus.EDITED
        corr = "Firewall extended ACL 'OUTSIDE-IN' permits TCP 53 but denies UDP 53 return DNS traffic."
        reason = "Show access-lists showed rule 10 only permitting TCP 53 while UDP DNS queries hit rule 30 deny."
    else:
        print("  -> Simulating Human Review Approval (ACCEPT)...")
        status = ReviewStatus.ACCEPTED
        corr = ""
        reason = "Evidence in show access-lists confirms the implicit deny match counter matches packet drops."

    rev_req = HumanReviewRequest(
        diagnosis_id=fused_diag.diagnosis_id,
        case_id=case_id,
        status=status,
        reviewer_name="Senior Network Specialist - Alex Morgan",
        corrected_diagnosis=corr,
        reviewer_reason=reason
    )
    rev_res = ReviewService.process_review(rev_req, db)
    print(f"  [SAVED] Review Record: {rev_res.review_id} | Status: {rev_res.status.value}")

    print("\n[STEP 4] Cisco Packet Tracer Fix & Closed-Loop Verification")
    print("  Applying configuration in Packet Tracer...")
    print("  Executing connectivity test: 'ping 192.168.10.50' (5/5 packets received)")

    verif_req = VerificationRequest(
        diagnosis_id=fused_diag.diagnosis_id,
        case_id=case_id,
        status=VerificationStatus.PASS,
        verification_command="ping 192.168.10.50",
        verification_output="Sending 5, 100-byte ICMP Echos to 192.168.10.50, timeout is 2 seconds: !!!!! (100% success)"
    )
    verif_res = VerificationService.process_verification(verif_req, db)
    print(f"  [SAVED] Verification: {verif_res.verification_id} | Result: {verif_res.status.value}")

    print("\n================================================================================")
    print("                PIPELINE EXECUTION COMPLETED SUCCESSFULLY!                      ")
    print("================================================================================\n")
    db.close()


if __name__ == "__main__":
    print_banner()
    case_to_run = sys.argv[1] if len(sys.argv) > 1 else "NS-ACL-001"
    sim_flag = "--misdiag" in sys.argv
    asyncio.run(run_scenario_demo(case_to_run, simulate_misdiagnosis=sim_flag))