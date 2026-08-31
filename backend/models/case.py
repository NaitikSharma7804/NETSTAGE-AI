"""
SQLAlchemy ORM Data Models for NetSage AI.
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.database.database import Base


class CaseModel(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    symptom = Column(Text, nullable=False)
    topology_note = Column(Text, default="")
    show_outputs = Column(Text, nullable=False)
    expected_fault = Column(Text, nullable=False)
    osi_layer = Column(String(64), default="Layer 3 (Network)")
    concept = Column(String(64), index=True, nullable=False)
    severity = Column(String(32), default="Medium")
    difficulty = Column(String(32), default="Medium")
    expected_next_command = Column(String(256), default="")
    expected_fix = Column(Text, default="")
    verification_method = Column(Text, default="")
    tags = Column(String(256), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnoses = relationship("DiagnosisModel", back_populates="case", cascade="all, delete-orphan")


class DiagnosisModel(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(String(64), unique=True, index=True, nullable=False)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=True)
    root_cause = Column(Text, nullable=False)
    confidence = Column(String(32), nullable=False)
    osi_layer = Column(String(64), nullable=False)
    affected_component = Column(String(128), default="")
    evidence_json = Column(Text, default="[]")
    next_command = Column(String(256), default="")
    fix_steps_json = Column(Text, default="[]")
    alternative_causes_json = Column(Text, default="[]")
    raw_response = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("CaseModel", back_populates="diagnoses")
    rule_results = relationship("RuleResultModel", back_populates="diagnosis", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReviewModel", back_populates="diagnosis", cascade="all, delete-orphan")
    verifications = relationship("VerificationModel", back_populates="diagnosis", cascade="all, delete-orphan")


class RuleResultModel(Base):
    __tablename__ = "rule_results"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(String(64), ForeignKey("diagnoses.diagnosis_id"), nullable=False)
    rule_id = Column(String(64), nullable=False)
    rule_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    severity = Column(String(32), default="INFO")
    message = Column(Text, nullable=False)
    evidence = Column(Text, default="")
    recommendation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnosis = relationship("DiagnosisModel", back_populates="rule_results")


class HumanReviewModel(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String(64), unique=True, index=True, nullable=False)
    diagnosis_id = Column(String(64), ForeignKey("diagnoses.diagnosis_id"), nullable=False)
    case_id = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False)  # ACCEPTED, EDITED, REJECTED
    reviewer_name = Column(String(128), default="Network Engineer")
    ai_predicted_fault = Column(Text, default="")
    corrected_diagnosis = Column(Text, default="")
    reviewer_reason = Column(Text, nullable=False)
    ai_agreement = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnosis = relationship("DiagnosisModel", back_populates="human_reviews")


class VerificationModel(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(64), unique=True, index=True, nullable=False)
    diagnosis_id = Column(String(64), ForeignKey("diagnoses.diagnosis_id"), nullable=False)
    case_id = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False)  # PASS, FAIL
    verification_command = Column(String(256), default="")
    verification_output = Column(Text, nullable=False)
    tester_notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnosis = relationship("DiagnosisModel", back_populates="verifications")


class LLMRunModel(Base):
    __tablename__ = "llm_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    provider = Column(String(64), nullable=False)
    model = Column(String(64), nullable=False)
    prompt_version = Column(String(32), default="v1.2.0")
    case_id = Column(String(64), nullable=True)
    execution_time_ms = Column(Integer, default=0)
    status = Column(String(32), default="SUCCESS")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)