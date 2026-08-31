"""AI Diagnosis Engine Orchestrator."""

import json
from typing import Dict, Any, List
from ai.provider import get_llm_provider, BaseLLMProvider, MockLLMProvider
from ai.prompt_builder import load_master_prompt, build_troubleshooting_prompt
from ai.response_validator import validate_ai_response, AIDiagnosisSchema


class AIDiagnosisEngine:
    """Orchestrates building prompts, calling LLM provider, and validating response."""

    def __init__(self, provider: BaseLLMProvider = None):
        self.provider = provider or get_llm_provider()
        self.system_prompt = load_master_prompt()

    def run_diagnosis(
        self,
        symptom: str,
        topology_note: str,
        show_output: str,
        rule_results: List[Dict[str, Any]],
        concept: str = None
    ) -> AIDiagnosisSchema:
        """Executes full AI diagnosis workflow with schema validation and fallback handling."""

        prompt = build_troubleshooting_prompt(
            symptom=symptom,
            topology_note=topology_note,
            show_output=show_output,
            rule_results=rule_results,
            concept=concept
        )

        try:
            raw_response = self.provider.generate_diagnosis(prompt, self.system_prompt)
            # Clean markdown codeblocks if present
            cleaned_str = raw_response.strip()
            if cleaned_str.startswith("```json"):
                cleaned_str = cleaned_str[7:]
            if cleaned_str.startswith("```"):
                cleaned_str = cleaned_str[3:]
            if cleaned_str.endswith("```"):
                cleaned_str = cleaned_str[:-3]
            cleaned_str = cleaned_str.strip()

            validated_diagnosis = validate_ai_response(cleaned_str)
            return validated_diagnosis
        except Exception as e:
            # On API failure or validation failure, log and fallback to MockLLMProvider
            fallback_provider = MockLLMProvider()
            raw_fallback = fallback_provider.generate_diagnosis(prompt, self.system_prompt)
            return validate_ai_response(raw_fallback)
