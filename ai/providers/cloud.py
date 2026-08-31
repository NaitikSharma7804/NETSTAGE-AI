"""
Cloud LLM Provider (OpenAI, Gemini, or Claude compatible via HTTP REST).
"""

import json
import os
import uuid
import httpx
from typing import Optional
from ai.providers.base import LLMProvider
from ai.schemas.diagnosis import (
    ConfidenceLevel,
    DiagnosisRequest,
    DiagnosisResponse,
    EvidenceItem,
)


class CloudLLMProvider(LLMProvider):
    """Cloud-based LLM diagnostic provider using structured JSON output."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1"
    ):
        super().__init__(model_name, api_key or os.getenv("LLM_API_KEY", ""))
        self.base_url = base_url

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def _build_system_prompt(self) -> str:
        prompt_path = os.path.join("ai", "prompts", "diagnose_prompt.md")
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "You are NetSage AI, an expert Cisco Network Troubleshooting Assistant. Output valid JSON only."

    async def generate_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """Calls cloud LLM endpoint and validates structured output via Pydantic."""
        if not self.is_available():
            raise ValueError("Cloud LLM API key not configured. Set LLM_API_KEY or use DEMO_MODE=true.")

        prompt_system = self._build_system_prompt()
        rule_findings = "\n".join([f"- [{r.status}] {r.rule_name}: {r.message}" for r in (request.rule_results or [])])
        
        user_prompt = f"""
TROUBLESHOOTING CASE INPUT:
Case ID: {request.case_id or 'Ad-hoc'}
Symptom: {request.symptom}
Topology: {request.topology_note}
Target IP (user-supplied context only; it has not been probed): {request.target_ip or 'Not provided'}

SHOW COMMAND OUTPUTS:
{request.show_outputs}

DETERMINISTIC RULE ENGINE FINDINGS:
{rule_findings if rule_findings else 'No rule engine flags triggered.'}

Diagnose the fault and return structured JSON according to the schema.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_text)

        diag_id = f"DIAG-{request.case_id or 'CLOUD'}-{uuid.uuid4().hex[:6].upper()}"
        
        evidence_list = [
            EvidenceItem(
                source=item.get("source", "show-output"),
                observation=item.get("observation", ""),
                relevance=item.get("relevance", "")
            )
            for item in parsed.get("evidence", [])
        ]

        conf_str = parsed.get("confidence", "medium").lower()
        confidence = ConfidenceLevel(conf_str) if conf_str in ["low", "medium", "high"] else ConfidenceLevel.MEDIUM

        return DiagnosisResponse(
            diagnosis_id=diag_id,
            case_id=request.case_id,
            root_cause=parsed.get("root_cause", "Diagnosed network fault"),
            confidence=confidence,
            osi_layer=parsed.get("osi_layer", "Layer 3 (Network)"),
            affected_component=parsed.get("affected_component", "Cisco Device"),
            evidence=evidence_list,
            next_command=parsed.get("next_command", "show running-config"),
            fix_steps=parsed.get("fix_steps", ["Review network configuration"]),
            alternative_causes=parsed.get("alternative_causes", []),
            raw_response=raw_text
        )
