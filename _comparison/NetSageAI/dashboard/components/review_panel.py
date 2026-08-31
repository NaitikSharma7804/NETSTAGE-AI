"""UI Component for mandatory human review workflow."""

import streamlit as st


def render_human_review_panel(diagnosis_id: int, original_ai_cause: str, on_submit_callback):
    """Renders human review form allowing user to Accept, Edit, or Reject AI diagnosis."""
    st.markdown("---")
    st.markdown("## 🛡️ Mandatory Human Oversight Review")
    st.warning("⚠️ **Human Review Required**: NetSage AI recommendations must be verified by a network engineer before being accepted.")

    with st.form(key=f"review_form_{diagnosis_id}"):
        action = st.radio(
            "Select Human Decision:",
            ["Accepted", "Edited", "Rejected"],
            index=0,
            horizontal=True
        )

        final_diagnosis = st.text_area(
            "Final Accepted / Corrected Diagnosis:",
            value=original_ai_cause,
            help="If editing or rejecting, enter the verified corrected network fault diagnosis here."
        )

        reviewer_notes = st.text_area(
            "Reviewer Engineering Notes:",
            placeholder="Explain why the diagnosis was accepted, modified, or rejected...",
            height=80
        )

        col_reason, col_lesson = st.columns(2)
        with col_reason:
            reason = st.text_input("Correction Reason (for Responsible AI Log)", placeholder="e.g. AI overlooked subinterface line protocol state")
        with col_lesson:
            lesson = st.text_input("Lesson Learned / Knowledge Base Entry", placeholder="e.g. Check subinterface line status in show ip interface brief")

        submitted = st.form_submit_button("Submit Final Human Review", type="primary", use_container_width=True)

        if submitted:
            on_submit_callback(
                diagnosis_id=diagnosis_id,
                status=action,
                final_human_diagnosis=final_diagnosis,
                reviewer_notes=reviewer_notes,
                reason=reason,
                lesson=lesson
            )
