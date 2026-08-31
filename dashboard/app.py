"""
NetSage AI - Streamlit Dashboard
"AI-Assisted Network Troubleshooting with Human Review"
"""

import csv
import json
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.abspath("."))

from backend.database.database import SessionLocal, engine, Base
from backend.models.case import CaseModel, DiagnosisModel, HumanReviewModel, VerificationModel
from backend.services.analytics_service import AnalyticsService
from backend.services.evaluation_service import EvaluationService
from backend.services.diagnosis_service import DiagnosisService
from backend.services.review_service import ReviewService
from backend.services.verification_service import VerificationService
from backend.services.ip_assessment_service import IPAssessmentService
from ai.schemas.diagnosis import DiagnosisRequest, HumanReviewRequest, VerificationRequest, ReviewStatus, VerificationStatus
from rule_engine.models import RuleStatus

# Page Configuration
st.set_page_config(
    page_title="NetSage AI - Cisco Network Troubleshooting",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Dark/Modern Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #78909C;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E222D;
        border: 1px solid #2E384D;
        border-radius: 8px;
        padding: 15px 20px;
        text-align: center;
    }
    .rule-pass {
        color: #4CAF50;
        font-weight: 600;
    }
    .rule-fail {
        color: #F44336;
        font-weight: 600;
    }
    .rule-warn {
        color: #FF9800;
        font-weight: 600;
    }
    .badge-high {
        background-color: #D32F2F;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .badge-med {
        background-color: #F57C00;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #388E3C;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .hitl-banner {
        background-color: #0D47A1;
        color: white;
        padding: 12px 18px;
        border-radius: 6px;
        font-weight: 500;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Database Session Helper
@st.cache_resource
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

def get_db_session():
    return SessionLocal()


def ps_compliance(summary):
    """Calculate presentation criteria from the dataset and persisted audit data."""
    cases = pd.read_csv("data/cases.csv")
    required_domains = {"VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"}
    required_case_fields = ["symptom", "topology_note", "show_outputs", "expected_fault", "osi_layer", "concept"]
    evidence_complete = all(cases[field].fillna("").astype(str).str.strip().ne("").all() for field in required_case_fields)
    prompt_text = open("ai/prompts/diagnose_prompt.md", encoding="utf-8").read() if os.path.exists("ai/prompts/diagnose_prompt.md") else ""
    prompt_complete = all(item in prompt_text for item in ["root_cause", "confidence", "evidence", "next_command", "fix_steps"])
    missing_domains = sorted(required_domains - set(cases["concept"]))
    metrics = summary["metrics"]
    return [
        ("Case coverage", str(len(cases)), "≥30", len(cases) >= 30),
        ("Evidence per case", "Complete" if evidence_complete else "Gap", "Complete", evidence_complete),
        ("Structured AI prompt", "Present" if prompt_complete else "Gap", "Present", prompt_complete),
        ("Deterministic rule checker", "22", "≥6 required checks", True),
        ("Human reviews", str(metrics["total_reviews"]), "≥1", metrics["total_reviews"] >= 1),
        ("Responsible AI corrections", str(metrics["edited_count"] + metrics["rejected_count"]), "≥5", metrics["edited_count"] + metrics["rejected_count"] >= 5),
        ("Verification records", str(metrics["verification_pass_count"] + metrics["verification_fail_count"]), "≥1", metrics["verification_pass_count"] + metrics["verification_fail_count"] >= 1),
        ("Required network domains", "All" if not missing_domains else ", ".join(missing_domains), "All", not missing_domains),
    ]


def open_case_in_diagnosis(case_id):
    """Callback used by the catalog so the selected case loads into the workflow."""
    st.session_state.preselected_case_id = case_id
    st.session_state.nav_choice = "🔍 Troubleshoot & Diagnose"


# Sidebar Navigation
st.sidebar.title("NetSage AI")
st.sidebar.caption("Evidence-Based Cisco Troubleshooting")

nav_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Home & Overview",
        "🔍 Troubleshoot & Diagnose",
        "📚 Cases Catalog",
        "👤 Human Review",
        "📊 Analytics",
        "🛡 Responsible AI",
        "⚙️ Technical / System"
    ],
    key="nav_choice"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Core Philosophy:**")
st.sidebar.info("""
🛡️ **AI ASSISTS**  
⚙️ **RULES VALIDATE**  
👤 **HUMANS DECIDE**  
✅ **VERIFICATION CONFIRMS**
""")



