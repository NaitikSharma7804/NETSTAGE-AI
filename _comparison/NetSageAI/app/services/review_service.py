"""Business logic service for human reviews, responsible AI logging, and analytics aggregation."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.case import CaseModel
from app.models.diagnosis import DiagnosisModel
from app.models.review import ReviewModel
from app.schemas.review_schema import ReviewCreate, AnalyticsSummary


def create_human_review(db: Session, review_data: ReviewCreate) -> ReviewModel:
    """Processes human review (Accept, Edit, Reject), updates diagnosis review_status, and appends to CSV log."""
    
    # 1. Fetch original diagnosis and update its review_status
    diagnosis = db.query(DiagnosisModel).filter(DiagnosisModel.id == review_data.diagnosis_id).first()
    if diagnosis:
        diagnosis.review_status = review_data.status
        db.add(diagnosis)

    original_ai = {
        "root_cause": diagnosis.root_cause if diagnosis else "Unknown",
        "confidence": diagnosis.confidence if diagnosis else 0.0,
        "osi_layer": diagnosis.osi_layer if diagnosis else "Unknown"
    }

    # 2. Save review to DB with record_type = REAL_TEAM_REVIEW
    db_review = ReviewModel(
        diagnosis_id=review_data.diagnosis_id,
        case_id=review_data.case_id or (diagnosis.case_id if diagnosis else None),
        status=review_data.status,
        reviewer_notes=review_data.reviewer_notes or "",
        original_ai_response=json.dumps(original_ai),
        final_human_diagnosis=review_data.final_human_diagnosis,
        reason=review_data.reason or "",
        lesson=review_data.lesson or "",
        record_type="REAL_TEAM_REVIEW"
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 3. Append to data/responsible_ai_log.csv if status is Edited or Rejected
    if review_data.status in ["Edited", "Rejected"]:
        log_path = Path(__file__).parent.parent.parent / "data" / "responsible_ai_log.csv"
        file_exists = log_path.exists()
        with open(log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["case_id", "ai_diagnosis", "human_decision", "correction", "reason", "lesson", "record_type"])
            writer.writerow([
                review_data.case_id or f"DIAG-{review_data.diagnosis_id}",
                original_ai["root_cause"],
                review_data.status,
                review_data.final_human_diagnosis,
                review_data.reason or review_data.reviewer_notes or "Human correction applied",
                review_data.lesson or "Review guidelines applied",
                "REAL_TEAM_REVIEW"
            ])

    return db_review


def get_all_reviews(db: Session) -> List[ReviewModel]:
    """Retrieves all human review entries."""
    return db.query(ReviewModel).order_by(ReviewModel.created_at.desc()).all()


def get_responsible_ai_logs() -> List[Dict[str, str]]:
    """Reads data/responsible_ai_log.csv into list of dictionaries."""
    log_path = Path(__file__).parent.parent.parent / "data" / "responsible_ai_log.csv"
    logs = []
    if log_path.exists():
        with open(log_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append(row)
    return logs


def calculate_analytics_summary(db: Session) -> AnalyticsSummary:
    """Computes comprehensive analytics metrics across cases, diagnoses, and reviews.
    
    Agreement Rate Formula: Accepted / (Accepted + Edited + Rejected) across reviewed diagnoses ONLY.
    Pending reviews do NOT count toward agreement.
    Development example log rows do NOT count toward real human corrections.
    """
    total_cases = db.query(CaseModel).count()
    diagnoses_run = db.query(DiagnosisModel).count()
    pending_review_count = db.query(DiagnosisModel).filter(DiagnosisModel.review_status == "Pending Review").count()

    reviews = db.query(ReviewModel).all()

    accepted_count = sum(1 for r in reviews if r.status == "Accepted")
    edited_count = sum(1 for r in reviews if r.status == "Edited")
    rejected_count = sum(1 for r in reviews if r.status == "Rejected")
    
    total_reviewed = accepted_count + edited_count + rejected_count
    agreement_rate = round((accepted_count / total_reviewed * 100), 1) if total_reviewed > 0 else 0.0

    # Count ONLY REAL_TEAM_REVIEW corrections (excluding DEVELOPMENT_EXAMPLE)
    real_human_corrections = sum(
        1 for r in reviews 
        if getattr(r, "record_type", "REAL_TEAM_REVIEW") == "REAL_TEAM_REVIEW" and r.status in ["Edited", "Rejected"]
    )
    # Also check CSV logs for REAL_TEAM_REVIEW
    csv_logs = get_responsible_ai_logs()
    real_csv_corrections = sum(1 for row in csv_logs if row.get("record_type") == "REAL_TEAM_REVIEW")
    real_human_corrections = max(real_human_corrections, real_csv_corrections)

    high_severity_count = db.query(CaseModel).filter(CaseModel.severity == "High").count()

    # Breakdown by concept
    cases = db.query(CaseModel).all()
    by_concept = {}
    by_severity = {}
    by_osi = {}

    for c in cases:
        by_concept[c.concept] = by_concept.get(c.concept, 0) + 1
        by_severity[c.severity] = by_severity.get(c.severity, 0) + 1
        by_osi[c.osi_layer] = by_osi.get(c.osi_layer, 0) + 1

    return AnalyticsSummary(
        total_cases=total_cases,
        diagnoses_run=diagnoses_run,
        pending_review_count=pending_review_count,
        accepted_count=accepted_count,
        edited_count=edited_count,
        rejected_count=rejected_count,
        agreement_rate=agreement_rate,
        real_human_corrections=real_human_corrections,
        high_severity_count=high_severity_count,
        by_concept=by_concept,
        by_severity=by_severity,
        by_osi_layer=by_osi
    )
