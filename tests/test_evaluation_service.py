"""
Evaluation and Metrics Calculation Tests.
"""

import pytest
from backend.services.evaluation_service import EvaluationService


def test_evaluation_metrics_calculation():
    metrics = EvaluationService.calculate_metrics()
    assert metrics["total_canonical_cases"] == 40
    assert metrics["human_acceptance_rate_pct"] >= 0.0
    assert "VLAN" in metrics["concept_distribution"]