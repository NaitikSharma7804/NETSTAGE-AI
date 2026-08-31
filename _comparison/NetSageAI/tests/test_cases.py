"""Unit tests for cases.csv data integrity and case loading."""

import csv
from pathlib import Path


def test_cases_csv_exists_and_has_30_plus_records():
    cases_path = Path(__file__).parent.parent / "data" / "cases.csv"
    assert cases_path.exists(), "data/cases.csv must exist."

    with open(cases_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) >= 30, f"cases.csv must contain at least 30 cases. Found {len(reader)}."

        expected_columns = {"case_id", "symptom", "topology_note", "show_output", "expected_fault", "osi_layer", "concept", "severity"}
        actual_columns = set(reader[0].keys())
        assert expected_columns.issubset(actual_columns), f"cases.csv is missing required columns. Found {actual_columns}."


def test_cases_cover_all_8_required_concepts():
    cases_path = Path(__file__).parent.parent / "data" / "cases.csv"
    with open(cases_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        concepts = {row["concept"].strip() for row in reader}

    required_concepts = {"VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"}
    missing_concepts = required_concepts - concepts
    assert not missing_concepts, f"cases.csv missing coverage for required concepts: {missing_concepts}"
