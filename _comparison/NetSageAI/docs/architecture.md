# NetSage AI Architecture Specification

NetSage AI is an AI-assisted Cisco network troubleshooting assistant for Packet Tracer lab problems.

## System Architecture Diagram

```text
Packet Tracer Case
        |
        v
Streamlit Dashboard (Port 8501)
        |
        v
FastAPI Backend (Port 8000)
        |
        +----------------------+
        |                      |
        v                      v
Deterministic Rule Engine    AI Diagnosis Engine
(Python checks)              (OpenAI API / Mock Fallback)
        |                      |
        |                      v
        |                 Structured Pydantic Validation
        |                      |
        +----------+-----------+
                   |
                   v
             Combined Evidence Package
                   |
                   v
             Mandatory Human Review
          (Accept / Edit / Reject)
                   |
                   v
             SQLite Database (netsage.db)
                   |
                   v
          Plotly Analytics & Responsible AI Audit Log
```

## Core Design Principles

1. **Deterministic First**: Basic network anomalies (shutdown interfaces, duplicate IPs, subnet mismatches, missing VLANs, routing omissions) are caught deterministically by Python rules before calling the LLM.
2. **Strict Schema Enforcment**: Raw LLM output is validated through Pydantic (`AIDiagnosisSchema`). Malformed responses are rejected.
3. **Mandatory Human Oversight**: The AI system is advisory only. It NEVER automatically applies network changes or marks a diagnosis as final without human engineering signoff.
4. **Responsible AI Auditing**: Human corrections and rejected diagnoses are automatically audited in `data/responsible_ai_log.csv` to track model failure modes and lessons learned.
