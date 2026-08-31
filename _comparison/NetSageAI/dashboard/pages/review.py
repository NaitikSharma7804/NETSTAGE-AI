"""Streamlit Human Review History Page."""

import streamlit as st
import pandas as pd
import requests

API_BASE = "http://127.0.0.1:8000/api"


def show_review_page():
    st.title("🛡️ Human Review & Audit History")
    st.markdown("Track mandatory human oversight decisions (Accepted, Edited, Rejected) across diagnostic runs.")

    try:
        res = requests.get(f"{API_BASE}/reviews", timeout=3)
        if res.status_code == 200:
            reviews = res.json()
            if reviews:
                df = pd.DataFrame(reviews)
                
                col1, col2 = st.columns(2)
                with col1:
                    status_filter = st.selectbox("Filter by Human Decision:", ["All", "Accepted", "Edited", "Rejected"])
                
                if status_filter != "All":
                    df = df[df["status"] == status_filter]

                st.dataframe(
                    df[["id", "diagnosis_id", "case_id", "status", "final_human_diagnosis", "reviewer_notes", "created_at"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No human reviews recorded yet. Run a diagnosis and submit a human review to populate history.")
        else:
            st.error("Failed to retrieve reviews from backend API.")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
