"""Prompt Builder Service for formatting evidence packages for LLM consumption."""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_master_prompt() -> str:
    """Loads master system prompt from prompts/diagnose_prompt.md."""
    prompt_file = Path(__file__).parent.parent / "prompts" / "diagnose_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "You are a Cisco network troubleshooting assistant. Return structured JSON."


def build_troubleshooting_prompt(
    symptom: str,
    topology_note: str,
    show_output: str,
    rule_results: List[Dict[str, Any]],
    concept: str = None
) -> str:
    """Builds a structured evidence package prompt for the LLM."""
    
    rule_summary = json.dumps(rule_results, indent=2)

    prompt = f"""### TROUBLESHOOTING CASE EVIDENCE PACKAGE

#### 1. NETWORK SYMPTOM:
{symptom or "No explicit symptom provided."}

#### 2. TOPOLOGY & NOTES:
{topology_note or "No topology note provided."}

#### 3. CISCO IOS SHOW COMMAND OUTPUT:
```text
{show_output or "No show command output provided."}
```

#### 4. DETERMINISTIC RULE ENGINE FINDINGS:
```json
{rule_summary}
```

#### 5. TARGET NETWORK CONCEPT / DOMAIN:
{concept or "General Networking"}

---
### INSTRUCTION:
Analyze the above evidence package. Identify the root cause, assign a confidence score (0.0 to 1.0), identify the OSI Layer, cite explicit evidence lines, specify the next Cisco IOS command to run, and list recommended fix steps.

Return strictly a valid JSON object matching the required schema.
"""
    return prompt
