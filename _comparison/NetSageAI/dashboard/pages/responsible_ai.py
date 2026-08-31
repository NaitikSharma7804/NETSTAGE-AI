"""Streamlit Responsible AI Transparency & Correction Log Page."""

import streamlit as st
import pandas as pd
import requests

API_BASE = "http://127.0.0.1:8000/api"


def show_responsible_ai_page():
    st.title("🛡️ Responsible AI & Model Governance Log")
    st.markdown(
        """
        NetSage AI enforces **evidence-based AI diagnosis** with **mandatory human oversight**.
        This transparency audit log captures cases where human engineers corrected or rejected AI recommendations,
        documenting root causes for model error and lessons learned for future prompt calibration.
        """
    )

    try:
        res = requests.get(f"{API_BASE}/responsible-ai", timeout=3)
        if res.status_code == 200:
            logs = res.json()
            if logs:
                df = pd.DataFrame(logs)

                st.markdown(f"### 📑 Transparency Audit Trail ({len(df)} Records)")

                st.dataframe(
                    df[["case_id", "record_type", "human_decision", "ai_diagnosis", "correction", "reason", "lesson"]],
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("---")
                st.markdown("### 🔍 Case Correction Deep-Dive")
                selected_case = st.selectbox("Select Corrected Case ID:", df["case_id"].tolist())

                if selected_case:
                    row = df[df["case_id"] == selected_case].iloc[0]
                    
                    st.markdown(
                        f"""
                        <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #f43f5e;">
                            <h4 style="color: #f43f5e; margin-top: 0;">Case {row['case_id']} — Decision: {row['human_decision']}</h4>
                            <p><strong>🤖 Initial AI Diagnosis:</strong> <br/><span style="color: #cbd5e1;">{row['ai_diagnosis']}</span></p>
                            <p><strong>👨‍💻 Verified Human Correction:</strong> <br/><span style="color: #4ade80; font-weight: 500;">{row['correction']}</span></p>
                            <p><strong>⚠️ Reason for AI Error:</strong> <br/><span style="color: #fbbf24;">{row['reason']}</span></p>
                            <p><strong>💡 Lesson Learned & Prompt Rule:</strong> <br/><span style="color: #38bdf8;">{row['lesson']}</span></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No corrected records found in Responsible AI log.")
        else:
            st.error("Failed to load Responsible AI log.")
    except Exception as e:
        st.error(f"Error fetching Responsible AI log: {e}")
