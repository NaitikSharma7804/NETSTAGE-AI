"""Streamlit Dashboard Home Page."""

import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000/api"


def show_home():
    st.title("🌐 NetSage AI - Cisco Network Troubleshooting Assistant")
    st.markdown(
        """
        Welcome to **NetSage AI**, an AI-assisted Cisco network troubleshooting helper for Packet Tracer lab problems.
        Combines **deterministic Python network checks** with **structured evidence-based LLM diagnosis** and **mandatory human oversight**.
        """
    )

    # Fetch summary metrics
    try:
        res = requests.get(f"{API_BASE}/analytics", timeout=3)
        if res.status_code == 200:
            data = res.json()
            total_cases = data.get("total_cases", 0)
            diagnoses_run = data.get("diagnoses_run", 0)
            pending_rev = data.get("pending_review_count", 0)
            accepted = data.get("accepted_count", 0)
            edited = data.get("edited_count", 0)
            rejected = data.get("rejected_count", 0)
            agreement = data.get("agreement_rate", 0.0)
            real_corrections = data.get("real_human_corrections", 0)
        else:
            total_cases, diagnoses_run, pending_rev, accepted, edited, rejected, agreement, real_corrections = 32, 0, 0, 0, 0, 0, 0.0, 0
    except Exception:
        total_cases, diagnoses_run, pending_rev, accepted, edited, rejected, agreement, real_corrections = 32, 0, 0, 0, 0, 0, 0.0, 0

    st.info("ℹ️ **DEVELOPMENT SAMPLE DATASET — PENDING NETWORKING TEAM VERIFICATION**")

    # Summary Cards
    st.markdown("### 📊 Operational Summary")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Cases", total_cases)
    c2.metric("Diagnoses Run", diagnoses_run)
    c3.metric("Pending Review", pending_rev)
    c4.metric("Accepted", accepted)
    c5.metric("Agreement Rate", f"{agreement}%")
    c6.metric("Real Corrections", real_corrections)

    st.markdown("---")
    st.markdown("### 🚀 Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-top: 4px solid #38bdf8;">
                <h4>🔍 New Diagnosis</h4>
                <p>Run deterministic rule checks and LLM analysis on Packet Tracer CLI outputs.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-top: 4px solid #4ade80;">
                <h4>📂 Case Library</h4>
                <p>Browse 30+ preloaded Cisco Packet Tracer lab cases across 8 networking concepts.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-top: 4px solid #f43f5e;">
                <h4>🛡️ Responsible AI Log</h4>
                <p>Review transparency logs of human corrections and lessons learned.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
