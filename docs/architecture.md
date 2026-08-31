# NetSage AI - Architectural Blueprint

NetSage AI is structured around a three-tier reasoning architecture:
1. **Deterministic Network Validation** (Python Rule Engine)
2. **AI/LLM Semantic & Topological Reasoning** (Pydantic Structured Inferences)
3. **Human-in-the-Loop Decision & Closed-Loop Verification**

```
+-----------------------------------------------------------------------------------+
|                                Cisco Packet Tracer                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
                         Troubleshooting Case (Symptom + CLI)
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                                 FastAPI Backend                                   |
|   +------------------------------------+-------------------------------------+  |
|   | Deterministic Python Rule Engine   | AI / LLM Reasoning Engine (Prompts) |  |
|   +------------------------------------+-------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|                         Evidence Fusion & Conflict Engine                         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
                         Structured Diagnostic Proposition
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                          Human-in-the-Loop Review Gate                            |
|                     [ ACCEPT ]     [ EDIT ]     [ REJECT ]                        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
                            Manual Cisco Configuration Fix
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                          Closed-Loop Fix Verification                             |
|                               [ PASS ] / [ FAIL ]                                 |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
                           SQLite Database + Audit Log
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     Streamlit Dashboard (Plotly + Pandas)                         |
+-----------------------------------------------------------------------------------+
```

## Component Breakdown

### 1. Deterministic Rule Engine (`rule_engine/`)
Executes 22 pure-Python static analysis rules against show command outputs. It checks:
- Duplicate IP and invalid host IP allocations
- Subnet mask and boundary inconsistencies
- Default gateway reachability and HSRP/VRRP virtual IP alignment
- VLAN database missing IDs and 802.1Q subinterface tag mismatches
- Physical interface states (administratively shutdown, duplex mismatches, BPDU Guard err-disable)
- Routing anomalies (missing default static routes, OSPF area/MTU mismatches, recursive routing failures)
- Access Control List errors (inverted wildcard masks, implicit deny drops, missing TCP established flags)
- DHCP relay gaps and pool exhaustion
- NAT outside interface omissions and PAT overload keyword omissions

### 2. AI Reasoning Layer (`ai/`)
- Abstracts LLM providers (`CloudLLMProvider`, `LocalLLMProvider`, `MockLLMProvider`).
- Strict JSON output enforcement via Pydantic schemas.
- Version-controlled Markdown prompts with mandatory evidence citation and calibrated confidence levels.

### 3. Evidence Fusion Service (`backend/services/evidence_service.py`)
- Cross-references deterministic findings with AI hypotheses.
- Detects discrepancies or unaddressed rule alerts.
- Calibrates confidence downwards if conflicts are detected.

### 4. Human-in-the-Loop Governance (`backend/services/review_service.py`)
- Forces human approval before any action is considered confirmed.
- Requires engineering justifications for all edits and rejections.

### 5. Persistence & Analytics (`backend/database/` & `dashboard/`)
- Relational storage in SQLite for all cases, diagnoses, reviews, verifications, and execution metrics.
- Pandas aggregations feeding real-time Plotly charts.