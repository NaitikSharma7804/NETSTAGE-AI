"""NetSage AI - Master Streamlit Application."""

import streamlit as st
import sys
from pathlib import Path

# Add project root directory to python path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dashboard.pages.home import show_home
from dashboard.pages.diagnosis import show_diagnosis_page
from dashboard.pages.cases import show_cases_page
from dashboard.pages.review import show_review_page
from dashboard.pages.analytics import show_analytics_page
from dashboard.pages.responsible_ai import show_responsible_ai_page
from dashboard.pages.about import show_about_page

st.set_page_config(
    page_title="NetSage AI - Cisco Network Troubleshooting Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cisco-Inspired Professional Networking Aesthetic CSS
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            border-right: 1px solid #334155;
        }
        .main-header {
            background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
            padding: 16px 24px;
            border-radius: 10px;
            margin-bottom: 24px;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .main-header h2 {
            margin: 0;
            font-size: 1.6rem;
            font-weight: 700;
        }
        .main-header p {
            margin: 4px 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Banner Header
st.markdown(
    """
    <div class="main-header">
        <h2>⚡ NETSAGE AI — Cisco Network Troubleshooting Assistant</h2>
        <p>Deterministic Network Verification & Evidence-Based LLM Diagnostics for Packet Tracer</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "Home",
        "New Diagnosis",
        "Case History",
        "Human Review",
        "Analytics",
        "Responsible AI",
        "About"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("NetSage AI v1.0 • Cisco Internship Project")
st.sidebar.caption("System Mode: Advisory (Human Oversight Mandatory)")

# Page Router
if page == "Home":
    show_home()
elif page == "New Diagnosis":
    show_diagnosis_page()
elif page == "Case History":
    show_cases_page()
elif page == "Human Review":
    show_review_page()
elif page == "Analytics":
    show_analytics_page()
elif page == "Responsible AI":
    show_responsible_ai_page()
elif page == "About":
    show_about_page()
