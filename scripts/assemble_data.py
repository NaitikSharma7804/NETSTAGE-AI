import csv
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import scripts.case_batch1 as b1
import scripts.case_batch2 as b2
import scripts.case_batch3 as b3
import scripts.case_reviews as rev

def main():
    os.makedirs("data", exist_ok=True)
    all_cases = b1.CASES + b2.CASES + b3.CASES
    
    # 1. Write data/cases.csv
    cases_file = os.path.join("data", "cases.csv")
    fieldnames = [
        "case_id", "title", "symptom", "topology_note", "show_outputs",
        "expected_fault", "osi_layer", "concept", "severity", "difficulty",
        "expected_next_command", "expected_fix", "verification_method", "tags"
    ]
    with open(cases_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in all_cases:
            writer.writerow(c)
            
    print(f"Successfully assembled {len(all_cases)} cases into {cases_file}")
    
    # 2. Write data/reviews.csv
    reviews_file = os.path.join("data", "reviews.csv")
    rev_fields = [
        "review_id", "case_id", "diagnosis_id", "reviewer_name", "status",
        "ai_predicted_fault", "corrected_diagnosis", "reviewer_reason",
        "ai_agreement", "created_at"
    ]
    with open(reviews_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rev_fields)
        writer.writeheader()
        for r in rev.REVIEWS:
            writer.writerow(r)
            
    print(f"Successfully assembled {len(rev.REVIEWS)} reviews into {reviews_file}")

if __name__ == "__main__":
    main()