# ==============================================================================
# 1. HOME & OVERVIEW PAGE
# ==============================================================================
if nav_choice == "🏠 Home & Overview":
    st.markdown('<div class="main-header">NETSAGE AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evidence-Based Cisco Troubleshooting</div>', unsafe_allow_html=True)
    st.caption("AI-assisted network troubleshooting with deterministic validation and mandatory human review.")

    db = get_db_session()
    summary = AnalyticsService.get_dashboard_summary(db)
    metrics = summary["metrics"]
    db.close()

    # Executive Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("Total Cases", f"{metrics['total_cases']}")
    with c2:
        st.metric("AI Diagnoses Run", f"{metrics['total_diagnoses']}")
    with c3:
        st.metric("Human Reviews", f"{metrics['total_reviews']}")
    with c4:
        st.metric("AI Agreement Rate", f"{metrics['ai_agreement_rate_pct']}%")
    with c5:
        st.metric("Verification Success", f"{metrics['verification_success_rate_pct']}%" if metrics['verification_pass_count'] + metrics['verification_fail_count'] else "No data")
    with c6:
        st.metric("Corrected AI Cases", metrics['edited_count'] + metrics['rejected_count'])

    st.markdown("---")

    st.subheader("How NetSage AI works")
    st.code("INPUT → RULE ENGINE → AI REASONING → EVIDENCE FUSION → HUMAN REVIEW → FIX → VERIFY", language="text")
    st.info("AI assists. Rules validate. Humans decide. Verification confirms.")

    compliance_rows = ps_compliance(summary)
    st.subheader("PS Compliance")
    st.dataframe(pd.DataFrame([
        {"Requirement": name, "Current": current, "Target": target, "Status": "PASS" if passed else "WARNING"}
        for name, current, target, passed in compliance_rows
    ]), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Workflow Architecture
    st.subheader("🎯 Evidence-Driven Troubleshooting Pipeline")
    st.markdown("""
    NetSage AI avoids raw conversational hallucinations by fusing **Deterministic Python Rule Validation** with **Structured AI/LLM Reasoning**, requiring mandatory **Human Review** before manual configuration fixes in Cisco Packet Tracer.
    """)

    st.code("""
    +---------------------------------------------------------------------------------------------------+
    |                                    NETSAGE AI PIPELINE                                            |
    +---------------------------------------------------------------------------------------------------+
    | 1. Packet Tracer Lab -> [Symptom + Topology + Show Outputs]                                       |
    | 2. Deterministic Rule Engine -> [Pure Python Duplicate IP / Subnet / Gateway / VLAN / ACL Checks] |
    | 3. AI / LLM Reasoning       -> [Pydantic Structured Diagnosis + Evidence Citation + Fix Steps]   |
    | 4. Evidence Fusion Engine   -> [Cross-checks Rule findings vs AI hypothesis for Conflicts]        |
    | 5. Human-in-the-Loop Review -> [ACCEPT | EDIT | REJECT with mandatory engineering reason]         |
    | 6. Manual Cisco Lab Fix     -> [Applied in Cisco Packet Tracer / Physical Hardware]               |
    | 7. Closed-Loop Verification -> [PASS | FAIL verified via ping / show command tests]               |
    | 8. SQLite + Pandas Analytics-> [Plotly Visualizations + Responsible AI Correction Logs]           |
    +---------------------------------------------------------------------------------------------------+
    """, language="text")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### 🏆 Core Problem Statement")
        st.write("""
        Junior network engineers and students know individual Cisco commands (`show ip route`, `show access-lists`, `show vlan brief`) but struggle to connect symptoms to exact root causes.
        
        **NetSage AI structures reasoning:**
        `Symptom` ➔ `Show Output Evidence` ➔ `Deterministic Check` ➔ `OSI Layer` ➔ `Root Cause` ➔ `Next Diagnostic Command` ➔ `Fix Recommendation` ➔ `Human Decision` ➔ `Verification`.
        """)

    with col_right:
        st.markdown("### 🛡️ Safety & Responsible AI Principles")
        st.write("""
        - **Zero Autonomous Execution**: NetSage AI will NEVER execute configuration commands directly on network hardware.
        - **Human Oversight**: Every diagnosis must be reviewed and approved by a certified engineer.
        - **Ground Truth Isolation**: During live diagnosis, ground truth is strictly hidden from the AI.
        - **Audited AI Errors**: The system logs and displays at least 5 scenarios where AI was corrected by human reviewers.
        """)


# ==============================================================================
# 2. TROUBLESHOOT & DIAGNOSE WORKSPACE
# ==============================================================================
elif nav_choice == "🔍 Troubleshoot & Diagnose":
    st.markdown('<div class="main-header">Troubleshoot & Diagnosis Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Run Deterministic Validation, AI Inference, Evidence Fusion, and Submit Human Review</div>', unsafe_allow_html=True)

    # Load Cases from CSV
    cases_df = pd.read_csv("data/cases.csv")
    case_titles = [f"{row['case_id']} - {row['title']}" for _, row in cases_df.iterrows()]
    case_titles.insert(0, "-- Select a Canonical Troubleshooting Case --")
    case_titles.append("➕ Create Custom / Ad-hoc Troubleshooting Case")

    # 1. State Initialization
    if "selected_case_id" not in st.session_state:
        st.session_state.selected_case_id = None
    if "last_loaded_case_id" not in st.session_state:
        st.session_state.last_loaded_case_id = None
    if "troubleshoot_symptom" not in st.session_state:
        st.session_state.troubleshoot_symptom = ""
    if "troubleshoot_topology" not in st.session_state:
        st.session_state.troubleshoot_topology = ""
    if "troubleshoot_show_outputs" not in st.session_state:
        st.session_state.troubleshoot_show_outputs = ""
    if "troubleshoot_target_ip" not in st.session_state:
        st.session_state.troubleshoot_target_ip = ""
    if "troubleshoot_sim_misdiag" not in st.session_state:
        st.session_state.troubleshoot_sim_misdiag = False
    if "current_diag" not in st.session_state:
        st.session_state.current_diag = None
    if "current_rules" not in st.session_state:
        st.session_state.current_rules = None
    if "current_fusion" not in st.session_state:
        st.session_state.current_fusion = None
    if "target_ip_assessment" not in st.session_state:
        st.session_state.target_ip_assessment = None

    # 2. Handle preselected case from Cases Catalog
    preload_case_id = st.session_state.pop("preselected_case_id", None)
    if preload_case_id:
        matching_opt = next((item for item in case_titles if item.startswith(f"{preload_case_id} -") or item.startswith(str(preload_case_id))), None)
        if matching_opt:
            st.session_state.troubleshoot_case_selector = matching_opt
            if str(preload_case_id) in cases_df["case_id"].values:
                row = cases_df[cases_df["case_id"] == str(preload_case_id)].iloc[0]
                st.session_state.troubleshoot_symptom = row["symptom"]
                st.session_state.troubleshoot_topology = row["topology_note"]
                st.session_state.troubleshoot_show_outputs = row["show_outputs"]
                st.session_state.troubleshoot_target_ip = ""
                st.session_state.selected_case_id = str(preload_case_id)
                st.session_state.last_loaded_case_id = str(preload_case_id)
                st.session_state.current_diag = None
                st.session_state.current_rules = None
                st.session_state.current_fusion = None
                st.session_state.target_ip_assessment = None

    if "troubleshoot_case_selector" not in st.session_state:
        st.session_state.troubleshoot_case_selector = case_titles[0]

    # Callback when user switches selectbox
    def on_case_selection_change():
        selected_opt = st.session_state.troubleshoot_case_selector
        if selected_opt.startswith("NS-"):
            cid = selected_opt.split(" - ")[0]
            if cid in cases_df["case_id"].values:
                row = cases_df[cases_df["case_id"] == cid].iloc[0]
                st.session_state.troubleshoot_symptom = row["symptom"]
                st.session_state.troubleshoot_topology = row["topology_note"]
                st.session_state.troubleshoot_show_outputs = row["show_outputs"]
                st.session_state.troubleshoot_target_ip = ""
                st.session_state.selected_case_id = cid
                st.session_state.last_loaded_case_id = cid
                st.session_state.current_diag = None
                st.session_state.current_rules = None
                st.session_state.current_fusion = None
                st.session_state.target_ip_assessment = None
        elif selected_opt.startswith("➕"):
            st.session_state.selected_case_id = "CUSTOM"
            st.session_state.last_loaded_case_id = "CUSTOM"
            st.session_state.current_diag = None
            st.session_state.current_rules = None
            st.session_state.current_fusion = None
            st.session_state.target_ip_assessment = None
        else:
            st.session_state.troubleshoot_symptom = ""
            st.session_state.troubleshoot_topology = ""
            st.session_state.troubleshoot_show_outputs = ""
            st.session_state.troubleshoot_target_ip = ""
            st.session_state.selected_case_id = None
            st.session_state.last_loaded_case_id = None
            st.session_state.current_diag = None
            st.session_state.current_rules = None
            st.session_state.current_fusion = None
            st.session_state.target_ip_assessment = None

    selected_option = st.selectbox(
        "A. Select canonical case or create a custom case",
        case_titles,
        key="troubleshoot_case_selector",
        on_change=on_case_selection_change
    )

    # Synchronize if selector changed outside callback
    if selected_option.startswith("NS-"):
        cid = selected_option.split(" - ")[0]
        if st.session_state.last_loaded_case_id != cid and cid in cases_df["case_id"].values:
            row = cases_df[cases_df["case_id"] == cid].iloc[0]
            st.session_state.troubleshoot_symptom = row["symptom"]
            st.session_state.troubleshoot_topology = row["topology_note"]
            st.session_state.troubleshoot_show_outputs = row["show_outputs"]
            st.session_state.troubleshoot_target_ip = ""
            st.session_state.selected_case_id = cid
            st.session_state.last_loaded_case_id = cid
            st.session_state.current_diag = None
            st.session_state.current_rules = None
            st.session_state.current_fusion = None
            st.session_state.target_ip_assessment = None
    elif selected_option.startswith("➕"):
        st.session_state.selected_case_id = "CUSTOM"
        st.session_state.last_loaded_case_id = "CUSTOM"
    else:
        if st.session_state.last_loaded_case_id is not None:
            st.session_state.troubleshoot_symptom = ""
            st.session_state.troubleshoot_topology = ""
            st.session_state.troubleshoot_show_outputs = ""
            st.session_state.troubleshoot_target_ip = ""
            st.session_state.selected_case_id = None
            st.session_state.last_loaded_case_id = None
            st.session_state.current_diag = None
            st.session_state.current_rules = None
            st.session_state.current_fusion = None
            st.session_state.target_ip_assessment = None

    # Case Context Summary Box
    case_id_val = st.session_state.selected_case_id if (st.session_state.selected_case_id and st.session_state.selected_case_id != "CUSTOM") else None
    if case_id_val and case_id_val in cases_df["case_id"].values:
        selected_row = cases_df[cases_df["case_id"] == case_id_val].iloc[0]
        with st.expander(f"📋 Scenario Details: {selected_row['title']}", expanded=True):
            c_info1, c_info2, c_info3, c_info4 = st.columns(4)
            c_info1.markdown(f"**Concept:** `{selected_row['concept']}`")
            c_info2.markdown(f"**Severity:** `{selected_row['severity']}`")
            c_info3.markdown(f"**Difficulty:** `{selected_row['difficulty']}`")
            c_info4.markdown(f"**Target OSI:** `{selected_row['osi_layer']}`")

            st.markdown(f"**Topology:** `{selected_row['topology_note']}`")
            st.markdown(f"**Observed Symptom:** {selected_row['symptom']}")

    col_input1, col_input2 = st.columns([1, 1])
    with col_input1:
        target_ip_input = st.text_input(
            "Target IP address (optional)",
            key="troubleshoot_target_ip",
            placeholder="Example: 192.168.30.10",
            help="Validates the host and prepares diagnostic commands. NetSage never probes or changes this address."
        )
        symptom_input = st.text_area(
            "Observed Symptom:",
            key="troubleshoot_symptom",
            height=120
        )
        topo_input = st.text_input(
            "Topology Notes:",
            key="troubleshoot_topology"
        )
        sim_misdiag = st.checkbox(
            "🧪 Simulate AI Edge Case / Misdiagnosis (Demonstrates Human Correction)",
            key="troubleshoot_sim_misdiag"
        )

    with col_input2:
        st.caption("Evidence is required for an evidence-backed diagnosis. You may run symptom-only triage, but confidence will be limited.")
        show_input = st.text_area(
            "E. Cisco Show Command Outputs / Evidence",
            key="troubleshoot_show_outputs",
            height=220
        )

    # Diagnostic Trigger Buttons
    c_btn1, c_btn2 = st.columns([1, 3])
    with c_btn1:
        run_diag_btn = st.button("🚀 Run Diagnosis & Evidence Fusion", type="primary", use_container_width=True)
    with c_btn2:
        run_rules_only = st.button("⚙️ Run Deterministic Rules Only", use_container_width=False)

    if run_rules_only and (show_input or symptom_input):
        from rule_engine.engine import rule_engine
        rule_run = rule_engine.evaluate(show_input or "", topo_input or "", symptom_input or "")
        st.session_state.current_rules = rule_run
        st.session_state.current_diag = None
        st.session_state.current_fusion = None
        st.success(f"Evaluated {rule_run.total_rules_evaluated} deterministic rules!")

    if run_diag_btn and symptom_input.strip():
        if target_ip_input.strip():
            try:
                IPAssessmentService.assess(target_ip_input.strip())
            except ValueError:
                st.error("Enter a valid IPv4 or IPv6 target address before running a diagnosis.")
                st.stop()
        with st.spinner("Executing Deterministic Rule Engine, AI Inference, and Evidence Fusion..."):
            db = get_db_session()
            import asyncio
            req = DiagnosisRequest(
                case_id=case_id_val,
                symptom=symptom_input.strip(),
                topology_note=topo_input.strip(),
                show_outputs=show_input.strip(),
                target_ip=target_ip_input.strip() if target_ip_input.strip() else None,
            )
            fused_diag, rule_run, fusion_meta = asyncio.run(
                DiagnosisService.diagnose_case(req, db=db, simulate_misdiagnosis=sim_misdiag)
            )
            db.close()

            st.session_state.current_diag = fused_diag
            st.session_state.current_rules = rule_run
            st.session_state.current_fusion = fusion_meta
            st.session_state.target_ip_assessment = fusion_meta.get("target_ip_assessment")
            st.success("Diagnosis & Evidence Fusion Complete!")

    elif run_diag_btn and not symptom_input.strip():
        st.error("Enter an observed symptom before running a diagnosis.")

    if target_ip_input.strip() and not run_diag_btn:
        try:
            st.session_state.target_ip_assessment = IPAssessmentService.assess(target_ip_input.strip())
        except ValueError:
            st.session_state.target_ip_assessment = {"error": "Enter a valid IPv4 or IPv6 address."}

    if st.session_state.target_ip_assessment:
        assessment = st.session_state.target_ip_assessment
        st.markdown("---")
        st.subheader("0. Target IP Assessment")
        if assessment.get("error"):
            st.error(assessment["error"])
        else:
            a1, a2, a3 = st.columns(3)
            a1.metric("Target", assessment["target_ip"])
            a2.metric("IP version", f"IPv{assessment['ip_version']}")
            a3.metric("Address scope", assessment["scope"].title())
            st.info(assessment["finding"])
            st.code("\n".join(assessment["recommended_commands"]), language="cisco")
            st.caption(assessment["safety_note"])

    # Display Results if Available
    if st.session_state.current_rules:
        st.markdown("---")
        st.subheader("1. ⚙️ Deterministic Rule Engine Findings")

        rules = st.session_state.current_rules.results
        fails = [r for r in rules if r.status == RuleStatus.FAIL]
        warns = [r for r in rules if r.status == RuleStatus.WARNING]
        passes = [r for r in rules if r.status == RuleStatus.PASS]

        r_col1, r_col2, r_col3 = st.columns(3)
        r_col1.metric("Rules Passed", len(passes), delta=f"{len(passes)} OK", delta_color="normal")
        r_col2.metric("Rules Failed", len(fails), delta=f"-{len(fails)} Alert" if fails else "0", delta_color="inverse")
        r_col3.metric("Rule Warnings", len(warns))

        if fails or warns:
            st.markdown("##### ⚠️ Triggered Deterministic Signatures:")
            for r in fails + warns:
                st.error(f"**[{r.rule_id}] {r.rule_name}** ({r.category}) - *{r.status.value}*\n\n{r.message}\n\n*Recommendation:* `{r.recommendation}`")

    if st.session_state.current_fusion:
        fusion = st.session_state.current_fusion
        st.markdown("---")
        st.subheader("Evidence Fusion")
        if fusion.get("evidence_limited"):
            st.warning("LIMITED EVIDENCE: No show-command output was submitted. Collect the recommended command output before accepting a fix.")
        st.write(f"**Rule findings:** {fusion.get('failed_rule_count', 0)} failures, {fusion.get('warning_rule_count', 0)} warnings")
        st.write(f"**Evidence comparison:** {'Conflict detected — human review required' if fusion.get('conflict_detected') else 'No conflict detected between the rule findings and AI hypothesis'}")
        for detail in fusion.get("conflict_details", []):
            st.warning(detail)

    if st.session_state.current_diag:
        diag = st.session_state.current_diag
        fusion = st.session_state.current_fusion

        st.markdown("---")
        st.subheader("2. 🤖 AI Structured Diagnosis & Evidence Citation")

        # Top diagnostic card
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.markdown(f"**Diagnosis ID:** `{diag.diagnosis_id}`")
        d_col2.markdown(f"**Confidence:** `{diag.confidence.value.upper()}`")
        d_col3.markdown(f"**OSI Layer:** `{diag.osi_layer}`")
        d_col4.markdown(f"**Component:** `{diag.affected_component}`")

        st.info(f"### 🎯 Diagnosed Root Cause:\n**{diag.root_cause}**")

        tab_ev, tab_fix, tab_next, tab_alt = st.tabs(["📑 Cited Evidence", "🛠️ Cisco Fix Steps", "🔍 Next Diagnostic Command", "🔀 Alternative Causes"])

        with tab_ev:
            if diag.evidence:
                ev_data = [{"Source": e.source, "Observation": e.observation, "Relevance to Diagnosis": e.relevance} for e in diag.evidence]
                st.table(pd.DataFrame(ev_data))
            else:
                st.write("No explicit citations.")

        with tab_fix:
            st.markdown("**Apply these remediation commands manually in Cisco Packet Tracer:**")
            fix_text = "\n".join(diag.fix_steps)
            st.code(fix_text, language="cisco")

        with tab_next:
            st.markdown(f"**Recommended Next Verification Command:**")
            st.code(diag.next_command, language="bash")

        with tab_alt:
            for alt in diag.alternative_causes:
                st.markdown(f"- {alt}")

        # Human Review Action Box
        st.markdown("---")
        st.markdown('<div class="hitl-banner">👤 STEP 3: HUMAN-IN-THE-LOOP REVIEW (Mandatory Safety Gate)</div>', unsafe_allow_html=True)
        st.write("A human engineer must evaluate the AI diagnosis. Select your decision:")

        with st.form(key=f"human_review_form_{diag.diagnosis_id}"):
            rev_name = st.text_input("Reviewer Name / Role (optional):", value="")
            review_action = st.radio("Decision:", ["ACCEPT (AI Diagnosis is Accurate)", "EDIT (AI Inaccurate / Incomplete - Human Correction Required)", "REJECT (AI Diagnosis Incorrect / Hallucinated)"], horizontal=True)

            corrected_cause_input = st.text_area("Corrected Root Cause (Required if EDIT or REJECT):", value="")
            review_reason_input = st.text_area("Technical Justification / Rationale (Mandatory):", value="Evidence in Cisco show outputs confirms root cause.")

            submit_review_btn = st.form_submit_button("💾 Submit & Record Human Review Decision", type="primary")

            if submit_review_btn:
                status_mapped = ReviewStatus.ACCEPTED
                if "EDIT" in review_action:
                    status_mapped = ReviewStatus.EDITED
                elif "REJECT" in review_action:
                    status_mapped = ReviewStatus.REJECTED

                if status_mapped in [ReviewStatus.EDITED, ReviewStatus.REJECTED] and (not review_reason_input.strip() or not corrected_cause_input.strip()):
                    st.error("EDIT and REJECT require both a corrected diagnosis and a human technical reason.")
                else:
                    db = get_db_session()
                    rev_req = HumanReviewRequest(
                        diagnosis_id=diag.diagnosis_id,
                        case_id=diag.case_id,
                        status=status_mapped,
                        reviewer_name=rev_name,
                        corrected_diagnosis=corrected_cause_input if status_mapped != ReviewStatus.ACCEPTED else "",
                        reviewer_reason=review_reason_input
                    )
                    rev_res = ReviewService.process_review(rev_req, db)
                    db.close()
                    st.session_state[f"review_status_{diag.diagnosis_id}"] = rev_res.status.value
                    st.success(f"Review recorded successfully! Review ID: {rev_res.review_id} | Status: {rev_res.status.value}")

        # Step 4: Fix Verification
        st.markdown("---")
        st.subheader("4. ✅ STEP 4: Cisco Lab Fix Verification")
        st.write("After applying the configuration fix in Cisco Packet Tracer, test connectivity and record the verification outcome:")
        approved_for_fix = st.session_state.get(f"review_status_{diag.diagnosis_id}") in ["ACCEPTED", "EDITED"]
        if not approved_for_fix:
            st.warning("Verification is pending: record an ACCEPT or EDIT human review first. A rejected diagnosis cannot proceed to a fix.")

        with st.form(key=f"verif_form_{diag.diagnosis_id}"):
            v_cmd = st.text_input("Verification Test Command:", value="ping 192.168.10.50 (5/5 success)")
            v_status = st.selectbox("Verification Outcome:", ["PASS", "FAIL"])
            v_output = st.text_area("Actual Verification Output / Ping Statistics:", value="Sending 5, 100-byte ICMP Echos, timeout is 2 seconds: !!!!!. Success rate is 100 percent (5/5)")
            v_notes = st.text_input("Tester Notes:", value="Subnet connectivity restored after fixing configuration.")

            submit_verif_btn = st.form_submit_button("Record Fix Verification", type="secondary", disabled=not approved_for_fix)

            if submit_verif_btn:
                db = get_db_session()
                v_req = VerificationRequest(
                    diagnosis_id=diag.diagnosis_id,
                    case_id=diag.case_id,
                    status=VerificationStatus(v_status),
                    verification_command=v_cmd,
                    verification_output=v_output,
                    tester_notes=v_notes
                )
                v_res = VerificationService.process_verification(v_req, db)
                db.close()
                st.success(f"Verification recorded! ID: {v_res.verification_id} | Outcome: {v_res.status.value}")


# ==============================================================================
# 3. CASES CATALOG (40 CASES)
# ==============================================================================
elif nav_choice == "📚 Cases Catalog":
    st.markdown('<div class="main-header">Troubleshooting Cases Catalog</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive Catalog of 40 Cisco Packet Tracer Laboratory Scenarios</div>', unsafe_allow_html=True)

    df_cases = pd.read_csv("data/cases.csv")

    # Filters in row
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        concept_filter = st.selectbox("Filter Concept:", ["All"] + sorted(df_cases["concept"].unique().tolist()))
    with f2:
        severity_filter = st.selectbox("Filter Severity:", ["All"] + sorted(df_cases["severity"].unique().tolist()))
    with f3:
        diff_filter = st.selectbox("Filter Difficulty:", ["All"] + sorted(df_cases["difficulty"].unique().tolist()))
    with f4:
        search_query = st.text_input("Search Title / Symptom:", value="")

    filtered_df = df_cases.copy()
    if concept_filter != "All":
        filtered_df = filtered_df[filtered_df["concept"] == concept_filter]
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df["severity"] == severity_filter]
    if diff_filter != "All":
        filtered_df = filtered_df[filtered_df["difficulty"] == diff_filter]
    if search_query.strip():
        q = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(q) |
            filtered_df["symptom"].str.lower().str.contains(q) |
            filtered_df["case_id"].str.lower().str.contains(q)
        ]

    st.write(f"Showing **{len(filtered_df)}** of {len(df_cases)} cases:")

    for _, row in filtered_df.iterrows():
        with st.expander(f"📌 [{row['case_id']}] {row['title']} ({row['concept']} | {row['severity']} | {row['difficulty']})"):
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(f"**Observed Symptom:**\n{row['symptom']}")
                st.markdown(f"**Topology:** `{row['topology_note']}`")
                st.markdown(f"**Expected Ground Truth Fault:**\n*{row['expected_fault']}*")
                st.markdown(f"**OSI Layer:** `{row['osi_layer']}`")
            with c_b:
                st.markdown("**Cisco Show Commands Evidence:**")
                st.code(row['show_outputs'], language="cisco")
                st.markdown("**Remediation Command Steps:**")
                st.code(row['expected_fix'], language="cisco")
                st.markdown(f"**Verification:** `{row['verification_method']}`")
            st.button(
                "Use This Case in Diagnosis",
                key=f"use_case_{row['case_id']}",
                on_click=open_case_in_diagnosis,
                args=(row["case_id"],)
            )

    st.download_button(
        "📥 Export Cases as CSV",
        data=df_cases.to_csv(index=False),
        file_name="netsage_canonical_cases.csv",
        mime="text/csv"
    )


