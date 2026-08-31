"""Unit tests for NetSage AI Deterministic Rule Engine."""

import pytest
from rules.checker import run_all_rules
from rules.interface_checks import check_interface_status
from rules.ip_checks import check_duplicate_ips
from rules.subnet_checks import check_subnet_masks
from rules.gateway_checks import check_gateway_configuration
from rules.vlan_checks import check_vlan_configuration
from rules.route_checks import check_routing_configuration


def test_interface_down_check():
    show_output = "GigabitEthernet0/0  192.168.1.1  YES manual administratively down down"
    results = check_interface_status(show_output, "Interface not working", "Router R1")
    assert len(results) > 0
    assert results[0]["rule"] == "interface_admin_down"
    assert results[0]["status"] == "FAIL"
    assert results[0]["severity"] == "HIGH"


def test_duplicate_ip_check():
    symptom = "Duplicate IP address conflict reported"
    show_output = "Internet  192.168.1.10   0   0001.c711.1111  ARPA  VLAN10\nInternet  192.168.1.10   0   0002.d822.2222  ARPA  VLAN10"
    results = check_duplicate_ips(show_output, symptom, "PC1 and Printer PR1")
    assert len(results) > 0
    assert results[0]["rule"] == "duplicate_ip_check"
    assert results[0]["status"] == "FAIL"


def test_subnet_mask_check():
    symptom = "PC1 and PC2 cannot ping due to subnet mask mismatch"
    topology = "PC1 192.168.1.50/24. PC2 192.168.1.200/25."
    show_output = "PC1 ipconfig: 255.255.255.0. PC2 ipconfig: 255.255.255.128"
    results = check_subnet_masks(show_output, symptom, topology)
    assert len(results) > 0
    assert results[0]["rule"] == "subnet_mask_check"
    assert results[0]["status"] == "FAIL"


def test_gateway_mismatch_check():
    symptom = "Host default gateway mismatch"
    show_output = "Host gateway set to 192.168.1.254. R1 subinterface is 192.168.1.1."
    results = check_gateway_configuration(show_output, symptom, "Topology notes")
    assert len(results) > 0
    assert results[0]["status"] == "FAIL"


def test_missing_vlan_check():
    symptom = "VLAN 30 traffic not reaching switch"
    show_output = "switchport trunk allowed vlan 10,20"
    results = check_vlan_configuration(show_output, symptom, "Host in vlan 30 connected")
    assert len(results) > 0
    assert results[0]["rule"] == "vlan_trunk_allowed_check"
    assert results[0]["status"] == "FAIL"


def test_missing_route_check():
    symptom = "Cannot reach HQ subnet 172.16.0.0/16"
    show_output = "Gateway of last resort is not set\nC 10.0.0.0/30 is directly connected"
    results = check_routing_configuration(show_output, symptom, "R2 missing static route")
    assert len(results) > 0
    assert results[0]["status"] == "FAIL"


def test_master_checker_pass():
    show_output = "GigabitEthernet0/0  192.168.1.1  YES manual up up"
    results = run_all_rules("Normal operation", "Standard setup", show_output)
    assert len(results) > 0
    assert results[0]["status"] == "PASS"
