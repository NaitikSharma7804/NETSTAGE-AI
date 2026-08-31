"""
NetSage AI Automated Evaluation Engine.
Evaluates AI diagnostic output against ground truth across all 40 cases.
Calculates concept agreement, rule detection rate, and stores benchmark metrics.
"""

import asyncio
import csv
import os
import re
import sys

sys.path.insert(0, os.path.abspath("."))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rule_engine.engine import rule_engine
from ai.providers.mock import MockLLMProvider
from ai.schemas.diagnosis import DiagnosisRequest


async def evaluate_all_cases():
    cases_file = os.path.join("data", "cases.csv")
    if not os.path.exists(cases_file):
        print("[ERROR] cases.csv not found.")
        return

    with open(cases_file, "r", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    print("==================================================")
    print("      NETSAGE AI BATCH BENCHMARK EVALUATION       ")
    print("==================================================")
    print(f"Total Cases to Evaluate: {len(cases)}\n")

    provider = MockLLMProvider()
    results = []
    concept_stats = {}

    exact_matches = 0
    rule_detections = 0

    for idx, c in enumerate(cases, start=1):
        cid = c["case_id"]
        concept = c["concept"]
        expected_fault = c["expected_fault"]

        if concept not in concept_stats:
            concept_stats[concept] = {"total": 0, "correct": 0, "rule_flags": 0}
        concept_stats[concept]["total"] += 1

        # 1. Evaluate with Rule Engine
        rule_run = rule_engine.evaluate(c["show_outputs"], c["topology_note"], c["symptom"])
        failed_or_warn = [r for r in rule_run.results if r.status.value in ["FAIL", "WARNING"]]
        if failed_or_warn:
            rule_detections += 1
            concept_stats[concept]["rule_flags"] += 1

        # 2. Evaluate with AI Provider (Mock / Ground Truth blind)
        req = DiagnosisRequest(
            case_id=cid,
            symptom=c["symptom"],
            topology_note=c["topology_note"],
            show_outputs=c["show_outputs"],
            rule_results=rule_run.results
        )
        diag = await provider.generate_diagnosis(req)

        # 3. Check concept & keyword alignment (without revealing ground truth to AI during inference)
        diag_cause_lower = diag.root_cause.lower()
        expected_lower = expected_fault.lower()
        
        # Check semantic agreement
        tokens = [w for w in re.split(r"\W+", expected_lower) if len(w) > 3]
        matched_tokens = sum(1 for t in tokens if t in diag_cause_lower)
        is_agreement = (matched_tokens >= len(tokens) * 0.4) or (concept.lower() in diag_cause_lower)

        if is_agreement:
            exact_matches += 1
            concept_stats[concept]["correct"] += 1

        results.append({
            "case_id": cid,
            "title": c["title"],
            "concept": concept,
            "severity": c["severity"],
            "difficulty": c["difficulty"],
            "expected_fault": expected_fault,
            "ai_root_cause": diag.root_cause,
            "confidence": diag.confidence.value,
            "rule_flags_count": len(failed_or_warn),
            "is_agreement": is_agreement
        })

    # Save to data/evaluations.csv
    eval_csv_path = os.path.join("data", "evaluations.csv")
    with open(eval_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    agreement_pct = round((exact_matches / len(cases) * 100), 1)
    rule_det_pct = round((rule_detections / len(cases) * 100), 1)

    print(f"Overall AI Agreement Rate    : {agreement_pct}% ({exact_matches}/{len(cases)})")
    print(f"Deterministic Detection Rate : {rule_det_pct}% ({rule_detections}/{len(cases)})")
    print(f"Saved evaluation details to  : {eval_csv_path}\n")

    print("Concept Performance Breakdown:")
    for c, stat in sorted(concept_stats.items()):
        acc = round(stat["correct"] / stat["total"] * 100, 1)
        r_rate = round(stat["rule_flags"] / stat["total"] * 100, 1)
        print(f"  - {c:<12}: AI Agreement {acc:>5}% | Rule Triggers {r_rate:>5}% ({stat['correct']}/{stat['total']} cases)")

    print("\n[BENCHMARK COMPLETE] Evaluation finished successfully.\n")

if __name__ == "__main__":
    asyncio.run(evaluate_all_cases())