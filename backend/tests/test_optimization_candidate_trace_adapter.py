"""Tests for optimization_candidate_trace_adapter.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_candidate_trace_adapter import (
    CANDIDATE_TYPE_ROOM,
    CANDIDATE_TYPE_SPLIT,
    CANDIDATE_TYPE_STAFF,
    CANDIDATE_TYPE_TIMESLOT,
    REASON_CODE_CAPACITY_TOO_LOW,
    REASON_CODE_FALLBACK_USED,
    REASON_CODE_SPLIT_REQUIRED,
    REASON_CODE_STAFF_OVERLOAD,
    trace_accepted_candidate,
    trace_rejected_candidate,
    trace_room_candidate,
    trace_split_candidate,
    trace_staff_candidate,
    trace_timeslot_candidate,
)
from services.optimization_trace_context import OptimizationTraceContext


def test_trace_room_candidate_adds_generated_room_event():
    context = OptimizationTraceContext(trace_id="trace-1", session_id="session-1")

    event = trace_room_candidate(
        context,
        entity_type="section",
        entity_id=10,
        candidate_id="R-101",
        capacity=60,
        assigned_count=48,
        building="B1",
        floor="3",
        room_type="LECTURE",
        reason_code=REASON_CODE_CAPACITY_TOO_LOW,
    )

    assert event["event_type"] == "CANDIDATE_GENERATED"
    assert event["candidate_type"] == CANDIDATE_TYPE_ROOM
    assert event["candidate_id"] == "R-101"
    assert event["metadata"]["capacity"] == 60
    assert event["metadata"]["assigned_count"] == 48
    assert event["metadata"]["utilization_ratio"] == 0.8
    assert event["metadata"]["building"] == "B1"
    assert event["metadata"]["floor"] == "3"
    assert event["metadata"]["room_type"] == "LECTURE"


def test_trace_staff_candidate_adds_load_and_role_metadata():
    context = OptimizationTraceContext()

    event = trace_staff_candidate(
        context,
        entity_type="section",
        entity_id=11,
        candidate_id=2001,
        staff_current_load=3,
        staff_role="INVIGILATOR",
        time_slot="2026-05-14 09:00-12:00",
    )

    assert event["candidate_type"] == CANDIDATE_TYPE_STAFF
    assert event["metadata"]["staff_current_load"] == 3
    assert event["metadata"]["staff_role"] == "INVIGILATOR"
    assert event["metadata"]["time_slot"] == "2026-05-14 09:00-12:00"


def test_trace_timeslot_candidate_defaults_time_slot_from_candidate_id():
    context = OptimizationTraceContext()

    event = trace_timeslot_candidate(
        context,
        entity_type="section",
        entity_id=12,
        candidate_id="2026-05-14 13:00-16:00",
    )

    assert event["candidate_type"] == CANDIDATE_TYPE_TIMESLOT
    assert event["metadata"]["time_slot"] == "2026-05-14 13:00-16:00"


def test_trace_split_candidate_marks_split_candidate_type():
    context = OptimizationTraceContext()

    event = trace_split_candidate(
        context,
        entity_type="section",
        entity_id=13,
        candidate_id="split-2-rooms",
        reason_code=REASON_CODE_SPLIT_REQUIRED,
        assigned_count=2,
    )

    assert event["candidate_type"] == CANDIDATE_TYPE_SPLIT
    assert event["metadata"]["assigned_count"] == 2
    assert event["reason_code"] == REASON_CODE_SPLIT_REQUIRED


def test_trace_rejected_candidate_emits_rejected_event():
    context = OptimizationTraceContext()

    event = trace_rejected_candidate(
        context,
        entity_type="section",
        entity_id=14,
        candidate_type=CANDIDATE_TYPE_ROOM,
        candidate_id="R-404",
        reason_code=REASON_CODE_CAPACITY_TOO_LOW,
        constraint_code="ROOM_CAPACITY",
        capacity=30,
        assigned_count=45,
        message="Room does not fit the section.",
    )

    assert event["event_type"] == "CANDIDATE_REJECTED"
    assert event["constraint_code"] == "ROOM_CAPACITY"
    assert event["reason_code"] == REASON_CODE_CAPACITY_TOO_LOW
    assert event["severity"] == "WARNING"
    assert event["metadata"]["capacity"] == 30
    assert event["metadata"]["assigned_count"] == 45
    assert event["metadata"]["utilization_ratio"] == 1.5


def test_trace_accepted_candidate_emits_accepted_event():
    context = OptimizationTraceContext()

    event = trace_accepted_candidate(
        context,
        entity_type="section",
        entity_id=15,
        candidate_type=CANDIDATE_TYPE_STAFF,
        candidate_id=3001,
        reason_code=REASON_CODE_FALLBACK_USED,
        staff_current_load=2,
        staff_role="SUPERVISOR",
    )

    assert event["event_type"] == "CANDIDATE_ACCEPTED"
    assert event["candidate_type"] == CANDIDATE_TYPE_STAFF
    assert event["candidate_id"] == 3001
    assert event["reason_code"] == REASON_CODE_FALLBACK_USED
    assert event["metadata"]["staff_current_load"] == 2
    assert event["metadata"]["staff_role"] == "SUPERVISOR"


def test_trace_accepted_candidate_can_override_stage():
    context = OptimizationTraceContext()

    event = trace_accepted_candidate(
        context,
        entity_type="section",
        entity_id=16,
        candidate_type=CANDIDATE_TYPE_TIMESLOT,
        candidate_id="slot-1",
        stage="CANDIDATE_GENERATION",
    )

    assert event["stage"] == "CANDIDATE_GENERATION"


def test_adapter_uses_trace_context_sanitization():
    context = OptimizationTraceContext()

    event = trace_rejected_candidate(
        context,
        entity_type="section",
        entity_id=17,
        candidate_type=CANDIDATE_TYPE_STAFF,
        candidate_id=4001,
        reason_code=REASON_CODE_STAFF_OVERLOAD,
        metadata={
            "candidate_name": "Alice Student",
            "email": "alice@example.com",
            "safe_metric": 4,
        },
    )

    assert event["metadata"]["candidate_name"] == "[REDACTED]"
    assert event["metadata"]["email"] == "[REDACTED]"
    assert event["metadata"]["safe_metric"] == 4


def test_adapter_appends_events_to_context():
    context = OptimizationTraceContext()

    trace_room_candidate(context, entity_type="section", entity_id=18, candidate_id="R-18")
    trace_staff_candidate(context, entity_type="section", entity_id=18, candidate_id=1801)
    trace_rejected_candidate(
        context,
        entity_type="section",
        entity_id=18,
        candidate_type=CANDIDATE_TYPE_TIMESLOT,
        candidate_id="slot-18",
        reason_code="TIMESLOT_CONFLICT",
    )

    assert len(context.events) == 3
