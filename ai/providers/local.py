"""
Local LLM Provider (Ollama / vLLM REST API).
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


class LocalLLMProvider(LLMProvider):
    """Local LLM Diagnostic Provider communicating with Ollama or vLLM."""

    def __init__(
        self,
        model_name: str = "llama3:8b",
        api_url: Optional[str] = None
    ):
        super().__init__(model_name)
        self.api_url = api_url or os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")

    def is_available(self) -> bool:
        return True

    async def generate_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """Sends request to local Ollama instance with format=json."""
        rule_findings = "\n".join([f"- [{r.status}] {r.rule_name}: {r.message}" for r in (request.rule_results or [])])
        
        prompt = f"""
You are NetSage AI, a Cisco Network Troubleshooting Assistant. Return JSON only.
Schema:
{{
  "root_cause": "...",
  "confidence": "low|medium|high",
  "osi_layer": "...",
  "affected_component": "...",
  "evidence": [{{"source":"...", "observation":"...", "relevance":"..."}}],
  "next_command": "...",
  "fix_steps": ["..."],
  "alternative_causes": ["..."]
}}

Symptom: {request.symptom}
Topology: {request.topology_note}
Target IP (user-supplied context only; it has not been probed): {request.target_ip or 'Not provided'}
Show Outputs:
{request.show_outputs}
Rule Findings:
{rule_findings}
"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(self.api_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_text = data.get("response", "{}")
                parsed = json.loads(raw_text)
        except Exception as e:
            # Fallback to mock on local endpoint failure
            from ai.providers.mock import MockLLMProvider
            mock = MockLLMProvider()
            res = await mock.generate_diagnosis(request)
            res.root_cause += f" [Local LLM fallback: {str(e)}]"
            return res

        diag_id = f"DIAG-{request.case_id or 'LOCAL'}-{uuid.uuid4().hex[:6].upper()}"
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
            root_cause=parsed.get("root_cause", "Diagnosed local fault"),
            confidence=confidence,
            osi_layer=parsed.get("osi_layer", "Layer 3 (Network)"),
            affected_component=parsed.get("affected_component", "Cisco Device"),
            evidence=evidence_list,
            next_command=parsed.get("next_command", "show running-config"),
            fix_steps=parsed.get("fix_steps", ["Review network configuration"]),
            alternative_causes=parsed.get("alternative_causes", []),
            raw_response=raw_text
        )
