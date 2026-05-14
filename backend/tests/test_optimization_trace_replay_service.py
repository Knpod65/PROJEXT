"""Tests for optimization_trace_replay_service.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from events.event_envelope import event_envelope_to_dict
from services.optimization_trace_context import OptimizationTraceContext
from services.optimization_trace_replay_service import (
    build_decision_lineage,
    build_trace_timeline,
    find_rejected_alternatives,
    group_trace_events_by_entity,
    summarize_decision_lineage,
)


def _trace_event(
    *,
    trace_event_id,
    event_type,
    timestamp,
    entity_id=1,
    entity_type="section",
    candidate_type="ROOM",
    candidate_id="R-1",
    source="SOLVER_TRACE",
    severity="INFO",
    constraint_code=None,
    reason_code=None,
    score_delta=None,
    metadata=None,
):
    return {
        "trace_event_id": trace_event_id,
        "trace_id": "trace-1",
        "session_id": "session-1",
        "event_type": event_type,
        "stage": "SELECTION",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "candidate_type": candidate_type,
        "candidate_id": candidate_id,
        "constraint_code": constraint_code,
        "reason_code": reason_code,
        "severity": severity,
        "score_delta": score_delta,
        "source": source,
        "message": None,
        "metadata": metadata or {},
        "timestamp": timestamp,
    }


def test_build_trace_timeline_sorts_by_timestamp():
    events = [
        _trace_event(trace_event_id="2", event_type="CANDIDATE_ACCEPTED", timestamp="2026-05-14T10:00:00+00:00"),
        _trace_event(trace_event_id="1", event_type="CANDIDATE_GENERATED", timestamp="2026-05-14T09:00:00+00:00"),
    ]

    timeline = build_trace_timeline(events)

    assert [event["trace_event_id"] for event in timeline] == ["1", "2"]


def test_build_trace_timeline_accepts_event_envelope_dicts():
    context = OptimizationTraceContext(trace_id="trace-1", session_id="session-1")
    context.add_candidate_generated(entity_type="section", entity_id=1, candidate_type="ROOM", candidate_id="R-1")
    envelope = event_envelope_to_dict(context.to_event_envelopes()[0])

    timeline = build_trace_timeline([envelope])

    assert timeline[0]["event_type"] == "CANDIDATE_GENERATED"
    assert timeline[0]["source"] == "SOLVER_TRACE"


def test_group_trace_events_by_entity_groups_distinct_entities():
    events = [
        _trace_event(trace_event_id="1", event_type="CANDIDATE_GENERATED", timestamp="2026-05-14T09:00:00+00:00", entity_id=1),
        _trace_event(trace_event_id="2", event_type="CANDIDATE_GENERATED", timestamp="2026-05-14T09:05:00+00:00", entity_id=2),
    ]

    grouped = group_trace_events_by_entity(events)

    assert set(grouped.keys()) == {"section:1", "section:2"}


def test_find_rejected_alternatives_can_filter_by_entity():
    events = [
        _trace_event(trace_event_id="1", event_type="CANDIDATE_REJECTED", timestamp="2026-05-14T09:00:00+00:00", entity_id=1, candidate_id="R-1"),
        _trace_event(trace_event_id="2", event_type="CANDIDATE_REJECTED", timestamp="2026-05-14T09:05:00+00:00", entity_id=2, candidate_id="R-2"),
    ]

    rejected = find_rejected_alternatives(events, entity_id=1)

    assert len(rejected) == 1
    assert rejected[0]["candidate_id"] == "R-1"


def test_summarize_decision_lineage_counts_event_categories():
    events = [
        _trace_event(trace_event_id="1", event_type="CANDIDATE_GENERATED", timestamp="2026-05-14T09:00:00+00:00"),
        _trace_event(trace_event_id="2", event_type="CANDIDATE_REJECTED", timestamp="2026-05-14T09:05:00+00:00", severity="WARNING"),
        _trace_event(trace_event_id="3", event_type="CANDIDATE_ACCEPTED", timestamp="2026-05-14T09:10:00+00:00"),
        _trace_event(trace_event_id="4", event_type="CONSTRAINT_TRIGGERED", timestamp="2026-05-14T09:15:00+00:00", constraint_code="ROOM_CAPACITY"),
        _trace_event(trace_event_id="5", event_type="PENALTY_APPLIED", timestamp="2026-05-14T09:20:00+00:00"),
        _trace_event(trace_event_id="6", event_type="FINAL_SELECTION_ACCEPTED", timestamp="2026-05-14T09:25:00+00:00", severity="HARD_FAIL", source="POST_HOC_TRACE"),
    ]

    summary = summarize_decision_lineage(events)

    assert summary["candidate_generated_count"] == 1
    assert summary["candidate_rejected_count"] == 1
    assert summary["candidate_accepted_count"] == 1
    assert summary["constraint_triggered_count"] == 1
    assert summary["penalty_count"] == 1
    assert summary["selection_count"] == 2
    assert summary["highest_severity"] == "HARD_FAIL"
    assert summary["trace_source_breakdown"]["SOLVER_TRACE"] == 5
    assert summary["trace_source_breakdown"]["POST_HOC_TRACE"] == 1


def test_build_decision_lineage_returns_entity_lineage_and_summary():
    events = [
        _trace_event(trace_event_id="1", event_type="CANDIDATE_GENERATED", timestamp="2026-05-14T09:00:00+00:00", entity_id=1),
        _trace_event(trace_event_id="2", event_type="CANDIDATE_REJECTED", timestamp="2026-05-14T09:05:00+00:00", entity_id=1, candidate_id="R-2"),
        _trace_event(trace_event_id="3", event_type="FINAL_SELECTION_ACCEPTED", timestamp="2026-05-14T09:10:00+00:00", entity_id=1, candidate_id="schedule-1"),
    ]

    payload = build_decision_lineage(events)

    assert "lineage" in payload
    assert "summary" in payload
    assert len(payload["lineage"]) == 1
    assert payload["lineage"][0]["entity_key"] == "section:1"
    assert payload["lineage"][0]["final_selection"]["candidate_id"] == "schedule-1"
    assert payload["lineage"][0]["rejected_alternatives"][0]["candidate_id"] == "R-2"


def test_replay_service_sanitizes_sensitive_metadata_keys():
    events = [
        _trace_event(
            trace_event_id="1",
            event_type="CANDIDATE_REJECTED",
            timestamp="2026-05-14T09:00:00+00:00",
            metadata={"student_id": "630110001", "safe_total": 2},
        ),
    ]

    timeline = build_trace_timeline(events)

    assert "student_id" not in timeline[0]["metadata"]
    assert timeline[0]["metadata"]["safe_total"] == 2
