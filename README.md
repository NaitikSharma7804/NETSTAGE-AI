# 🛡️ NetSage AI

### Evidence-Based Cisco Network Troubleshooting with AI, Rule Validation & Human Review

NetSage AI is an AI-assisted network troubleshooting platform designed for **Cisco Packet Tracer and Cisco-style laboratory environments**.

The system combines a deterministic Python rule engine with AI-based reasoning to analyze network problems, identify potential root causes, provide evidence-backed recommendations, and guide the user through human review and post-fix verification.

> **AI ASSISTS. RULES VALIDATE. HUMANS DECIDE. VERIFICATION CONFIRMS.**

---

## 🎯 Project Objective

Network troubleshooting often requires engineers to analyze multiple Cisco CLI outputs, identify configuration errors, determine the root cause, apply a fix, and verify whether the problem has been resolved.

NetSage AI aims to make this process faster and more structured by combining:

- 🤖 AI-assisted diagnosis
- ⚙️ Deterministic networking rules
- 📋 Evidence-based reasoning
- 👤 Human-in-the-loop review
- 🔧 Cisco CLI fix recommendations
- ✅ Closed-loop verification
- 📊 Analytics and audit logging

The project is designed as an **educational prototype** and does not autonomously modify live network devices.

---

# 🧠 How NetSage AI Works

