"""
Unit Tests for Deterministic Network Rule Engine.
"""

import pytest
from rule_engine.engine import rule_engine
from rule_engine.models import RuleStatus
from rule_engine.ip_rules import check_duplicate_ip, check_invalid_host_ip
from rule_engine.subnet_rules import check_subnet_mask_mismatch
from rule_engine.gateway_rules import check_gateway_in_subnet
from rule_engine.vlan_rules import check_missing_vlan, check_subinterface_encapsulation, check_native_vlan_mismatch
from rule_engine.interface_rules import check_interface_administratively_down, check_duplex_mismatch
from rule_engine.routing_rules import check_missing_default_route, check_ospf_area_mismatch, check_ospf_mtu_mismatch
from rule_engine.acl_rules import check_acl_inverted_wildcard_mask, check_acl_implicit_or_explicit_deny
from rule_engine.dhcp_rules import check_missing_dhcp_helper, check_dhcp_pool_exhaustion
from rule_engine.nat_rules import check_missing_nat_outside, check_missing_nat_overload


def test_duplicate_ip_detected():
    output = "%SYS-4-DUPLICATE_IP: 192.168.1.50 duplicate IP address received from 0010.1122.3344"
    res = check_duplicate_ip(output)
    assert res.status == RuleStatus.FAIL
    assert "192.168.1.50" in res.message


def test_duplicate_ip_pass():
    output = "SW1# show ip arp\n192.168.1.1 0001.9654.1201"
    res = check_duplicate_ip(output)
    assert res.status == RuleStatus.PASS


def test_invalid_host_ip_network_address():
    output = "IP Address : 10.0.5.0\nSubnet Mask : 255.255.255.0"
    res = check_invalid_host_ip(output)
    assert res.status == RuleStatus.FAIL
    assert "Network ID" in res.message


def test_gateway_outside_subnet():
    output = "IP Address : 10.1.10.45\nSubnet Mask : 255.255.255.0\nDefault Gateway : 10.1.20.1"
    res = check_gateway_in_subnet(output)
    assert res.status == RuleStatus.FAIL
    assert "10.1.20.1" in res.message


def test_gateway_inside_subnet_pass():
    output = "IP Address : 10.1.10.45\nSubnet Mask : 255.255.255.0\nDefault Gateway : 10.1.10.1"
    res = check_gateway_in_subnet(output)
    assert res.status == RuleStatus.PASS


def test_missing_vlan():
    output = "Fa0/5 PC-A-Link inactive 20 auto auto 10/100BaseTX"
    res = check_missing_vlan(output)
    assert res.status == RuleStatus.FAIL
    assert "VLAN 20" in res.message


def test_subinterface_encapsulation_mismatch():
    output = "interface GigabitEthernet0/0.30\n encapsulation dot1Q 300\n ip address 192.168.30.1 255.255.255.0"
    res = check_subinterface_encapsulation(output)
    assert res.status == RuleStatus.FAIL
    assert "300" in res.message


def test_native_vlan_mismatch():
    output = "%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with SW2 GigabitEthernet0/1 (99)."
    res = check_native_vlan_mismatch(output)
    assert res.status == RuleStatus.FAIL
    assert "Native VLAN mismatch" in res.message


def test_interface_administratively_down():
    output = "GigabitEthernet0/1 is administratively down, line protocol is down"
    res = check_interface_administratively_down(output)
    assert res.status == RuleStatus.FAIL
    assert "administratively shutdown" in res.message


def test_duplex_mismatch_late_collisions():
    output = "Half-duplex, 100Mb/s\n 1890 late collisions, 2410 deferred"
    res = check_duplex_mismatch(output)
    assert res.status == RuleStatus.FAIL
    assert "Duplex mismatch" in res.message


def test_missing_default_route():
    output = "show ip route\nGateway of last resort is not set\nC 10.5.10.0/24"
    res = check_missing_default_route(output, topology_note="internet WAN 8.8.8.8")
    assert res.status == RuleStatus.FAIL


def test_ospf_area_mismatch():
    output = "Internet Address 10.1.12.1/30, Area 0\nInternet Address 10.1.12.2/30, Area 1"
    res = check_ospf_area_mismatch(output)
    assert res.status == RuleStatus.FAIL


def test_ospf_mtu_mismatch():
    output = "3.3.3.3 1 EXSTART/DR\nMTU 1500 bytes\nMTU 1400 bytes"
    res = check_ospf_mtu_mismatch(output)
    assert res.status == RuleStatus.FAIL


def test_acl_inverted_wildcard_mask():
    output = "permit tcp 10.10.50.0 255.255.255.0 host 10.20.10.100 eq 443"
    res = check_acl_inverted_wildcard_mask(output)
    assert res.status == RuleStatus.FAIL


def test_dhcp_missing_helper():
    output = "IP Address: 169.254.18.23\ninterface GigabitEthernet0/0.10"
    res = check_missing_dhcp_helper(output, topology_note="DHCP Server relay")
    assert res.status == RuleStatus.FAIL


def test_dhcp_pool_exhaustion():
    output = "Utilization mark (high/low) : 100 / 0\nTotal addresses : 14 Leased addresses : 14"
    res = check_dhcp_pool_exhaustion(output)
    assert res.status == RuleStatus.FAIL


def test_missing_nat_outside():
    output = "Outside interfaces:\n none\nInside interfaces:\n GigabitEthernet0/0"
    res = check_missing_nat_outside(output)
    assert res.status == RuleStatus.FAIL


def test_missing_nat_overload():
    output = "ip nat inside source list 1 interface GigabitEthernet0/1"
    res = check_missing_nat_overload(output)
    assert res.status == RuleStatus.FAIL


def test_rule_engine_full_run():
    output = "interface GigabitEthernet0/1\n switchport access vlan 20\nFa0/5 inactive 20"
    run = rule_engine.evaluate(output)
    assert run.total_rules_evaluated >= 20
    assert run.failed_count >= 1