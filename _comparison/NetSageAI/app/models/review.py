"""SQLAlchemy model for Human Reviews."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from database.database import Base


class ReviewModel(Base):
    """Human Oversight Review Entity."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    diagnosis_id = Column(Integer, index=True, nullable=False)
    case_id = Column(String(50), index=True, nullable=True)
    status = Column(String(20), nullable=False)  # Accepted, Edited, Rejected
    reviewer_notes = Column(Text, nullable=True)
    original_ai_response = Column(Text, nullable=False)  # JSON string of original AI diagnosis
    final_human_diagnosis = Column(Text, nullable=False)  # Final accepted/edited diagnosis
    reason = Column(Text, nullable=True)
    lesson = Column(Text, nullable=True)
    record_type = Column(String(30), default="REAL_TEAM_REVIEW", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