```text
Cisco Packet Tracer / Network Lab
              │
              ▼
       Network Problem
              │
              ▼
      CLI / Show Outputs
              │
              ▼
       FastAPI Backend
          │         │
          ▼         ▼
    Rule Engine    AI Reasoning
          │         │
          └────┬────┘
               ▼
        Evidence Fusion
               │
               ▼
      Structured Diagnosis
               │
               ▼
       Human Review Gate
        │      │      │
        ▼      ▼      ▼
      ACCEPT  EDIT   REJECT
               │
               ▼
        Final Decision
               │
               ▼
     Manual Cisco Configuration
               │
               ▼
       Verification Testing
               │
          ┌────┴────┐
          ▼         ▼
        PASS       FAIL
               │
               ▼
        Database + Analytics
               │
               ▼
       Streamlit Dashboard

✨ Key Features
1. 📚 40 Network Troubleshooting Cases

The project includes 40 canonical Cisco troubleshooting scenarios covering multiple networking domains.

Networking domains include:
VLAN configuration
Default Gateway & Subnetting
DHCP & DHCP Relay
DNS Resolution
Routing & OSPF
Access Control Lists
NAT & PAT
Wireless LAN
Trunking & Interfaces
Advanced Cisco scenarios

Examples include:

Incorrect default gateway
Subnet mask mismatch
Missing VLAN
Incorrect switchport configuration
Missing DHCP relay
DNS configuration problems
OSPF MTU mismatch
ACL filtering errors
NAT configuration issues
BPDU Guard err-disable
HSRP virtual IP mismatch
EtherChannel configuration mismatch
⚙️ Deterministic Rule Engine

The rule_engine/ module contains pure Python networking validation rules.

Unlike an LLM, deterministic rules provide predictable results for known configuration problems.

The rule engine analyzes Cisco-style show command outputs and checks for issues such as:

Invalid IP addresses
Duplicate IP addresses
Subnet inconsistencies
Default gateway problems
VLAN mismatches
Interface shutdown states
Duplex mismatches
BPDU Guard errors
Routing problems
OSPF configuration mismatches
ACL errors
DHCP relay issues
NAT configuration problems
🤖 AI Diagnosis

NetSage AI uses structured AI reasoning to generate a troubleshooting diagnosis.

Each diagnosis is expected to contain:

Root Cause
Confidence Level
OSI Layer
Supporting Evidence
Next Diagnostic Command
Recommended Cisco CLI Fix
Alternative Possible Causes

AI responses are validated using Pydantic schemas to maintain a consistent structure.

The system also supports a mock/offline AI provider for demonstrations.

🔀 Evidence Fusion

The Evidence Fusion layer combines:

Deterministic Rule Findings
            +
       AI Diagnosis
            +
     Network Evidence
            ↓
      Evidence Fusion
            ↓
   Structured Diagnosis

If the AI and rule engine disagree, the conflict is surfaced rather than hidden.

This allows a human engineer to investigate the disagreement before accepting the diagnosis.

👤 Human-in-the-Loop

NetSage AI does not allow AI to make the final decision automatically.

Every diagnosis can be:

✅ ACCEPT

The engineer agrees with the AI diagnosis.

✏️ EDIT

The engineer modifies the diagnosis based on additional knowledge or evidence.

❌ REJECT

The engineer determines that the diagnosis is incorrect.

A reviewer must provide a reason for edits and rejections.

🛡️ Responsible AI

The project follows four major safety principles:

AI ASSISTS
     ↓
RULES VALIDATE
     ↓
HUMANS DECIDE
     ↓
VERIFICATION CONFIRMS
Safety Guardrails
No Autonomous Network Changes
AI does not directly modify routers, switches, or firewalls.
Mandatory Human Review
AI-generated diagnoses must pass through a human review step.
Transparent AI Errors
The system intentionally records cases where human reviewers correct AI diagnoses.
Closed-Loop Verification
A proposed fix is not considered successful until it is verified.
🔧 Closed-Loop Verification

After a fix is applied manually, the system records verification evidence such as:

Ping Test
   ↓
Show Command
   ↓
Connectivity Check
   ↓
PASS / FAIL

This prevents the system from assuming that a recommended fix actually worked.

📊 Dashboard

The project includes an interactive Streamlit dashboard.

The dashboard provides:

Home & Overview
Troubleshoot & Diagnose
Cases Catalog
Human Review
Analytics
Responsible AI
Technical / System information

The dashboard also displays project metrics such as:

Total troubleshooting cases
AI diagnoses
Human reviews
AI agreement rate
Verification success rate
Corrected AI cases
🖥️ Screenshots
NetSage AI Dashboard

Add your project screenshot here.

![NetSage AI Dashboard](docs/images/dashboard.png)
Troubleshooting Module

Add screenshot here.

![Troubleshooting](docs/images/troubleshooting.png)
Human Review

Add screenshot here.

![Human Review](docs/images/human-review.png)
🏗️ Project Structure
NetSage-AI/
│
├── ai/
│   ├── __init__.py
│   └── ...
│
├── backend/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── main.py
│   └── ...
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── cases.csv
│   ├── evaluations.csv
│   ├── reviews.csv
│   └── verifications.csv
│
├── demo/
│   ├── scenario_walkthrough.md
│   └── RECORDING_CHECKLIST.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── responsible_ai.md
│   └── setup.md
│
├── rule_engine/
│   ├── acl_rules.py
│   ├── dhcp_rules.py
│   ├── gateway_rules.py
│   ├── interface_rules.py
│   ├── ip_rules.py
│   ├── nat_rules.py
│   ├── routing_rules.py
│   ├── subnet_rules.py
│   ├── vlan_rules.py
│   └── engine.py
│
├── scripts/
│   ├── seed_db.py
│   ├── validate_dataset.py
│   ├── evaluate_ai.py
│   └── ...
│
├── tests/
│   ├── test_rule_engine.py
│   ├── test_api_endpoints.py
│   ├── test_human_workflow.py
│   └── ...
│
├── .env.example
├── requirements.txt
├── start_netsage.py
└── README.md
🛠️ Technology Stack
Technology	Purpose
Python	Core application logic
FastAPI	Backend REST API
Uvicorn	API server
Streamlit	Interactive dashboard
Pydantic	Structured data & AI output validation
SQLAlchemy	Database ORM
SQLite	Persistent database
Pandas	Data processing & analytics
Plotly	Interactive visualizations
pytest	Automated testing
Cisco Packet Tracer	Network simulation environment
🚀 Installation & Setup
Prerequisites
Python 3.10+
Git
Modern web browser
Cisco Packet Tracer (for network lab scenarios)
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/NetSage-AI.git
cd NetSage-AI
2. Create a Virtual Environment
Windows PowerShell
python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

If PowerShell blocks activation:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
Linux / macOS
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Configuration

Create a .env file based on .env.example.

For offline demonstration:

APP_ENV=development
DATABASE_URL=sqlite:///./netsage.db

LLM_PROVIDER=mock
LLM_MODEL=mock-netsage-v1
LLM_API_KEY=

DEMO_MODE=true
Offline Demo Mode

The project supports:

DEMO_MODE=true

This allows NetSage AI to run without an external AI API key.

🗄️ Initialize the Database

Run:

python scripts/seed_db.py

This initializes the SQLite database and loads the troubleshooting cases and demo review data.

▶️ Running the Application
Option 1 — Start Backend

Run:

uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

Backend:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs
Option 2 — Start Dashboard

Open another terminal and activate the virtual environment.

Then run:

streamlit run dashboard/app.py --server.port 8501

Open:

http://localhost:8501
Option 3 — Start the Project Launcher

The project also provides:

python start_netsage.py

This can be used as the main application launcher.

🧪 Testing

Run all automated tests:

pytest -v tests/

Validate the troubleshooting dataset:

python scripts/validate_dataset.py

Run the AI evaluation:

python scripts/evaluate_ai.py
📡 REST API

The FastAPI backend provides the following major endpoints:

Method	Endpoint	Purpose
GET	/health	Check application health
GET	/cases	List troubleshooting cases
GET	/cases/{case_id}	Get a specific case
POST	/cases	Create a case
POST	/diagnose	Run AI + rule-based diagnosis
POST	/validate	Run deterministic rule validation
POST	/review	Submit human review
GET	/reviews	View review history
POST	/verify	Record verification result
GET	/verifications	View verification records
GET	/analytics	Retrieve analytics
GET	/responsible-ai	View responsible AI audit cases

Interactive documentation is available at:

http://127.0.0.1:8000/docs
📈 Example Diagnostic Workflow

Suppose a PC cannot communicate with another network.

The user provides:

Symptom:
PC cannot access the internet

Evidence:
show ip interface brief
show ip route
show running-config
show access-lists

NetSage AI processes the information:

1. Collect Evidence
        ↓
2. Run Rule Engine
        ↓
3. Generate AI Diagnosis
        ↓
4. Fuse Evidence
        ↓
5. Assign Confidence
        ↓
6. Human Reviews Diagnosis
        ↓
7. Engineer Applies Fix
        ↓
8. Verify Connectivity

Example:

Root Cause:
Incorrect default gateway

Evidence:
Host gateway does not belong to the configured subnet.

Recommended Fix:
Configure the correct default gateway.

Verification:
Ping successful → PASS
⚖️ Example of Human Correction

NetSage AI intentionally demonstrates that AI can make incorrect diagnoses.

For example:

Case: DHCP Relay

AI Diagnosis:

DHCP server has exhausted its IP pool.

Human Correction:

The DHCP pool is available.

The actual problem is a missing
ip helper-address on the router subinterface.

The system records this correction as part of its Responsible AI audit process.

This demonstrates why the project uses:

Human review instead of autonomous AI decisions.

📊 Project Metrics

The dashboard tracks metrics including:

Total Cases
AI Diagnoses
Human Reviews
AI Agreement Rate
Verification Success Rate
Corrected AI Cases

These metrics help evaluate both the technical performance of the troubleshooting system and the effectiveness of human oversight.

🎓 Educational Use

NetSage AI is designed primarily for:

Cisco networking education
Network troubleshooting labs
AI-assisted network diagnostics
Cisco Packet Tracer demonstrations
Responsible AI demonstrations
Human-in-the-loop AI research
Academic project demonstrations

It is not intended to autonomously configure or modify production network infrastructure.

🔒 Security & Safety

NetSage AI follows a conservative architecture:

No autonomous device configuration
No automatic execution of Cisco CLI commands
Human approval is required
AI evidence is explicitly displayed
AI/rule conflicts are surfaced
Fixes require verification
Review decisions are stored for auditing
📚 Documentation

Additional documentation is available in the docs/ directory:

docs/setup.md — Installation and setup
docs/architecture.md — System architecture
docs/api.md — REST API documentation
docs/responsible_ai.md — Responsible AI and human corrections
demo/scenario_walkthrough.md — Demonstration workflow
🚧 Project Status

Status: Educational Prototype / Cisco Networking Lab Project

The current implementation focuses on:

Evidence-based troubleshooting
Deterministic rule validation
AI-assisted reasoning
Human review
Fix verification
Analytics
Responsible AI auditing

Future improvements could include:

Real Cisco device integrations
More networking scenarios
Additional vendor support
Advanced topology analysis
More LLM providers
Automated evidence collection
Improved diagnostic benchmarking
👥 Team
NetSage AI — Cisco Networking / AI Project

Contributors:

Add Team Member 1 — AI & Backend
Add Team Member 2 — Network Rules & Dataset
Add Team Member 3 — Dashboard & Analytics

Update the contributor section with your actual team members and GitHub profiles.

📄 License

This project is intended for educational and academic use.

Add an appropriate open-source license if you plan to distribute the project publicly.

⭐ Key Takeaway

NetSage AI is not designed to replace a network engineer.

It is designed to assist the engineer with evidence-based diagnosis while keeping humans responsible for the final decision.

        🤖 AI ASSISTS
              ↓
        ⚙️ RULES VALIDATE
              ↓
        👤 HUMANS DECIDE
              ↓
        ✅ VERIFICATION CONFIRMS
