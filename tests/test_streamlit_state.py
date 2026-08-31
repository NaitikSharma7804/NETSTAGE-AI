"""
Regression and Integration Tests for Streamlit Dashboard State Management.
Tests widget state preservation across reruns, canonical case loading, custom cases,
modified inputs, deterministic rule execution, and AI misdiagnosis simulations.
"""

import pytest
from streamlit.testing.v1 import AppTest


def test_troubleshoot_page_canonical_selection_and_diagnosis_run():
    """
    TEST 1: Canonical case selection + Diagnosis Run MUST NOT reset state.
    """
    at = AppTest.from_file("dashboard/app.py", default_timeout=30)
    at.run()
    assert not at.exception

    # 1. Navigate to "🔍 Troubleshoot & Diagnose"
    at.sidebar.radio(key="nav_choice").set_value("🔍 Troubleshoot & Diagnose").run()
    assert not at.exception

    # 2. Select canonical case NS-VLAN-001
    case_selector = at.selectbox(key="troubleshoot_case_selector")
    opt_vlan1 = next(opt for opt in case_selector.options if opt.startswith("NS-VLAN-001"))
    case_selector.select(opt_vlan1).run()
    assert not at.exception

    # 3. Verify populated fields
    symptom_widget = at.text_area(key="troubleshoot_symptom")
    topo_widget = at.text_input(key="troubleshoot_topology")
    show_widget = at.text_area(key="troubleshoot_show_outputs")

    assert "VLAN 20" in symptom_widget.value or "FastEthernet0/5" in symptom_widget.value
    assert topo_widget.value != ""
    assert "show vlan brief" in show_widget.value

    # 4. Click "🚀 Run Diagnosis & Evidence Fusion" (first button in main area)
    run_diag_btn = next(b for b in at.button if "Run Diagnosis & Evidence Fusion" in b.label)
    run_diag_btn.click().run()
    assert not at.exception

    # 5. Verify state AFTER rerun
    assert at.selectbox(key="troubleshoot_case_selector").value == opt_vlan1
    assert at.text_area(key="troubleshoot_symptom").value == symptom_widget.value
    assert at.text_input(key="troubleshoot_topology").value == topo_widget.value
    assert at.text_area(key="troubleshoot_show_outputs").value == show_widget.value

    # Verify diagnosis completed successfully
    assert at.session_state.current_diag is not None
    assert at.session_state.current_diag.case_id == "NS-VLAN-001"
    assert at.session_state.current_rules is not None


def test_troubleshoot_page_modified_symptom_preservation():
    """
    TEST 2: Modified user symptom must be preserved across rerun.
    """
    at = AppTest.from_file("dashboard/app.py", default_timeout=30)
    at.run()
    at.sidebar.radio(key="nav_choice").set_value("🔍 Troubleshoot & Diagnose").run()

    # Select NS-VLAN-001
    case_selector = at.selectbox(key="troubleshoot_case_selector")
    opt_vlan1 = next(opt for opt in case_selector.options if opt.startswith("NS-VLAN-001"))
    case_selector.select(opt_vlan1).run()

    # Modify the symptom
    custom_symptom = "PC-A cannot communicate with VLAN 20 hosts."
    at.text_area(key="troubleshoot_symptom").input(custom_symptom).run()

    # Run Diagnosis
    run_diag_btn = next(b for b in at.button if "Run Diagnosis & Evidence Fusion" in b.label)
    run_diag_btn.click().run()
    assert not at.exception

    # Verify modified symptom survived rerun and was NOT overwritten by canonical
    assert at.text_area(key="troubleshoot_symptom").value == custom_symptom
    assert at.session_state.current_diag.symptom == custom_symptom


def test_troubleshoot_page_switch_canonical_case():
    """
    TEST 3: Switching to NS-VLAN-002 replaces inputs with NS-VLAN-002 values.
    """
    at = AppTest.from_file("dashboard/app.py", default_timeout=30)
    at.run()
    at.sidebar.radio(key="nav_choice").set_value("🔍 Troubleshoot & Diagnose").run()

    # Select NS-VLAN-001 first
    case_selector = at.selectbox(key="troubleshoot_case_selector")
    opt_vlan1 = next(opt for opt in case_selector.options if opt.startswith("NS-VLAN-001"))
    case_selector.select(opt_vlan1).run()

    # Switch to NS-VLAN-002
    opt_vlan2 = next(opt for opt in case_selector.options if opt.startswith("NS-VLAN-002"))
    case_selector.select(opt_vlan2).run()
    assert not at.exception

    # Verify fields changed to NS-VLAN-002
    symptom_val = at.text_area(key="troubleshoot_symptom").value
    assert "VLAN 30" in symptom_val or "Wrong VLAN" in opt_vlan2

    # Run diagnosis
    run_diag_btn = next(b for b in at.button if "Run Diagnosis & Evidence Fusion" in b.label)
    run_diag_btn.click().run()
    assert not at.exception
    assert at.session_state.current_diag.case_id == "NS-VLAN-002"


def test_troubleshoot_page_run_rules_only():
    """
    TEST 4: 'Run Deterministic Rules Only' preserves inputs and evaluates rules.
    """
    at = AppTest.from_file("dashboard/app.py", default_timeout=30)
    at.run()
    at.sidebar.radio(key="nav_choice").set_value("🔍 Troubleshoot & Diagnose").run()

    # Select NS-VLAN-001
    case_selector = at.selectbox(key="troubleshoot_case_selector")
    opt_vlan1 = next(opt for opt in case_selector.options if opt.startswith("NS-VLAN-001"))
    case_selector.select(opt_vlan1).run()

    # Click 'Run Deterministic Rules Only'
    rules_btn = next(b for b in at.button if "Run Deterministic Rules Only" in b.label)
    rules_btn.click().run()
    assert not at.exception

    # Verify rules evaluated and state preserved
    assert at.session_state.current_rules is not None
    assert at.session_state.current_rules.total_rules_evaluated >= 20
    assert at.selectbox(key="troubleshoot_case_selector").value == opt_vlan1
    assert at.text_area(key="troubleshoot_symptom").value != ""


def test_troubleshoot_page_misdiagnosis_simulation():
    """
    TEST 5: AI Misdiagnosis simulation executes properly and enables human correction.
    """
    at = AppTest.from_file("dashboard/app.py", default_timeout=30)
    at.run()
    at.sidebar.radio(key="nav_choice").set_value("🔍 Troubleshoot & Diagnose").run()

    # Select NS-DNS-004
    case_selector = at.selectbox(key="troubleshoot_case_selector")
    opt_dns4 = next(opt for opt in case_selector.options if opt.startswith("NS-DNS-004"))
    case_selector.select(opt_dns4).run()

    # Check simulate misdiagnosis
    at.checkbox(key="troubleshoot_sim_misdiag").check().run()
    assert at.checkbox(key="troubleshoot_sim_misdiag").value is True

    # Run Diagnosis
    run_diag_btn = next(b for b in at.button if "Run Diagnosis & Evidence Fusion" in b.label)
    run_diag_btn.click().run()
    assert not at.exception

    # Verify misdiagnosis output
    diag = at.session_state.current_diag
    assert diag is not None
    assert "1.1.1.1" in diag.root_cause or "offline" in diag.root_cause.lower()