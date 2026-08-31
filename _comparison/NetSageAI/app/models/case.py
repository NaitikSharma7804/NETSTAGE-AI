"""SQLAlchemy model for Cases."""

from sqlalchemy import Column, Integer, String, Text
from database.database import Base


class CaseModel(Base):
    """Network Troubleshooting Case Entity."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(String(50), unique=True, index=True, nullable=False)
    symptom = Column(Text, nullable=False)
    topology_note = Column(Text, nullable=False)
    show_output = Column(Text, nullable=False)
    expected_fault = Column(Text, nullable=False)
    osi_layer = Column(String(20), nullable=False)
    concept = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    dataset_status = Column(String(20), default="SAMPLE", nullable=False)
