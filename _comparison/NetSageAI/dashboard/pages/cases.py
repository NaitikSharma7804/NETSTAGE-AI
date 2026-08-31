"""Streamlit Case History / Dataset Library Page."""

import streamlit as st
import pandas as pd
import requests

API_BASE = "http://127.0.0.1:8000/api"


def show_cases_page():
    st.title("📂 Cisco Packet Tracer Case Library")
    st.markdown("Explore preloaded lab cases across 8 networking concepts.")

    st.info("ℹ️ **DEVELOPMENT SAMPLE DATASET — PENDING NETWORKING TEAM VERIFICATION**")

    try:
        res = requests.get(f"{API_BASE}/cases", timeout=3)
        if res.status_code == 200:
            cases_data = res.json()
            df = pd.DataFrame(cases_data)

            if not df.empty:
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_concept = st.selectbox("Filter by Concept:", ["All"] + sorted(list(df["concept"].unique())))
                with col2:
                    selected_severity = st.selectbox("Filter by Severity:", ["All"] + sorted(list(df["severity"].unique())))
                with col3:
                    selected_osi = st.selectbox("Filter by OSI Layer:", ["All"] + sorted(list(df["osi_layer"].unique())))

                filtered_df = df.copy()
                if selected_concept != "All":
                    filtered_df = filtered_df[filtered_df["concept"] == selected_concept]
                if selected_severity != "All":
                    filtered_df = filtered_df[filtered_df["severity"] == selected_severity]
                if selected_osi != "All":
                    filtered_df = filtered_df[filtered_df["osi_layer"] == selected_osi]

                st.markdown(f"Displaying **{len(filtered_df)}** of **{len(df)}** total cases.")

                st.dataframe(
                    filtered_df[["case_id", "dataset_status", "concept", "severity", "osi_layer", "symptom", "expected_fault"]],
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("---")
                st.markdown("### 🔎 Case Detail Inspector")
                selected_case_id = st.selectbox("Select Case ID to view full CLI output & expected fault:", filtered_df["case_id"].tolist())

                if selected_case_id:
                    case_row = filtered_df[filtered_df["case_id"] == selected_case_id].iloc[0]
                    
                    st.subheader(f"Case {case_row['case_id']}: {case_row['concept']} ({case_row['severity']} Severity)")
                    st.markdown(f"**Symptom**: {case_row['symptom']}")
                    st.markdown(f"**Topology Note**: {case_row['topology_note']}")
                    st.markdown(f"**Expected Fault**: `{case_row['expected_fault']}`")
                    st.markdown(f"**OSI Layer**: {case_row['osi_layer']}")
                    
                    st.markdown("**Cisco IOS CLI Show Command Output**:")
                    st.code(case_row["show_output"], language="text")
        else:
            st.error("Error fetching cases from API.")
    except Exception as e:
        st.error(f"Failed to load cases: {e}")
