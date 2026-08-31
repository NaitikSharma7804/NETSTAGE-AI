"""
Database Seeding Script for NetSage AI.
Initializes SQLite database schema and imports canonical cases and historical reviews.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.abspath("."))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.database.database import engine, Base, SessionLocal
from backend.models.case import (
    CaseModel,
    DiagnosisModel,
    HumanReviewModel,
    VerificationModel
)

def seed_database():
    print("[INIT] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Cases from data/cases.csv
        cases_file = os.path.join("data", "cases.csv")
        if os.path.exists(cases_file):
            with open(cases_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cases_added = 0
                for row in reader:
                    existing = db.query(CaseModel).filter(CaseModel.case_id == row["case_id"]).first()
                    if not existing:
                        case_obj = CaseModel(
                            case_id=row["case_id"],
                            title=row["title"],
                            symptom=row["symptom"],
                            topology_note=row.get("topology_note", ""),
                            show_outputs=row["show_outputs"],
                            expected_fault=row["expected_fault"],
                            osi_layer=row.get("osi_layer", "Layer 3 (Network)"),
                            concept=row.get("concept", "General"),
                            severity=row.get("severity", "Medium"),
                            difficulty=row.get("difficulty", "Medium"),
                            expected_next_command=row.get("expected_next_command", ""),
                            expected_fix=row.get("expected_fix", ""),
                            verification_method=row.get("verification_method", ""),
                            tags=row.get("tags", "")
                        )
                        db.add(case_obj)
                        cases_added += 1
                db.commit()
                print(f"[SEEDED] Added {cases_added} cases into SQLite.")

        # 2. Seed Initial Reviews from data/reviews.csv
        reviews_file = os.path.join("data", "reviews.csv")
        if os.path.exists(reviews_file):
            with open(reviews_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                revs_added = 0
                for row in reader:
                    existing_rev = db.query(HumanReviewModel).filter(HumanReviewModel.review_id == row["review_id"]).first()
                    if not existing_rev:
                        diag_id = row.get("diagnosis_id", "DIAG-SEED")
                        diag = db.query(DiagnosisModel).filter(DiagnosisModel.diagnosis_id == diag_id).first()
                        if not diag:
                            diag = DiagnosisModel(
                                diagnosis_id=diag_id,
                                case_id=row.get("case_id"),
                                root_cause=row.get("ai_predicted_fault", "Seed diagnosis"),
                                confidence="high",
                                osi_layer="Layer 3 (Network)",
                                affected_component="Device"
                            )
                            db.add(diag)
                            db.flush()

                        rev_obj = HumanReviewModel(
                            review_id=row["review_id"],
                            diagnosis_id=diag_id,
                            case_id=row.get("case_id"),
                            status=row.get("status", "ACCEPTED"),
                            reviewer_name=row.get("reviewer_name", "Network Engineer"),
                            ai_predicted_fault=row.get("ai_predicted_fault", ""),
                            corrected_diagnosis=row.get("corrected_diagnosis", ""),
                            reviewer_reason=row.get("reviewer_reason", "Verified"),
                            ai_agreement=(row.get("ai_agreement", "TRUE").upper() == "TRUE")
                        )
                        db.add(rev_obj)
                        revs_added += 1
                db.commit()
                print(f"[SEEDED] Added {revs_added} reviews into SQLite.")

        # 3. Seed demo verification outcomes, including failures that show why
        # a human must re-check a fix rather than assume it worked.
        verifications_file = os.path.join("data", "verifications.csv")
        if os.path.exists(verifications_file):
            with open(verifications_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                verifications_added = 0
                for row in reader:
                    existing = db.query(VerificationModel).filter(
                        VerificationModel.verification_id == row["verification_id"]
                    ).first()
                    if not existing:
                        db.add(VerificationModel(
                            verification_id=row["verification_id"],
                            diagnosis_id=row["diagnosis_id"],
                            case_id=row.get("case_id"),
                            status=row["status"],
                            verification_command=row["verification_command"],
                            verification_output=row["verification_output"],
                            tester_notes=row.get("tester_notes", "")
                        ))
                        verifications_added += 1
                db.commit()
                print(f"[SEEDED] Added {verifications_added} verification outcomes into SQLite.")

        print("\n[DATABASE INITIALIZATION COMPLETE] netsage.db ready!\n")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
