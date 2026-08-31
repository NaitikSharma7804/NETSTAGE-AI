"""Streamlit About & System Architecture Page."""

import streamlit as st


def show_about_page():
    st.title("ℹ️ About NetSage AI")
    st.markdown(
        """
        ### Cisco Internship Project Overview
        NetSage AI is an AI-assisted Cisco network troubleshooting helper for Packet Tracer lab problems.
        
        #### Core Pillars:
        1. **Deterministic Rule Validation**: Runs non-LLM Python parsing checks for duplicate IPs, interface shutdown, subnet mask mismatches, missing VLANs, and route table omissions.
        2. **Structured AI Diagnosis**: Formats verified evidence packages into strict Pydantic-validated JSON schemas.
        3. **Mandatory Human Oversight**: Prohibits automatic application of network changes. Every diagnosis must pass human review (Accepted, Edited, Rejected).
        4. **Responsible AI Governance**: Audit trail logging for AI error modes and continuous model calibration.
        
        ---
        #### Logical Architecture:
        ```text
        Packet Tracer Case -> Streamlit Dashboard -> FastAPI Backend
                                                        |
                                          +-------------+-------------+
                                          |                           |
                                          v                           v
                              Deterministic Rule Engine     AI Diagnosis Engine (OpenAI/Mock)
                                          |                           |
                                          +-------------+-------------+
                                                        |
                                                        v
                                                Combined Evidence
                                                        |
                                                        v
                                                Human Oversight Review
                                               (Accept / Edit / Reject)
                                                        |
                                                        v
                                              SQLite DB & Analytics
        ```
        """
    )
