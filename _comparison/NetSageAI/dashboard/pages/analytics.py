"""Streamlit Analytics Page using Plotly charts."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests

API_BASE = "http://127.0.0.1:8000/api"


def show_analytics_page():
    st.title("📈 NetSage AI Diagnostics Analytics")
    st.markdown("Metrics on issue distribution, severity levels, OSI layer counts, and AI-vs-Human agreement rate.")

    try:
        res = requests.get(f"{API_BASE}/analytics", timeout=3)
        if res.status_code == 200:
            data = res.json()

            # Top Metrics
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Total Lab Cases", data["total_cases"])
            c2.metric("Diagnoses Executed", data["diagnoses_run"])
            c3.metric("Pending Review", data.get("pending_review_count", 0))
            c4.metric("Human Agreement", f"{data['agreement_rate']}%")
            c5.metric("Real Corrections", data.get("real_human_corrections", 0))
            c6.metric("High Severity", data["high_severity_count"])

            st.markdown("---")

            col1, col2 = st.columns(2)

            # 1. Cases by Concept
            with col1:
                st.markdown("### 🏷️ Cases by Networking Concept")
                concept_data = data.get("by_concept", {})
                if concept_data:
                    fig_concept = px.bar(
                        x=list(concept_data.keys()),
                        y=list(concept_data.values()),
                        labels={"x": "Concept", "y": "Number of Cases"},
                        color=list(concept_data.keys()),
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                    st.plotly_chart(fig_concept, use_container_width=True)

            # 2. Cases by Severity
            with col2:
                st.markdown("### ⚠️ Cases by Severity Level")
                sev_data = data.get("by_severity", {})
                if sev_data:
                    fig_sev = px.pie(
                        names=list(sev_data.keys()),
                        values=list(sev_data.values()),
                        color=list(sev_data.keys()),
                        color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"},
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_sev, use_container_width=True)

            col3, col4 = st.columns(2)

            # 3. AI vs Human Agreement
            with col3:
                st.markdown("### 🤝 AI vs Human Oversight Decisions")
                acc = data.get("accepted_count", 0)
                ed = data.get("edited_count", 0)
                rej = data.get("rejected_count", 0)
                
                fig_rev = px.pie(
                    names=["Accepted", "Edited", "Rejected"],
                    values=[acc, ed, rej],
                    color=["Accepted", "Edited", "Rejected"],
                    color_discrete_map={"Accepted": "#2ecc71", "Edited": "#f39c12", "Rejected": "#e74c3c"},
                    template="plotly_dark"
                )
                st.plotly_chart(fig_rev, use_container_width=True)

            # 4. OSI Layer Distribution
            with col4:
                st.markdown("### 🌐 OSI Layer Distribution")
                osi_data = data.get("by_osi_layer", {})
                if osi_data:
                    fig_osi = px.bar(
                        x=list(osi_data.keys()),
                        y=list(osi_data.values()),
                        labels={"x": "OSI Layer", "y": "Count"},
                        color=list(osi_data.keys()),
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_osi, use_container_width=True)
        else:
            st.error("Failed to fetch analytics data.")
    except Exception as e:
        st.error(f"Error connecting to analytics endpoint: {e}")
