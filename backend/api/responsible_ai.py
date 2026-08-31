"""
Responsible AI & Audit API Router.
"""

import csv
import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.case import HumanReviewModel

router = APIRouter(prefix="/responsible-ai", tags=["Responsible AI"])


@router.get("")
def get_responsible_ai_summary(db: Session = Depends(get_db)):
    """
    Returns statistics and audited instances where humans corrected AI diagnoses.
    """
    reviews = db.query(HumanReviewModel).all()
    corrections = []

    total_reviewed = len(reviews)
    if reviews:
        for r in reviews:
            if r.status in ["EDITED", "REJECTED"]:
                corrections.append({
                    "review_id": r.review_id,
                    "case_id": r.case_id,
                    "diagnosis_id": r.diagnosis_id,
                    "reviewer_name": r.reviewer_name,
                    "status": r.status,
                    "ai_predicted_fault": r.ai_predicted_fault,
                    "corrected_diagnosis": r.corrected_diagnosis,
                    "reviewer_reason": r.reviewer_reason,
                    "created_at": r.created_at.isoformat() if r.created_at else ""
                })
    elif os.path.exists("data/reviews.csv"):
        with open("data/reviews.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_demo_reviews = list(reader)
            total_reviewed = len(all_demo_reviews)
            for row in all_demo_reviews:
                if row.get("status") in ["EDITED", "REJECTED"]:
                    corrections.append(row)

    total_corrected = len(corrections)
    correction_rate = round((total_corrected / total_reviewed * 100), 1) if total_reviewed > 0 else 0.0

    return {
        "summary": {
            "total_reviews": total_reviewed,
            "total_corrected_cases": total_corrected,
            "human_oversight_rate_pct": 100.0,
            "correction_rate_pct": correction_rate,
            "principle": "AI ASSISTS. RULES VALIDATE. HUMANS DECIDE. VERIFICATION CONFIRMS."
        },
        "corrected_cases": corrections
    }