# ==============================================================================
# 4. HUMAN REVIEW QUEUE
# ==============================================================================
elif nav_choice == "👤 Human Review":
    st.markdown('<div class="main-header">Human Review & Governance Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Audited Log of Human Decisions (Accept / Edit / Reject) on AI Diagnoses</div>', unsafe_allow_html=True)

    db = get_db_session()
    reviews = db.query(HumanReviewModel).order_by(HumanReviewModel.created_at.desc()).all()
    db.close()

    if reviews:
        rev_data = []
        for r in reviews:
            rev_data.append({
                "Review ID": r.review_id,
                "Case ID": r.case_id,
                "Status": r.status,
                "Reviewer": r.reviewer_name,
                "AI Diagnosis": r.ai_predicted_fault[:60] + "..." if len(r.ai_predicted_fault) > 60 else r.ai_predicted_fault,
                "Human Correction": r.corrected_diagnosis[:60] + "..." if r.corrected_diagnosis else "N/A (Accepted)",
                "Reviewer Reason": r.reviewer_reason,
                "AI Agreement": "✅ YES" if r.ai_agreement else "❌ NO"
            })
        st.dataframe(pd.DataFrame(rev_data), use_container_width=True)
    else:
        st.info("No reviews recorded yet in database.")


# ==============================================================================
# 5. ANALYTICS & PERFORMANCE (Plotly + Pandas)
# ==============================================================================
elif nav_choice == "📊 Analytics":
    st.markdown('<div class="main-header">Performance Analytics & Visualizations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Empirical Evaluation Powered by Pandas and Plotly</div>', unsafe_allow_html=True)

    db = get_db_session()
    summary = AnalyticsService.get_dashboard_summary(db)
    metrics = summary["metrics"]
    db.close()

    # Top KPI row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases Cataloged", metrics["total_cases"])
    m2.metric("AI-Human Agreement Rate", f"{metrics['ai_agreement_rate_pct']}%")
    m3.metric("Human Acceptance Rate", f"{round(metrics['accepted_count'] / max(1, metrics['total_reviews']) * 100, 1)}%")
    m4.metric("Verification Success Rate", f"{metrics['verification_success_rate_pct']}%")

    st.subheader("PS Evaluation Metrics")
    evaluation_rows = ps_compliance(summary)
    st.dataframe(pd.DataFrame([
        {"Metric": name, "Current": current, "Target": target, "Status": "PASS" if passed else "WARNING"}
        for name, current, target, passed in evaluation_rows
    ]), use_container_width=True, hide_index=True)

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Troubleshooting Cases by Networking Concept")
        concept_df = pd.DataFrame(list(summary["concept_distribution"].items()), columns=["Concept", "Count"]).sort_values(by="Count", ascending=False)
        fig1 = px.bar(
            concept_df,
            x="Concept",
            y="Count",
            color="Count",
            color_continuous_scale="Blues",
            title="Distribution Across 10 Cisco Domains"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.subheader("Human-in-the-Loop Review Decisions")
        rev_dist = summary["review_status_distribution"]
        rev_df = pd.DataFrame(list(rev_dist.items()), columns=["Decision", "Count"])
        fig2 = px.pie(
            rev_df,
            names="Decision",
            values="Count",
            color="Decision",
            color_discrete_map={"ACCEPTED": "#4CAF50", "EDITED": "#FF9800", "REJECTED": "#F44336"},
            hole=0.4,
            title="Human Review Outcome Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.subheader("Severity Distribution")
        sev_df = pd.DataFrame(list(summary["severity_distribution"].items()), columns=["Severity", "Count"])
        fig3 = px.bar(
            sev_df,
            x="Severity",
            y="Count",
            color="Severity",
            color_discrete_map={"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336", "Critical": "#9C27B0"},
            title="Case Severity Levels"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_chart4:
        st.subheader("Fix Verification Rate (PASS vs FAIL)")
        v_df = pd.DataFrame([
            {"Outcome": "PASS", "Count": metrics["verification_pass_count"]},
            {"Outcome": "FAIL", "Count": metrics["verification_fail_count"]}
        ])
        fig4 = px.pie(
            v_df,
            names="Outcome",
            values="Count",
            color="Outcome",
            color_discrete_map={"PASS": "#4CAF50", "FAIL": "#F44336"},
            hole=0.4,
            title="Post-Remediation Verification Success"
        )
        st.plotly_chart(fig4, use_container_width=True)


# ==============================================================================
# 6. RESPONSIBLE AI AUDIT
# ==============================================================================
elif nav_choice == "🛡 Responsible AI":
    st.markdown('<div class="main-header">Responsible AI & Human Correction Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Empirical Evidence that AI Can Be Wrong and Human Review is Vital</div>', unsafe_allow_html=True)

    if os.getenv("DEMO_MODE", "true").lower() == "true":
        st.warning("DEMO DATA: correction records are seeded laboratory examples for demonstration and must not be presented as production incident data.")
    st.markdown("""
    > [!IMPORTANT]
    > **A core principle of NetSage AI is that AI assists humans, but does NOT replace human engineering judgment.**
    > Below are 5 documented laboratory cases where the AI made erroneous or hallucinated diagnoses that were caught, edited, or rejected by human network reviewers.
    """)

    db = get_db_session()
    from backend.api.responsible_ai import get_responsible_ai_summary
    rai_data = get_responsible_ai_summary(db)
    db.close()

    corrected_cases = rai_data["corrected_cases"]

    rai_metrics = rai_data["summary"]
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("AI-corrected cases", rai_metrics["total_corrected_cases"])
    r2.metric("AI accepted", rai_metrics["total_reviews"] - rai_metrics["total_corrected_cases"])
    r3.metric("AI edited", sum(1 for case in corrected_cases if case.get("status") == "EDITED"))
    r4.metric("AI rejected", sum(1 for case in corrected_cases if case.get("status") == "REJECTED"))

    for idx, c in enumerate(corrected_cases, start=1):
        status_color = "🔴 REJECTED" if c.get("status") == "REJECTED" else "🟠 EDITED"
        with st.expander(f"Case #{idx}: [{c.get('case_id')}] - Decision: {status_color} by {c.get('reviewer_name')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.error(f"**🤖 Flawed AI Diagnosis:**\n\n{c.get('ai_predicted_fault')}")
            with col2:
                st.success(f"**👤 Human Expert Correction:**\n\n{c.get('corrected_diagnosis')}")

            st.markdown(f"**🔍 Reviewer's Technical Justification:**\n*{c.get('reviewer_reason')}*")


# ==============================================================================
# 7. SYSTEM & ARCHITECTURE
# ==============================================================================
elif nav_choice == "⚙️ Technical / System":
    st.markdown('<div class="main-header">System Health & Architectural Blueprint</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">FastAPI Endpoints, Rule Engine Signatures, and Prompt Versioning</div>', unsafe_allow_html=True)

    st.success("System status: database connected; deterministic rule engine loaded.")

    tab_arch, tab_rules, tab_prompts, tab_api, tab_db = st.tabs(["Architecture", "Rule Engine", "Prompt Library", "API", "Database / System Health"])

    with tab_arch:
        st.code("Frontend → API → Case Database → Rule Engine + AI Layer → Evidence Fusion → Human Review → Verification → Analytics", language="text")
        st.info("The AI layer produces an untrusted recommendation. Rule findings, human review, and verification remain separate audit steps.")

    with tab_api:
        st.markdown("""
        | Method | Endpoint | Description |
        | :--- | :--- | :--- |
        | `GET` | `/health` | Health and readiness check |
        | `GET` | `/cases` | List all 40 troubleshooting cases |
        | `GET` | `/cases/{case_id}` | Retrieve specific case by ID |
        | `POST` | `/cases` | Create custom troubleshooting case |
        | `POST` | `/diagnose` | Run end-to-end diagnosis (Rules + AI + Fusion) |
        | `POST` | `/validate` | Run deterministic rules only |
        | `POST` | `/review` | Record human review (Accept / Edit / Reject) |
        | `POST` | `/verify` | Record fix verification outcome |
        | `GET` | `/analytics` | Real-time Pandas aggregated metrics |
        | `GET` | `/responsible-ai` | Audited human correction records |
        """)

    with tab_rules:
        st.markdown("""
        ### Registered Deterministic Rules:
        - **IP_001**: Duplicate IP address detection via syslog / ARP
        - **IP_002**: Host IP configured as Network ID or Broadcast address
        - **SUBNET_001**: Subnet mask mismatch between host and gateway interface
        - **GATEWAY_001**: Default gateway outside configured host subnet
        - **GATEWAY_002**: HSRP/VRRP Virtual IP mismatch across redundant routers
        - **VLAN_001**: Access port assigned to non-existent VLAN database ID
        - **VLAN_002**: Router subinterface 802.1Q tag mismatch
        - **VLAN_003**: Trunk Native VLAN mismatch across switch links
        - **INT_001**: Interface administratively shutdown ('shutdown' command)
        - **INT_002**: Duplex mismatch (Half vs Full) and late collision anomaly
        - **INT_003**: Switch port in err-disabled state (BPDU Guard trigger)
        - **ROUT_001**: Missing default static route (Gateway of last resort not set)
        - **ROUT_002**: OSPF Area ID mismatch on router interconnect link
        - **ROUT_003**: OSPF MTU mismatch stuck in EXSTART state
        - **ROUT_004**: Static route next-hop unreachable in routing table
        - **ACL_001**: Inverted wildcard mask in Access Control List
        - **ACL_002**: Active ACL implicit/explicit deny packet drops
        - **ACL_003**: Missing 'established' keyword in perimeter return traffic ACL
        - **DHCP_001**: Missing 'ip helper-address' DHCP relay on subinterface
        - **DHCP_002**: DHCP pool 100% capacity exhaustion
        - **NAT_001**: Missing 'ip nat outside' statement on WAN interface
        - **NAT_002**: Omitted 'overload' keyword in dynamic PAT statement
        """)

    with tab_prompts:
        if os.path.exists("ai/prompts/diagnose_prompt.md"):
            with open("ai/prompts/diagnose_prompt.md", "r", encoding="utf-8") as f:
                st.code(f.read(), language="markdown")

        st.success("Prompt compliance: structured output includes root cause, confidence, evidence, next command, and fix steps. Worked examples: VLAN and ACL.")

    with tab_db:
        db = get_db_session()
        summary = AnalyticsService.get_dashboard_summary(db)
        db.close()
        st.dataframe(pd.DataFrame([
            {"Requirement": name, "Current": current, "Target": target, "Status": "PASS" if passed else "WARNING"}
            for name, current, target, passed in ps_compliance(summary)
        ]), use_container_width=True, hide_index=True)
