"""
Analytics Service for NetSage AI Dashboard.
Uses Pandas for real-time aggregation of cases, diagnoses, reviews, and verifications.
"""

import os
import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.models.case import CaseModel, DiagnosisModel, HumanReviewModel, VerificationModel, LLMRunModel


class AnalyticsService:
    """Generates analytical summaries for dashboard visualizations."""

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        total_cases = db.query(CaseModel).count()
        total_diagnoses = db.query(DiagnosisModel).count()
        total_reviews = db.query(HumanReviewModel).count()
        total_verifications = db.query(VerificationModel).count()
        total_llm_runs = db.query(LLMRunModel).count()

        # If DB cases is 0, check cases.csv count
        if total_cases == 0 and os.path.exists("data/cases.csv"):
            df_c = pd.read_csv("data/cases.csv")
            total_cases = len(df_c)

        # Reviews Breakdown
        reviews = db.query(HumanReviewModel).all()
        if reviews:
            rev_df = pd.DataFrame([{
                "status": r.status,
                "ai_agreement": r.ai_agreement,
                "reviewer_name": r.reviewer_name
            } for r in reviews])
            accepted = int((rev_df["status"] == "ACCEPTED").sum())
            edited = int((rev_df["status"] == "EDITED").sum())
            rejected = int((rev_df["status"] == "REJECTED").sum())
            agreement_rate = round((accepted / len(rev_df) * 100), 1) if len(rev_df) > 0 else 0.0
        elif os.path.exists("data/reviews.csv"):
            df_r = pd.read_csv("data/reviews.csv")
            accepted = int((df_r["status"] == "ACCEPTED").sum())
            edited = int((df_r["status"] == "EDITED").sum())
            rejected = int((df_r["status"] == "REJECTED").sum())
            agreement_rate = round((accepted / len(df_r) * 100), 1) if len(df_r) > 0 else 0.0
            total_reviews = len(df_r)
        else:
            accepted, edited, rejected, agreement_rate = 0, 0, 0, 0.0

        # Verifications Breakdown
        verifs = db.query(VerificationModel).all()
        if verifs:
            v_df = pd.DataFrame([{"status": v.status} for v in verifs])
            v_pass = int((v_df["status"] == "PASS").sum())
            v_fail = int((v_df["status"] == "FAIL").sum())
            v_rate = round((v_pass / len(v_df) * 100), 1) if len(v_df) > 0 else 0.0
        else:
            v_pass, v_fail, v_rate = 0, 0, 0.0

        # Concept & Severity counts from cases
        if os.path.exists("data/cases.csv"):
            df_cases = pd.read_csv("data/cases.csv")
            concept_dist = df_cases["concept"].value_counts().to_dict()
            severity_dist = df_cases["severity"].value_counts().to_dict()
            difficulty_dist = df_cases["difficulty"].value_counts().to_dict()
        else:
            concept_dist, severity_dist, difficulty_dist = {}, {}, {}

        return {
            "metrics": {
                "total_cases": total_cases,
                "total_diagnoses": total_diagnoses,
                "total_reviews": total_reviews,
                "accepted_count": accepted,
                "edited_count": edited,
                "rejected_count": rejected,
                "ai_agreement_rate_pct": agreement_rate,
                "verification_pass_count": v_pass,
                "verification_fail_count": v_fail,
                "verification_success_rate_pct": v_rate,
                "total_llm_runs": total_llm_runs
            },
            "concept_distribution": concept_dist,
            "severity_distribution": severity_dist,
            "difficulty_distribution": difficulty_dist,
            "review_status_distribution": {
                "ACCEPTED": accepted,
                "EDITED": edited,
                "REJECTED": rejected
            }
        }
