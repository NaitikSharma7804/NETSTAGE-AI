"""UI Component for displaying Rule findings and AI diagnosis cards."""

import streamlit as st


def render_rule_findings(rule_results: list):
    """Renders deterministic rule engine findings with status badges."""
    st.markdown("### 🔍 Deterministic Rule Engine Findings")
    if not rule_results:
        st.info("No rule results recorded.")
        return

    for item in rule_results:
        status = item.get("status", "PASS")
        severity = item.get("severity", "INFO")
        rule_name = item.get("rule", "rule_check")
        message = item.get("message", "")

        if status == "FAIL":
            badge_color = "#e74c3c" if severity == "HIGH" else "#f39c12"
            icon = "❌"
        else:
            badge_color = "#2ecc71"
            icon = "✅"

        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {badge_color};">
                <span style="font-weight: bold; color: #f8fafc;">{icon} [{status}] {rule_name}</span>
                <span style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-left: 10px;">{severity}</span>
                <div style="color: #cbd5e1; margin-top: 6px; font-size: 0.95em;">{message}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_system_status_cards(diag_data: dict):
    """Renders 4 status cards: Dataset Status, AI Mode, Human Review Status, Evidence Grounding Status."""
    ds_status = diag_data.get("dataset_status", "SAMPLE")
    ai_mode = diag_data.get("ai_mode", "mock").upper()
    rev_status = diag_data.get("review_status", "Pending Review").upper()
    grounding_status = diag_data.get("evidence_grounding_status", "Unverified").upper()

    ai_badge_color = "#38bdf8" if ai_mode == "LIVE" or "OPENAI" in ai_mode else "#f59e0b"
    ai_label = "LIVE OPENAI" if ai_mode == "LIVE" or "OPENAI" in ai_mode else "OFFLINE MOCK"

    rev_color = "#f59e0b" if "PENDING" in rev_status else "#10b981" if "ACCEPT" in rev_status else "#ef4444"
    ground_color = "#10b981" if "VERIFIED" == grounding_status else "#f59e0b" if "PARTIALLY" in grounding_status else "#ef4444"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid #6366f1;">
                <div style="font-size: 0.75em; color: #94a3b8; font-weight: bold;">DATASET STATUS</div>
                <div style="font-size: 1.1em; color: #f8fafc; font-weight: bold; margin-top: 4px;">{ds_status}</div>
                <div style="font-size: 0.7em; color: #cbd5e1;">{'Pending Verification' if ds_status == 'SAMPLE' else 'Team Verified'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid {ai_badge_color};">
                <div style="font-size: 0.75em; color: #94a3b8; font-weight: bold;">AI MODE</div>
                <div style="font-size: 1.1em; color: #f8fafc; font-weight: bold; margin-top: 4px;">{ai_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid {rev_color};">
                <div style="font-size: 0.75em; color: #94a3b8; font-weight: bold;">HUMAN REVIEW</div>
                <div style="font-size: 1.1em; color: #f8fafc; font-weight: bold; margin-top: 4px;">{rev_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid {ground_color};">
                <div style="font-size: 0.75em; color: #94a3b8; font-weight: bold;">EVIDENCE GROUNDING</div>
                <div style="font-size: 1.1em; color: #f8fafc; font-weight: bold; margin-top: 4px;">{grounding_status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_ai_diagnosis_card(ai_diag: dict, full_diag: dict = None):
    """Renders structured AI diagnosis card with confidence, OSI layer, next command, and fix steps."""
    if full_diag:
        render_system_status_cards(full_diag)

    st.markdown("### 🤖 AI Troubleshooting Diagnosis")

    root_cause = ai_diag.get("root_cause", "N/A")
    confidence = ai_diag.get("confidence", 0.0)
    osi_layer = ai_diag.get("osi_layer", "N/A")
    next_cmd = ai_diag.get("next_command", "N/A")
    fix_steps = ai_diag.get("fix_steps", [])

    conf_pct = int(confidence * 100)

    # Show warning if dataset is SAMPLE or evidence is unverified/partially verified
    if full_diag:
        g_stat = full_diag.get("evidence_grounding_status", "Verified")
        if g_stat in ["Partially Verified", "Unverified"]:
            st.warning(f"⚠️ **Evidence Grounding Warning**: Some AI evidence is **{g_stat}** against the supplied CLI case output.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence Score", f"{conf_pct}%", delta=f"{osi_layer}")
    with col2:
        st.metric("OSI Layer", osi_layer)
    with col3:
        st.metric("Advisory Mode", "Human Review Mandatory")

    st.markdown(
        f"""
        <div style="background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-top: 10px;">
            <h4 style="color: #38bdf8; margin-top: 0;">Identified Root Cause</h4>
            <p style="color: #f8fafc; font-size: 1.1em; font-weight: 500;">{root_cause}</p>
            
            <h4 style="color: #38bdf8; margin-top: 16px;">Recommended Next Command</h4>
            <code style="background-color: #1e293b; color: #4ade80; padding: 6px 12px; border-radius: 6px; font-size: 1em; display: inline-block;">{next_cmd}</code>
            
            <h4 style="color: #38bdf8; margin-top: 16px;">Recommended Fix Steps</h4>
            <ol style="color: #e2e8f0; margin-left: 20px; line-height: 1.6;">
                {''.join(f'<li><code>{step}</code></li>' for step in fix_steps)}
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
