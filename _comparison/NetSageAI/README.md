# ⚡ NetSage AI — AI-Assisted Cisco Network Troubleshooting Helper

NetSage AI is an AI-assisted Cisco network troubleshooting assistant built for Packet Tracer lab problems. It combines **deterministic Python network checks** with **structured evidence-based LLM diagnosis**, **evidence grounding validation**, **mandatory human oversight**, and **responsible AI auditing**.

> [!IMPORTANT]
> **Cisco Internship Dataset Notice**: The repository initially contains 32 development sample cases (`dataset_status = SAMPLE`). Final Packet Tracer verification must be performed by the Cisco networking team before marking cases as `VERIFIED`.

---

## 📌 Core Architectural Pillars & Hardening Highlights

1. **Dynamic LLM Provider Status**:
   - `/health` endpoint and UI status cards dynamically inspect the active runtime provider (`"llm_provider": "openai"`, `"mode": "live"` vs `"llm_provider": "mock"`, `"mode": "offline"`).
2. **Explicit Diagnosis Review Status**:
   - Every AI diagnosis defaults to `review_status = "Pending Review"`.
   - Diagnoses never automatically become `Accepted`.
   - Workflow: `AI Diagnosis` → `Pending Review` → `Human Review` → `Accepted` / `Edited` / `Rejected`.
3. **Evidence-Grounding Validation Layer**:
   - Validates AI evidence statements against symptoms, topology notes, CLI outputs, and rule findings.
   - Computes grounding status: `Verified`, `Partially Verified`, or `Unverified`.
   - Triggers UI warnings if ungrounded or unverified evidence is detected.
4. **Dataset Status (SAMPLE vs VERIFIED)**:
   - Tracks dataset status (`SAMPLE`, `VERIFIED`, `RETIRED`).
   - Displays persistent UI banner: `"DEVELOPMENT SAMPLE DATASET — PENDING NETWORKING TEAM VERIFICATION"`.
5. **Responsible AI Audit Log Hardening**:
   - Differentiates `DEVELOPMENT_EXAMPLE` (initial seed entries) from `REAL_TEAM_REVIEW` (live human corrections).
   - Counts only `REAL_TEAM_REVIEW` in real human correction metrics.
6. **Strict Analytics Agreement Rate**:
   - Agreement Rate Formula: `Accepted / (Accepted + Edited + Rejected)` computed across reviewed cases ONLY.
   - Diagnoses in `Pending Review` do not count as agreement.

---

## 🏗️ System Architecture

```text
Packet Tracer Case (SAMPLE / VERIFIED)
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
        |                 Pydantic Schema Validation
        |                      |
        |                      v
        |                 Evidence Grounding Validation
        |                 (Verified / Partial / Unverified)
        |                      |
        +----------+-----------+
                   |
                   v
             Combined Evidence Package
                   |
                   v
             Mandatory Human Oversight Review
          (Pending Review -> Accept / Edit / Reject)
                   |
                   v
             SQLite Database (netsage.db)
                   |
                   v
          Plotly Analytics & Responsible AI Audit Log
          (REAL_TEAM_REVIEW vs DEVELOPMENT_EXAMPLE)
```

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Backend API**: FastAPI, Uvicorn
- **Frontend Dashboard**: Streamlit
- **AI / LLM**: OpenAI API (with flexible provider abstraction & offline mock fallback)
- **Validation**: Pydantic v2 & Evidence Grounding Engine
- **Database**: SQLite, SQLAlchemy
- **Data & Visualization**: Pandas, Plotly
- **Testing**: Pytest, HTTPX

---

## 📁 Repository Structure

