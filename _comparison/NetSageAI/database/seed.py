"""Database seed utility to initialize cases and responsible AI records from CSV."""

import csv
import json
from pathlib import Path
from sqlalchemy.orm import Session
from database.database import engine, Base, SessionLocal
from app.models.case import CaseModel
from app.models.diagnosis import DiagnosisModel
from app.models.review import ReviewModel


from sqlalchemy import inspect, text


def run_migrations(engine):
    """Executes safe SQLite column migrations for existing tables."""
    inspector = inspect(engine)
    with engine.connect() as conn:
        if "cases" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("cases")]
            if "dataset_status" not in columns:
                conn.execute(text("ALTER TABLE cases ADD COLUMN dataset_status VARCHAR(20) DEFAULT 'SAMPLE'"))
                conn.commit()

        if "diagnoses" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("diagnoses")]
            if "review_status" not in columns:
                conn.execute(text("ALTER TABLE diagnoses ADD COLUMN review_status VARCHAR(30) DEFAULT 'Pending Review'"))
            if "dataset_status" not in columns:
                conn.execute(text("ALTER TABLE diagnoses ADD COLUMN dataset_status VARCHAR(30) DEFAULT 'SAMPLE'"))
            if "ai_mode" not in columns:
                conn.execute(text("ALTER TABLE diagnoses ADD COLUMN ai_mode VARCHAR(20) DEFAULT 'mock'"))
            if "evidence_grounding_status" not in columns:
                conn.execute(text("ALTER TABLE diagnoses ADD COLUMN evidence_grounding_status VARCHAR(30) DEFAULT 'Unverified'"))
            if "grounded_evidence" not in columns:
                conn.execute(text("ALTER TABLE diagnoses ADD COLUMN grounded_evidence TEXT"))
            conn.commit()

        if "reviews" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("reviews")]
            if "record_type" not in columns:
                conn.execute(text("ALTER TABLE reviews ADD COLUMN record_type VARCHAR(30) DEFAULT 'REAL_TEAM_REVIEW'"))
            conn.commit()


def seed_database():
    """Seeds SQLite database from data/cases.csv if empty and runs migrations."""
    run_migrations(engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Cases
        existing_cases = db.query(CaseModel).count()
        if existing_cases == 0:
            csv_path = Path(__file__).parent.parent / "data" / "cases.csv"
            if csv_path.exists():
                with open(csv_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        case_obj = CaseModel(
                            case_id=row["case_id"],
                            symptom=row["symptom"],
                            topology_note=row["topology_note"],
                            show_output=row["show_output"],
                            expected_fault=row["expected_fault"],
                            osi_layer=row["osi_layer"],
                            concept=row["concept"],
                            severity=row["severity"],
                            dataset_status=row.get("dataset_status", "SAMPLE")
                        )
                        db.add(case_obj)
                db.commit()

        # 2. Seed Initial Reviews / Responsible AI Log if empty
        existing_reviews = db.query(ReviewModel).count()
        if existing_reviews == 0:
            log_path = Path(__file__).parent.parent / "data" / "responsible_ai_log.csv"
            if log_path.exists():
                with open(log_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, start=1):
                        # Create dummy diagnosis to link
                        diag = DiagnosisModel(
                            case_id=row["case_id"],
                            symptom="Sample symptom",
                            topology_note="Sample topology",
                            show_output="Sample CLI",
                            root_cause=row["ai_diagnosis"],
                            confidence=0.80,
                            osi_layer="Layer 3",
                            evidence=json.dumps(["Initial AI hypothesis"]),
                            next_command="show ip interface brief",
                            fix_steps=json.dumps(["Initial AI proposed fix"]),
                            rule_results=json.dumps([]),
                            review_status=row.get("human_decision", "Pending Review"),
                            dataset_status="SAMPLE",
                            ai_mode="mock",
                            evidence_grounding_status="Verified",
                            grounded_evidence=json.dumps([{"evidence": "Initial AI hypothesis", "grounded": True, "source": "rule_findings"}])
                        )
                        db.add(diag)
                        db.flush()

                        rev = ReviewModel(
                            diagnosis_id=diag.id,
                            case_id=row["case_id"],
                            status=row["human_decision"],
                            reviewer_notes=row.get("reason", "Sample evaluation"),
                            original_ai_response=json.dumps({"root_cause": row["ai_diagnosis"]}),
                            final_human_diagnosis=row["correction"],
                            reason=row.get("reason", ""),
                            lesson=row.get("lesson", ""),
                            record_type=row.get("record_type", "DEVELOPMENT_EXAMPLE")
                        )
                        db.add(rev)
                db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")
