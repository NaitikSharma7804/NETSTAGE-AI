"""
Analytics & Health API Router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.services.analytics_service import AnalyticsService
from backend.services.evaluation_service import EvaluationService

router = APIRouter(prefix="", tags=["Analytics"])


@router.get("/health")
def health_check():
    """Application health and readiness probe."""
    return {
        "status": "healthy",
        "service": "NetSage AI Backend",
        "version": "1.2.0",
        "framework": "FastAPI + SQLAlchemy + Pydantic"
    }


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Provides Pandas-computed metrics for dashboard charts."""
    return AnalyticsService.get_dashboard_summary(db)


@router.get("/evaluation")
def get_evaluation(db: Session = Depends(get_db)):
    """Provides AI vs Ground Truth evaluation benchmarking metrics."""
    return EvaluationService.calculate_metrics(db)