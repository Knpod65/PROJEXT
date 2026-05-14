"""Tests for optimization_trace_pdpa_policy.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policies.optimization_trace_pdpa_policy import (
    assert_trace_event_safe,
    classify_trace_batch,
    classify_trace_event,
    mask_trace_event,
)


def _event(metadata=None):
    return {
        "event_type": "CANDIDATE_GENERATED",
        "entity_type": "section",
        "entity_id": 1,
        "metadata": metadata or {},
    }


def test_classify_trace_event_detects_raw_sensitive_fields():
    classification = classify_trace_event(
        _event({"student_id": "630110001", "email": "alice@example.com"})
    )

    assert classification["contains_sensitive_data"] is True
    assert "student_id" in classification["sensitive_keys"]
    assert classification["recommended_classification"] == "restricted"
    assert classification["safe"] is False


def test_classify_trace_event_treats_redacted_fields_as_safe():
    classification = classify_trace_event(
        _event({"student_id": "[REDACTED]", "email": "[REDACTED]"})
    )

    assert classification["contains_sensitive_data"] is False
    assert "student_id" in classification["masked_keys"]
    assert classification["recommended_classification"] == "restricted"
    assert classification["safe"] is True


def test_mask_trace_event_redacts_nested_sensitive_fields():
    event = _event({
        "student_id": "630110001",
        "nested": {"qr_payload": "SECRET"},
        "safe_total": 2,
    })

    masked = mask_trace_event(event)

    assert masked["metadata"]["student_id"] == "[REDACTED]"
    assert masked["metadata"]["nested"]["qr_payload"] == "[REDACTED]"
    assert masked["metadata"]["safe_total"] == 2
    assert event["metadata"]["student_id"] == "630110001"


def test_assert_trace_event_safe_raises_on_raw_sensitive_data():
    try:
        assert_trace_event_safe(_event({"phone": "0812345678"}))
        assert False, "Expected ValueError for raw sensitive fields"
    except ValueError as exc:
        assert "phone" in str(exc)


def test_assert_trace_event_safe_allows_aggregate_counts_and_redacted_fields():
    event = _event({
        "student_id": "[REDACTED]",
        "assigned_count": 20,
        "utilization_ratio": 0.75,
    })

    assert_trace_event_safe(event)


def test_classify_trace_batch_summarizes_unsafe_and_masked_keys():
    batch = [
        _event({"student_id": "630110001"}),
        _event({"student_id": "[REDACTED]"}),
        _event({"safe_total": 3}),
    ]

    summary = classify_trace_batch(batch)

    assert summary["total_events"] == 3
    assert summary["unsafe_event_count"] == 1
    assert summary["safe_event_count"] == 2
    assert "student_id" in summary["sensitive_keys"]
    assert "student_id" in summary["masked_keys"]
    assert summary["recommended_classification"] == "restricted"
