"""
Abstract LLM Provider Base Class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ai.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse


class LLMProvider(ABC):
    """Abstract Interface for LLM Diagnostic Providers."""

    def __init__(self, model_name: str = "default", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    async def generate_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """Generates a structured Pydantic diagnosis given symptoms and show outputs."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the provider is configured and available."""
        pass