"""
Dataset Integrity and Canonical Validation Tests.
"""

import pytest
from scripts.validate_dataset import validate_dataset


def test_canonical_dataset_validation():
    assert validate_dataset("data/cases.csv") is True