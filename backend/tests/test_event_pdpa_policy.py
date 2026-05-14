"""Tests for policies/event_pdpa_policy.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policies.event_pdpa_policy import (
    assert_event_payload_safe,
    classify_event_payload,
    mask_event_payload,
)


# ── classify_event_payload ────────────────────────────────────────────────────

def test_clean_payload_no_pii():
    result = classify_event_payload({"section_id": 42, "course": "POL101"})
    assert result["contains_pii"] is False
    assert result["pii_keys"] == []
    assert result["masking_required"] is False
    assert result["recommended_classification"] == "public"


def test_email_detected_as_pii():
    result = classify_event_payload({"email": "alice@test.com", "score": 95})
    assert result["contains_pii"] is True
    assert "email" in result["pii_keys"]
    assert result["masking_required"] is True


def test_nested_dict_pii_detected():
    payload = {"user": {"email": "alice@test.com"}, "section_id": 42}
    result = classify_event_payload(payload)
    assert result["contains_pii"] is True
    assert "email" in result["pii_keys"]


def test_list_of_dicts_pii_detected():
    payload = {"signers": [{"phone": "0891234567"}, {"role": "admin"}]}
    result = classify_event_payload(payload)
    assert result["contains_pii"] is True
    assert "phone" in result["pii_keys"]


def test_pii_keys_sorted():
    payload = {"phone": "1", "email": "2", "name": "3"}
    result = classify_event_payload(payload)
    assert result["pii_keys"] == sorted(result["pii_keys"])


def test_classify_does_not_mutate_input():
    payload = {"email": "test@test.com"}
    original = dict(payload)
    classify_event_payload(payload)
    assert payload == original


# ── recommended_classification ────────────────────────────────────────────────

def test_citizen_id_gives_restricted():
    result = classify_event_payload({"citizen_id": "1234567890123"})
    assert result["recommended_classification"] == "restricted"


def test_student_id_gives_restricted():
    result = classify_event_payload({"student_id": "630110001"})
    assert result["recommended_classification"] == "restricted"


def test_email_gives_confidential():
    result = classify_event_payload({"email": "test@test.com"})
    assert result["recommended_classification"] == "confidential"


def test_token_gives_internal():
    result = classify_event_payload({"token": "abc123"})
    assert result["recommended_classification"] == "internal"


def test_clean_payload_gives_public():
    result = classify_event_payload({"score": 90, "course_id": "POL101"})
    assert result["recommended_classification"] == "public"


# ── assert_event_payload_safe ─────────────────────────────────────────────────

def test_assert_safe_no_op_on_clean_payload_strict():
    assert_event_payload_safe({"score": 90}, strict=True)  # must not raise


def test_assert_safe_raises_on_pii_strict():
    with pytest.raises(ValueError, match="PII keys"):
        assert_event_payload_safe({"email": "test@test.com"}, strict=True)


def test_assert_safe_no_op_on_pii_non_strict():
    assert_event_payload_safe({"email": "test@test.com"}, strict=False)  # must not raise


# ── mask_event_payload ────────────────────────────────────────────────────────

def test_mask_replaces_pii_values():
    payload = {"email": "alice@test.com", "section_id": 42}
    result = mask_event_payload(payload)
    assert result["email"] == "[REDACTED]"
    assert result["section_id"] == 42


def test_mask_does_not_mutate_input():
    payload = {"email": "test@test.com", "score": 95}
    original = dict(payload)
    mask_event_payload(payload)
    assert payload == original


def test_mask_preserves_non_pii_keys():
    payload = {"course_id": "POL101", "score": 88}
    result = mask_event_payload(payload)
    assert result == payload


def test_mask_nested_dict():
    payload = {"user": {"email": "alice@test.com", "role": "admin"}}
    result = mask_event_payload(payload)
    assert result["user"]["email"] == "[REDACTED]"
    assert result["user"]["role"] == "admin"


def test_mask_list_of_dicts():
    payload = {"signers": [{"phone": "089"}, {"role": "admin"}]}
    result = mask_event_payload(payload)
    assert result["signers"][0]["phone"] == "[REDACTED]"
    assert result["signers"][1]["role"] == "admin"


def test_mask_custom_mask_value():
    payload = {"email": "test@test.com"}
    result = mask_event_payload(payload, mask_value="***")
    assert result["email"] == "***"
