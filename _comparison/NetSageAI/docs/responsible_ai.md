# NetSage AI - Responsible AI & Human Oversight Policy

## Governance Framework

NetSage AI is designed in compliance with Cisco Responsible AI principles for automated network diagnostics.

### Key Governance Policies:
1. **Advisory Role**: The AI system acts strictly as an advisory assistant. It is prohibited from executing CLI commands or mutating live network topologies autonomously.
2. **Deterministic Pre-Validation**: Basic syntax, IP address collision, and interface status checks are performed using deterministic Python code to prevent LLM hallucinations on basic facts.
3. **Pydantic Validation**: All LLM JSON responses are strictly validated for confidence ranges (0.0 - 1.0), OSI layer formatting, and structured evidence fields.
4. **Mandatory Human Oversight**: Every diagnostic output must pass through human review before being finalized.
5. **Continuous Improvement Audit Log**: All human edits and rejections are recorded in `data/responsible_ai_log.csv` to capture:
   - Initial AI hypothesis
   - Human decision & correction
   - Root cause of AI failure
   - Lesson learned / prompt guideline update
