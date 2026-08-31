"""Local submission-readiness checks for the NetSage AI assignment."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_CONCEPTS = {"VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"}
REQUIRED_PROMPT_FIELDS = {"root_cause", "confidence", "evidence", "next_command", "fix_steps"}


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_submission() -> bool:
    errors: list[str] = []
    cases = read_csv("data/cases.csv")
    reviews = read_csv("data/reviews.csv")

    if len(cases) < 30:
        errors.append(f"cases.csv has {len(cases)} cases; at least 30 are required.")
    missing_concepts = REQUIRED_CONCEPTS - {row.get("concept", "").strip() for row in cases}
    if missing_concepts:
        errors.append("Missing required concepts: " + ", ".join(sorted(missing_concepts)))

    statuses = {row.get("status", "").strip() for row in reviews}
    missing_statuses = {"ACCEPTED", "EDITED", "REJECTED"} - statuses
    if missing_statuses:
        errors.append("Review log is missing statuses: " + ", ".join(sorted(missing_statuses)))

    corrections = [row for row in reviews if row.get("status") in {"EDITED", "REJECTED"}]
    if len(corrections) < 5:
        errors.append(f"Review log has {len(corrections)} corrections; at least 5 are required.")
    for row in corrections:
        if not row.get("corrected_diagnosis", "").strip() or not row.get("reviewer_reason", "").strip():
            errors.append(f"Correction {row.get('review_id', '<unknown>')} needs a correction and reviewer reason.")

    prompt_text = (ROOT / "ai/prompts/diagnose_prompt.md").read_text(encoding="utf-8").lower()
    missing_prompt_fields = {field for field in REQUIRED_PROMPT_FIELDS if field not in prompt_text}
    if missing_prompt_fields:
        errors.append("Diagnosis prompt is missing fields: " + ", ".join(sorted(missing_prompt_fields)))
    example_files = list((ROOT / "ai/prompts/examples").glob("*.md"))
    if len(example_files) < 2:
        errors.append("At least two worked prompt examples are required.")

    print("NetSage AI submission-readiness check")
    print(f"  Cases: {len(cases)}")
    print(f"  Human corrections: {len(corrections)}")
    print(f"  Worked prompt examples: {len(example_files)}")
    if errors:
        print("\nFAILED")
        for error in errors:
            print(f"  - {error}")
        return False

    print("\nPASSED: local submission artifacts satisfy the assignment checks.")
    print("Manual evidence still required: record the demo video and include the Packet Tracer files or screenshots used for the demonstrated cases.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if validate_submission() else 1)
