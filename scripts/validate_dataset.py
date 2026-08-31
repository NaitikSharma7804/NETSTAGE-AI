"""
NetSage AI Canonical Dataset Validator
Validates schema integrity, completeness, and value domains of cases.csv.
"""

import csv
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_COLUMNS = [
    "case_id", "title", "symptom", "topology_note", "show_outputs",
    "expected_fault", "osi_layer", "concept", "severity", "difficulty",
    "expected_next_command", "expected_fix", "verification_method", "tags"
]

VALID_CONCEPTS = {
    "VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL",
    "NAT", "Wireless", "Trunking", "Interface"
}

VALID_SEVERITIES = {"Low", "Medium", "High", "Critical"}
REQUIRED_CONCEPTS = {"VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"}
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}

def validate_dataset(filepath="data/cases.csv"):
    if not os.path.exists(filepath):
        print(f"[ERROR] Dataset file not found: {filepath}")
        return False
        
    errors = []
    case_ids = set()
    concept_counts = {}
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Check column headers
        if not reader.fieldnames:
            print("[ERROR] CSV file is empty.")
            return False
            
        missing_cols = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            
        row_count = 0
        for idx, row in enumerate(reader, start=1):
            row_count += 1
            cid = row.get("case_id", "").strip()
            
            if not cid:
                errors.append(f"Row {idx}: Empty case_id")
            elif cid in case_ids:
                errors.append(f"Row {idx}: Duplicate case_id '{cid}'")
            else:
                case_ids.add(cid)
                
            # Non-empty checks
            for field in ["title", "symptom", "topology_note", "show_outputs", "expected_fault", "expected_fix"]:
                val = row.get(field, "").strip()
                if not val:
                    errors.append(f"Row {idx} ({cid}): Field '{field}' is empty")
                    
            # Concept check
            concept = row.get("concept", "").strip()
            if concept not in VALID_CONCEPTS:
                errors.append(f"Row {idx} ({cid}): Invalid concept '{concept}'. Allowed: {VALID_CONCEPTS}")
            else:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
                
            # Severity check
            sev = row.get("severity", "").strip()
            if sev not in VALID_SEVERITIES:
                errors.append(f"Row {idx} ({cid}): Invalid severity '{sev}'. Allowed: {VALID_SEVERITIES}")
                
            # Difficulty check
            diff = row.get("difficulty", "").strip()
            if diff not in VALID_DIFFICULTIES:
                errors.append(f"Row {idx} ({cid}): Invalid difficulty '{diff}'. Allowed: {VALID_DIFFICULTIES}")

    if row_count < 30:
        errors.append(f"Dataset contains only {row_count} cases. Minimum requirement is 30.")

    missing_required_concepts = REQUIRED_CONCEPTS - set(concept_counts)
    if missing_required_concepts:
        errors.append(
            "Dataset is missing required troubleshooting concepts: "
            + ", ".join(sorted(missing_required_concepts))
        )

    print("\n==================================================")
    print("           NETSAGE AI DATASET VALIDATION          ")
    print("==================================================")
    print(f"Total Cases Checked : {row_count}")
    print(f"Unique Case IDs     : {len(case_ids)}")
    print("\nConcept Distribution:")
    for c, cnt in sorted(concept_counts.items()):
        print(f"  - {c:<12}: {cnt} cases")
        
    if errors:
        print("\n[VALIDATION FAILED] Errors found:")
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    else:
        print(f"\n[VALIDATION PASSED] All {row_count} cases passed integrity validation successfully!\n")
        return True

if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
