"""Streamlit New Diagnosis Page with Rule Engine, AI Analysis, and Mandatory Human Review."""

import streamlit as st
import requests
from dashboard.components.diagnosis_card import render_rule_findings, render_ai_diagnosis_card
from dashboard.components.evidence_panel import render_evidence_panel
from dashboard.components.review_panel import render_human_review_panel

API_BASE = "http://127.0.0.1:8000/api"


def show_diagnosis_page():
    st.title("🔬 Run Troubleshooting Diagnosis")
    st.markdown("Analyze Packet Tracer lab problems using deterministic rule engine and AI diagnosis.")

    # 1. Option to preload from cases dataset
    st.markdown("#### Select Input Source")
    input_source = st.radio("Choose Input Mode:", ["Preload Sample Case", "Custom CLI Input"], horizontal=True)

    symptom_val = ""
    topology_val = ""
    show_output_val = ""
    selected_case_id = None
    concept_val = "General Networking"

    if input_source == "Preload Sample Case":
        try:
            res = requests.get(f"{API_BASE}/cases", timeout=3)
            if res.status_code == 200:
                cases = res.json()
                case_options = {f"{c['case_id']} - [{c['concept']}] {c['symptom'][:60]}...": c for c in cases}
                selected_label = st.selectbox("Select Case from Database:", list(case_options.keys()))
                if selected_label:
                    c_data = case_options[selected_label]
                    selected_case_id = c_data["case_id"]
                    symptom_val = c_data["symptom"]
                    topology_val = c_data["topology_note"]
                    show_output_val = c_data["show_output"]
                    concept_val = c_data["concept"]
        except Exception:
            st.error("Failed to connect to backend API at http://127.0.0.1:8000. Ensure backend is running.")

    # Form inputs
    with st.form("diagnosis_input_form"):
        symptom_in = st.text_input("1. Network Troubleshooting Symptom:", value=symptom_val, placeholder="e.g. Host cannot ping default gateway 192.168.1.1")
        topology_in = st.text_area("2. Packet Tracer Topology Notes:", value=topology_val, placeholder="e.g. Host on SW1 Fa0/1 VLAN 10 connected to R1 Gi0/0 subinterface.", height=80)
        show_output_in = st.text_area("3. Cisco IOS 'show' Command Output:", value=show_output_val, placeholder="Paste show ip interface brief, show ip route, show run...", height=180)
        
        run_btn = st.form_submit_button("🚀 Run Diagnosis", type="primary", use_container_width=True)

    if run_btn:
        if not symptom_in or not show_output_in:
            st.error("Please provide both a symptom and Cisco show command output.")
            return

        with st.spinner("Executing deterministic rules and AI diagnosis engine..."):
            payload = {
                "case_id": selected_case_id,
                "symptom": symptom_in,
                "topology_note": topology_in,
                "show_output": show_output_in,
                "concept": concept_val
            }
            try:
                resp = requests.post(f"{API_BASE}/diagnose", json=payload, timeout=15)
                if resp.status_code == 200:
                    diag_data = resp.json()
                    st.session_state["current_diagnosis"] = diag_data
                    st.success("Diagnosis completed successfully! Proceed to review findings below.")
                else:
                    st.error(f"Backend API error ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Error calling diagnosis endpoint: {e}")

    # Display Current Diagnosis & Review Workflow if present in session_state
    if "current_diagnosis" in st.session_state:
        diag = st.session_state["current_diagnosis"]
        ds_status = diag.get("dataset_status", "SAMPLE")
        if ds_status == "SAMPLE":
            st.info("ℹ️ **DEVELOPMENT SAMPLE DATASET — PENDING NETWORKING TEAM VERIFICATION**")
        else:
            st.success("✅ **VERIFIED PACKET TRACER CASE**")

        st.markdown("---")
        st.markdown(f"### 📋 Case Diagnostic Report (ID: #{diag['id']})")
        
        col_rule, col_ai = st.columns([1, 1])
        with col_rule:
            render_rule_findings(diag.get("rule_results", []))
        with col_ai:
            render_ai_diagnosis_card(diag.get("ai_diagnosis", {}), full_diag=diag)

        render_evidence_panel(diag.get("ai_diagnosis", {}).get("evidence", []))

        # Callback function for human review
        def handle_review_submission(diagnosis_id, status, final_human_diagnosis, reviewer_notes, reason, lesson):
            review_payload = {
                "diagnosis_id": diagnosis_id,
                "case_id": diag.get("case_id"),
                "status": status,
                "final_human_diagnosis": final_human_diagnosis,
                "reviewer_notes": reviewer_notes,
                "reason": reason,
                "lesson": lesson
            }
            try:
                r_resp = requests.post(f"{API_BASE}/reviews", json=review_payload, timeout=5)
                if r_resp.status_code in [200, 201]:
                    diag["review_status"] = status
                    st.session_state["current_diagnosis"] = diag
                    st.success(f"✅ Human Review submitted successfully! Status updated to **{status}**")
                    if status in ["Edited", "Rejected"]:
                        st.info("📝 Correction recorded in Responsible AI Log as REAL_TEAM_REVIEW!")
                else:
                    st.error(f"Review submission failed: {r_resp.text}")
            except Exception as ex:
                st.error(f"Review API error: {ex}")

        render_human_review_panel(
            diagnosis_id=diag["id"],
            original_ai_cause=diag["ai_diagnosis"].get("root_cause", ""),
            on_submit_callback=handle_review_submission
        )