```text
NetSage-AI/
│
├── app/
│   ├── main.py                # FastAPI entrypoint with dynamic /health inspection
│   ├── config.py              # Configuration manager
│   ├── api/                   # REST API routes (cases, diagnosis, reviews)
│   ├── models/                # SQLAlchemy database models (CaseModel, DiagnosisModel, ReviewModel)
│   ├── schemas/               # Pydantic schemas (case_schema, diagnosis_schema, review_schema)
│   └── services/              # Business logic services (case_service, diagnosis_service, review_service)
│
├── ai/
│   ├── diagnosis.py           # AI diagnosis engine orchestrator
│   ├── evidence_grounding.py  # Evidence grounding validation engine
│   ├── prompt_builder.py      # Evidence package prompt builder
│   ├── response_validator.py  # Pydantic AIDiagnosisSchema response validator
│   └── provider.py            # LLM provider interface (OpenAIProvider vs MockLLMProvider)
│
├── prompts/                   # Master & domain-specific prompt library
│   ├── diagnose_prompt.md
│   ├── examples.md
│   ├── vlan_prompt.md
│   ├── routing_prompt.md
│   ├── dhcp_prompt.md
│   ├── dns_prompt.md
│   ├── acl_prompt.md
│   ├── nat_prompt.md
│   └── wireless_prompt.md
│
├── rules/                     # Deterministic Python rule checks
│   ├── checker.py             # Master rule engine runner
│   ├── ip_checks.py           # Duplicate IP & conflict checks
│   ├── subnet_checks.py       # Subnet mask mismatch checks
│   ├── gateway_checks.py      # Gateway & DHCP pool option checks
│   ├── vlan_checks.py         # VLAN database & trunk allowed list checks
│   ├── route_checks.py        # Static route & routing protocol checks
│   └── interface_checks.py    # Interface shutdown & err-disabled checks
│
├── dashboard/                 # Streamlit Web UI
│   ├── app.py                 # Main Streamlit app with Cisco theme
│   ├── pages/                 # Home, Diagnosis, Cases, Review, Analytics, Responsible AI, About
│   └── components/            # Diagnosis cards, evidence panels, review forms, status cards
│
├── data/
│   ├── cases.csv              # 32 preloaded sample lab cases (dataset_status = SAMPLE)
│   └── responsible_ai_log.csv # Audit trail of human corrections (record_type = REAL_TEAM_REVIEW)
│
├── database/
│   ├── database.py            # SQLite engine & session setup
│   └── seed.py                # Database startup seed & SQLite column migration utility
│
├── tests/                     # Automated test suite
│   ├── test_rules.py
│   ├── test_ai_schema.py
│   ├── test_cases.py
│   ├── test_api.py
│   └── test_hardening.py      # Post-audit hardening feature tests
│
├── packet_tracer/             # Lab resources organized by domain
├── docs/                      # Architecture, API, and Responsible AI docs
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py                     # Unified launcher script
```

---

## 📥 Installation & Setup

### 1. Clone & Setup Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

If an OpenAI API key is present:
```text
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
```
*Note: If no API key is provided, NetSage AI operates in offline mock mode (`"mode": "offline"`).*

---

## ⚡ How to Run

### Run Both Backend & Dashboard Concurrently:
```powershell
python run.py
```

### Run FastAPI Backend Only:
```powershell
python run.py --backend
# Access Swagger API Docs at: http://127.0.0.1:8000/docs
```

### Run Streamlit Dashboard Only:
```powershell
python run.py --frontend
# Access Dashboard at: http://127.0.0.1:8501
```

---

## 🧪 Running Automated Tests

Run the full Pytest test suite (30 automated tests):

```powershell
python -m pytest -v
```

Tests cover:
- Dynamic LLM provider inspection (`/health`)
- `Pending Review` default diagnosis state
- Review state transitions (`Accepted`, `Edited`, `Rejected`)
- Evidence grounding validation (`Verified`, `Partially Verified`, `Unverified`)
- Dataset status (`SAMPLE` vs `VERIFIED`)
- Responsible AI record types (`REAL_TEAM_REVIEW` vs `DEVELOPMENT_EXAMPLE`)
- Agreement rate formula enforcement across reviewed cases
- Deterministic Python rule checks across all 8 domains

---

## 🛡️ Responsible AI & Mandatory Human Oversight

NetSage AI is strictly an **advisory troubleshooting assistant**. It does NOT automatically push configuration changes to networking hardware.

Every diagnosis requires explicit Human Review:
1. **Accepted**: AI root cause verified accurate by engineer.
2. **Edited**: Engineer modifies root cause or fix steps. Correction logged in `responsible_ai_log.csv` as `REAL_TEAM_REVIEW`.
3. **Rejected**: AI diagnosis deemed incorrect. AI error mode and lesson learned audited as `REAL_TEAM_REVIEW`.

---

## 📄 License & Team
Developed for the **Cisco Internship Project**.
Designed for Packet Tracer network troubleshooting research and education.
