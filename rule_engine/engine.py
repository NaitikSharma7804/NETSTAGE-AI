"""
NetSage AI Deterministic Rule Engine Orchestrator.
Executes pure Python network validation rules across all categories.
"""

from typing import List, Optional
from rule_engine.models import RuleCheckResult, RuleEngineRun, RuleStatus
from rule_engine.ip_rules import check_duplicate_ip, check_invalid_host_ip
from rule_engine.subnet_rules import check_subnet_mask_mismatch
from rule_engine.gateway_rules import check_gateway_in_subnet, check_hsrp_fhrp_vip
from rule_engine.vlan_rules import (
    check_missing_vlan,
    check_subinterface_encapsulation,
    check_native_vlan_mismatch,
)
from rule_engine.interface_rules import (
    check_interface_administratively_down,
    check_duplex_mismatch,
    check_err_disabled_port,
)
from rule_engine.routing_rules import (
    check_missing_default_route,
    check_ospf_area_mismatch,
    check_ospf_mtu_mismatch,
    check_unreachable_next_hop,
)
from rule_engine.acl_rules import (
    check_acl_inverted_wildcard_mask,
    check_acl_implicit_or_explicit_deny,
    check_acl_missing_established,
)
from rule_engine.dhcp_rules import check_missing_dhcp_helper, check_dhcp_pool_exhaustion
from rule_engine.nat_rules import check_missing_nat_outside, check_missing_nat_overload


class RuleEngine:
    """Master Deterministic Network Rule Engine."""

    def __init__(self):
        self.rule_functions = [
            # IP Rules
            check_duplicate_ip,
            check_invalid_host_ip,
            # Subnet Rules
            check_subnet_mask_mismatch,
            # Gateway Rules
            check_gateway_in_subnet,
            check_hsrp_fhrp_vip,
            # VLAN Rules
            check_missing_vlan,
            check_subinterface_encapsulation,
            check_native_vlan_mismatch,
            # Interface Rules
            check_interface_administratively_down,
            check_duplex_mismatch,
            check_err_disabled_port,
            # Routing Rules
            check_missing_default_route,
            check_ospf_area_mismatch,
            check_ospf_mtu_mismatch,
            check_unreachable_next_hop,
            # ACL Rules
            check_acl_inverted_wildcard_mask,
            check_acl_implicit_or_explicit_deny,
            check_acl_missing_established,
            # DHCP Rules
            check_missing_dhcp_helper,
            check_dhcp_pool_exhaustion,
            # NAT Rules
            check_missing_nat_outside,
            check_missing_nat_overload,
        ]

    def evaluate(self, show_outputs: str, topology_note: str = "", symptom: str = "") -> RuleEngineRun:
        """Runs all registered deterministic rules against network outputs."""
        combined_outputs = f"{show_outputs}\n{symptom}"
        results: List[RuleCheckResult] = []

        for rule_fn in self.rule_functions:
            try:
                res = rule_fn(combined_outputs, topology_note)
                results.append(res)
            except Exception as e:
                # Fail gracefully for individual rule execution errors
                results.append(
                    RuleCheckResult(
                        rule_id=f"ERR_{rule_fn.__name__}",
                        rule_name=rule_fn.__name__,
                        category="Engine",
                        status=RuleStatus.NOT_APPLICABLE,
                        message=f"Rule execution error: {str(e)}",
                        evidence="",
                        recommendation=""
                    )
                )

        passed = sum(1 for r in results if r.status == RuleStatus.PASS)
        failed = sum(1 for r in results if r.status == RuleStatus.FAIL)
        warning = sum(1 for r in results if r.status == RuleStatus.WARNING)

        return RuleEngineRun(
            total_rules_evaluated=len(results),
            passed_count=passed,
            failed_count=failed,
            warning_count=warning,
            results=results
        )


# Global singleton instance
rule_engine = RuleEngine()