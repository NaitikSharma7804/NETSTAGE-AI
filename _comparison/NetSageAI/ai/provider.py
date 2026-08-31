"""LLM Provider abstraction layer supporting OpenAI and deterministic Mock provider."""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ai.response_validator import AIDiagnosisSchema


class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM providers."""

    provider_name: str = "base"
    mode: str = "unknown"

    @abstractmethod
    def generate_diagnosis(self, prompt: str, system_prompt: str) -> str:
        """Generates raw JSON diagnosis response from LLM."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider implementation."""

    provider_name: str = "openai"
    mode: str = "live"

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    def generate_diagnosis(self, prompt: str, system_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        import openai
        client = openai.OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return response.choices[0].message.content


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM Provider for offline/testing/fallback environments."""

    provider_name: str = "mock"
    mode: str = "offline"

    def generate_diagnosis(self, prompt: str, system_prompt: str) -> str:
        """Generates evidence-backed diagnosis using rule findings embedded in prompt."""
        
        prompt_lower = prompt.lower()
        
        # Default fallback values
        root_cause = "Network configuration anomaly detected requiring manual CLI investigation."
        confidence = 0.85
        osi_layer = "Layer 3"
        evidence = ["Rule engine flagged matching network state anomaly."]
        next_command = "show ip interface brief"
        fix_steps = ["Verify interface state and IP subnet configurations."]

        if "vlan" in prompt_lower:
            root_cause = "Switchport VLAN assignment mismatch or missing VLAN configuration."
            confidence = 0.90
            osi_layer = "Layer 2"
            evidence = ["Switch interface configured with incorrect VLAN ID or missing from database."]
            next_command = "show vlan brief"
            fix_steps = ["switchport access vlan <correct_vlan>", "vlan <id>"]
        elif "dhcp" in prompt_lower:
            root_cause = "DHCP service misconfiguration (missing default-router or ip helper-address)."
            confidence = 0.92
            osi_layer = "Layer 7"
            evidence = ["DHCP pool parameters missing gateway router option or relay agent."]
            next_command = "show ip dhcp binding"
            fix_steps = ["ip dhcp pool <pool_name>", "default-router <gateway_ip>"]
        elif "dns" in prompt_lower:
            root_cause = "Client configured with invalid or unreachable DNS server IP."
            confidence = 0.88
            osi_layer = "Layer 7"
            evidence = ["DNS resolution failure due to incorrect host DNS settings or route."]
            next_command = "show ip route"
            fix_steps = ["ipconfig /all", "Set DNS server to active reachable server IP"]
        elif "gateway" in prompt_lower or "administratively down" in prompt_lower:
            root_cause = "Gateway interface administratively down or IP mismatch."
            confidence = 0.95
            osi_layer = "Layer 1"
            evidence = ["Interface line protocol is administratively down."]
            next_command = "show interface GigabitEthernet0/0"
            fix_steps = ["interface GigabitEthernet0/0", "no shutdown"]
        elif "route" in prompt_lower or "routing" in prompt_lower:
            root_cause = "Missing static route or routing protocol neighbor timer mismatch."
            confidence = 0.91
            osi_layer = "Layer 3"
            evidence = ["Routing table lacks entry for target destination prefix."]
            next_command = "show ip route"
            fix_steps = ["ip route <destination_prefix> <mask> <next_hop_ip>"]
        elif "acl" in prompt_lower or "access-list" in prompt_lower:
            root_cause = "Access Control List (ACL) rule explicitly denying target traffic."
            confidence = 0.89
            osi_layer = "Layer 4"
            evidence = ["Access-list rule deny line matched target packet parameters."]
            next_command = "show access-lists"
            fix_steps = ["Modify ACL rule to permit target subnet and protocol"]
        elif "nat" in prompt_lower:
            root_cause = "Missing 'ip nat inside' statement or NAT ACL subnet mismatch."
            confidence = 0.93
            osi_layer = "Layer 3"
            evidence = ["NAT translation table empty; interface missing NAT role designation."]
            next_command = "show ip nat statistics"
            fix_steps = ["interface GigabitEthernet0/0", "ip nat inside"]
        elif "wireless" in prompt_lower or "ssid" in prompt_lower:
            root_cause = "Wireless SSID or WPA2 pre-shared key mismatch."
            confidence = 0.87
            osi_layer = "Layer 2"
            evidence = ["Wireless AP configuration SSID does not match client connection request."]
            next_command = "show wireless status"
            fix_steps = ["Align SSID and WPA2 security key on client device"]

        response_dict = {
            "root_cause": root_cause,
            "confidence": confidence,
            "osi_layer": osi_layer,
            "evidence": evidence,
            "next_command": next_command,
            "fix_steps": fix_steps
        }
        return json.dumps(response_dict)


def get_llm_provider(provider_type: str = None) -> BaseLLMProvider:
    """Factory function returning the configured LLM provider."""
    provider_name = provider_type or os.getenv("LLM_PROVIDER", "openai").lower()
    api_key = os.getenv("OPENAI_API_KEY")

    if provider_name == "openai" and api_key and api_key.strip():
        try:
            return OpenAIProvider(api_key=api_key)
        except Exception:
            return MockLLMProvider()
    
    return MockLLMProvider()
