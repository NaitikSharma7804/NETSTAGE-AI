"""
AI Service and LLM Provider Factory.
"""

import os
from typing import Optional
from ai.providers.base import LLMProvider
from ai.providers.mock import MockLLMProvider
from ai.providers.cloud import CloudLLMProvider
from ai.providers.local import LocalLLMProvider


class AIService:
    """Factory and manager for AI diagnostic providers."""

    @staticmethod
    def get_provider() -> LLMProvider:
        demo_mode = os.getenv("DEMO_MODE", "true").lower() in ["true", "1", "yes"]
        provider_type = os.getenv("LLM_PROVIDER", "mock").lower()
        model_name = os.getenv("LLM_MODEL", "mock-netsage-v1")
        api_key = os.getenv("LLM_API_KEY", "")

        if demo_mode or provider_type == "mock":
            return MockLLMProvider(model_name=model_name)
        elif provider_type in ["cloud", "openai", "gemini", "anthropic"]:
            return CloudLLMProvider(model_name=model_name, api_key=api_key)
        elif provider_type in ["local", "ollama", "vllm"]:
            return LocalLLMProvider(model_name=model_name)
        else:
            return MockLLMProvider(model_name=model_name)