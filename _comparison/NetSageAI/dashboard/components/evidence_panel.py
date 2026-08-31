"""UI Component for displaying evidence panel."""

import streamlit as st


def render_evidence_panel(evidence_list: list):
    """Renders evidence list extracted from show outputs and rules."""
    st.markdown("### 📜 Evidence Used in Diagnosis")
    if not evidence_list:
        st.info("No specific evidence items listed.")
        return

    st.markdown(
        """
        <div style="background-color: #1e293b; padding: 16px; border-radius: 8px; border-left: 4px solid #38bdf8;">
            <ul style="color: #f1f5f9; margin-left: 20px; line-height: 1.6;">
        """
        + "".join(f"<li>{item}</li>" for item in evidence_list)
        + """
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
