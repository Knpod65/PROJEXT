"""Tests for optimization_trace_context.py."""
import os
import sys
from datetime import datetime, timezone
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_EVENT_CANDIDATE_ACCEPTED,
    TRACE_EVENT_CANDIDATE_GENERATED,
    TRACE_EVENT_CANDIDATE_REJECTED,
    TRACE_EVENT_CONSTRAINT_TRIGGERED,
    TRACE_EVENT_FINAL_SELECTION,
    TRACE_EVENT_PENALTY_APPLIED,
    TRACE_EVENT_TRADEOFF_CHOSEN,
    TRACE_SOURCE_FALLBACK,
    TRACE_SOURCE_INPUT,
)


class _ExampleSource(str, Enum):
    FALLBACK = TRACE_SOURCE_FALLBACK


def test_context_initializes_with_trace_and_session_ids():
    context = OptimizationTraceContext(session_id="session-1", trace_id="trace-1")

    assert context.trace_id == "trace-1"
    assert context.session_id == "session-1"
    assert context.events == []


def test_add_event_captures_required_fields():
    context = OptimizationTraceContext(session_id="session-7", trace_id="trace-7")

    event = context.add_event(
        event_type="CUSTOM_EVENT",
        stage="SELECTION",
        entity_type="section",
        entity_id=42,
        candidate_type="ROOM",
        candidate_id="R-101",
        constraint_code="ROOM_CAPACITY",
        reason_code="BEST_FIT",
        severity="INFO",
        score_delta=5,
        message="Room selected.",
        metadata={"capacity": 50},
    )

    assert event["trace_id"] == "trace-7"
    assert event["session_id"] == "session-7"
    assert event["trace_event_id"]
    assert event["entity_id"] == 42
    assert event["candidate_id"] == "R-101"
    assert event["score_delta"] == 5.0
    assert event["metadata"]["capacity"] == 50
    assert len(context.events) == 1


def test_add_event_rejects_unknown_source():
    context = OptimizationTraceContext()

    try:
        context.add_event(event_type="X", stage="Y", source="UNKNOWN_SOURCE")
        assert False, "Expected ValueError for unsupported source"
    except ValueError as exc:
        assert "Unsupported trace source" in str(exc)


def test_metadata_is_masked_for_trace_sensitive_keys():
    context = OptimizationTraceContext()

    event = context.add_candidate_generated(
        entity_type="section",
        entity_id=1,
        candidate_type="ROOM",
        candidate_id="R-1",
        metadata={
            "student_id": "630110001",
            "student_name": "Alice Student",
            "candidate_name": "Alice Student",
            "qr_payload": "SECRET-QR",
            "email": "alice@example.com",
            "safe_count": 8,
        },
    )

    metadata = event["metadata"]
    assert metadata["student_id"] == "[REDACTED]"
    assert metadata["student_name"] == "[REDACTED]"
    assert metadata["candidate_name"] == "[REDACTED]"
    assert metadata["qr_payload"] == "[REDACTED]"
    assert metadata["email"] == "[REDACTED]"
    assert metadata["safe_count"] == 8


def test_metadata_is_json_safe_and_deterministic_for_common_types():
    context = OptimizationTraceContext()
    ts = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)

    event = context.add_candidate_generated(
        entity_type="section",
        entity_id={"section": 1},
        candidate_type="ROOM",
        candidate_id=("R-1", "A"),
        metadata={
            "seen_slots": {"09:00-12:00", "13:00-16:00"},
            "timestamp": ts,
            "source_enum": _ExampleSource.FALLBACK,
        },
    )

    assert isinstance(event["entity_id"], dict)
    assert isinstance(event["candidate_id"], list)
    assert isinstance(event["metadata"]["seen_slots"], list)
    assert event["metadata"]["timestamp"] == ts.isoformat()
    assert event["metadata"]["source_enum"] == TRACE_SOURCE_FALLBACK


def test_convenience_methods_emit_expected_event_types():
    context = OptimizationTraceContext()

    event_types = [
        context.add_candidate_generated(entity_type="section", entity_id=1)["event_type"],
        context.add_candidate_rejected(entity_type="section", entity_id=1)["event_type"],
        context.add_candidate_accepted(entity_type="section", entity_id=1)["event_type"],
        context.add_constraint_triggered(entity_type="section", entity_id=1)["event_type"],
        context.add_penalty_applied(entity_type="section", entity_id=1)["event_type"],
        context.add_tradeoff_chosen(entity_type="section", entity_id=1)["event_type"],
        context.add_final_selection(entity_type="section", entity_id=1)["event_type"],
    ]

    assert event_types == [
        TRACE_EVENT_CANDIDATE_GENERATED,
        TRACE_EVENT_CANDIDATE_REJECTED,
        TRACE_EVENT_CANDIDATE_ACCEPTED,
        TRACE_EVENT_CONSTRAINT_TRIGGERED,
        TRACE_EVENT_PENALTY_APPLIED,
        TRACE_EVENT_TRADEOFF_CHOSEN,
        TRACE_EVENT_FINAL_SELECTION,
    ]


def test_constraint_triggered_defaults_to_input_constraint_source():
    context = OptimizationTraceContext()

    event = context.add_constraint_triggered(entity_type="section", entity_id=1)

    assert event["source"] == TRACE_SOURCE_INPUT


def test_to_dict_contains_event_count_and_events():
    context = OptimizationTraceContext(session_id="sess-2", trace_id="trace-2")
    context.add_candidate_generated(entity_type="section", entity_id=2)

    payload = context.to_dict()

    assert payload["trace_id"] == "trace-2"
    assert payload["session_id"] == "sess-2"
    assert payload["event_count"] == 1
    assert len(payload["events"]) == 1


def test_to_event_envelopes_builds_optimization_event_envelopes():
    context = OptimizationTraceContext(session_id="sess-3", trace_id="trace-3")
    context.add_final_selection(
        entity_type="section",
        entity_id=3,
        candidate_type="ROOM",
        candidate_id="R-301",
        metadata={"safe_total": 12},
    )

    envelopes = context.to_event_envelopes()

    assert len(envelopes) == 1
    envelope = envelopes[0]
    assert envelope.domain == "optimization"
    assert envelope.event_type == TRACE_EVENT_FINAL_SELECTION
    assert envelope.session_id == "sess-3"
    assert envelope.correlation_id == "trace-3"
    assert envelope.payload["candidate_id"] == "R-301"
    assert envelope.metadata["trace_id"] == "trace-3"
    assert envelope.contains_pii is False


def test_event_timestamps_are_valid_iso_strings():
    context = OptimizationTraceContext()
    event = context.add_tradeoff_chosen(entity_type="section", entity_id=5)

    parsed = datetime.fromisoformat(event["timestamp"])
    assert parsed.tzinfo is not None
