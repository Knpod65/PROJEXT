"""Tests for integration_contract_registry_service.py"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.integration_contract_registry_service import (
    list_contracts,
    get_contract,
    list_inbound_contracts,
    list_outbound_contracts,
    get_contract_pdpa_level,
    validate_contract_fields,
)
from contracts.integration_contracts import IntegrationContract


def test_list_contracts_returns_all_five():
    contracts = list_contracts()
    assert isinstance(contracts, list)
    assert len(contracts) == 5
    codes = {c["system_code"] for c in contracts}
    assert codes == {"sis", "hr", "lms", "finance", "cmu_sso"}


def test_get_contract_returns_correct():
    sis = get_contract("sis")
    assert sis is not None
    assert sis["system_name"] == "Student Information System"
    assert sis["integration_direction"] == "inbound"
    assert sis["sync_mode"] == "batch_daily"

    hr = get_contract("hr")
    assert hr is not None
    assert hr["system_name"] == "Human Resources / Personnel System"
    assert hr["sync_mode"] == "batch_hourly"

    lms = get_contract("lms")
    assert lms is not None
    assert lms["integration_direction"] == "bidirectional"
    assert lms["data_domain"] == "teaching_schedule"

    finance = get_contract("finance")
    assert finance is not None
    assert finance["integration_direction"] == "outbound"
    assert finance["data_domain"] == "payment"

    cmu = get_contract("cmu_sso")
    assert cmu is not None
    assert cmu["integration_direction"] == "inbound"
    assert cmu["data_domain"] == "auth"
    assert cmu["sync_mode"] == "realtime"
    assert cmu["failure_policy"] == "skip"


def test_get_contract_missing_returns_none():
    assert get_contract("nonexistent") is None
    assert get_contract("") is None
    assert get_contract("SIS") is None  # case-sensitive


def test_list_inbound_contracts():
    inbound = list_inbound_contracts()
    codes = {c["system_code"] for c in inbound}
    assert codes == {"sis", "hr", "lms", "cmu_sso"}
    # Each must have integration_direction inbound or bidirectional
    assert all(c["integration_direction"] in ("inbound", "bidirectional") for c in inbound)


def test_list_outbound_contracts():
    outbound = list_outbound_contracts()
    codes = {c["system_code"] for c in outbound}
    assert codes == {"finance", "lms"}
    # Each must have integration_direction outbound or bidirectional
    assert all(c["integration_direction"] in ("outbound", "bidirectional") for c in outbound)


def test_get_contract_pdpa_level():
    assert get_contract_pdpa_level("sis") == "confidential"
    assert get_contract_pdpa_level("hr") == "confidential"
    assert get_contract_pdpa_level("lms") == "internal"
    assert get_contract_pdpa_level("finance") == "internal"
    assert get_contract_pdpa_level("cmu_sso") == "public"
    assert get_contract_pdpa_level("unknown") is None


def test_validate_contract_fields_sis():
    sis_contract = get_contract("sis")
    required = set(sis_contract["required_fields"])  # student_id, full_name, department
    # Valid payload
    payload = {
        "student_id": "12345678",
        "full_name": "John Doe",
        "department": "Science",
        "extra_field": "allowed"
    }
    assert validate_contract_fields("sis", payload) is True
    # Missing required field
    payload_missing = {
        "student_id": "12345678",
        "full_name": "John Doe",
        # missing department
    }
    assert validate_contract_fields("sis", payload_missing) is False
    # Empty payload
    assert validate_contract_fields("sis", {}) is False


def test_validate_contract_fields_lms_bidirectional():
    lms_contract = get_contract("lms")
    required = set(lms_contract["required_fields"])
    # Valid payload
    payload = {
        "course_id": "CS101",
        "section_id": "01",
        "meeting_time": "10:00",
        "room_id": "R201",
    }
    assert validate_contract_fields("lms", payload) is True
    # Missing required
    payload_missing = {
        "course_id": "CS101",
        "section_id": "01",
        "meeting_time": "10:00",
        # missing room_id
    }
    assert validate_contract_fields("lms", payload_missing) is False


def test_validate_contract_fields_finance_outbound():
    finance_contract = get_contract("finance")
    required = set(finance_contract["required_fields"])
    payload = {
        "workload_units": 10.0,
        "rate": 1500.0,
        "total_cost": 15000.0,
    }
    assert validate_contract_fields("finance", payload) is True
    payload_missing = {
        "workload_units": 10.0,
        "rate": 1500.0,
        # missing total_cost
    }
    assert validate_contract_fields("finance", payload_missing) is False


def test_validate_contract_fields_unknown_system_returns_false():
    assert validate_contract_fields("nonexistent", {"foo": 1}) is False
    assert validate_contract_fields("", {"required": "field"}) is False
