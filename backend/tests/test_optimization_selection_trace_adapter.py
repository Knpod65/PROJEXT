"""Tests for optimization_selection_trace_adapter.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_selection_trace_adapter import (
    CANDIDATE_TYPE_DISTRIBUTOR,
    CANDIDATE_TYPE_SCHEDULE,
    trace_distribution_selection,
    trace_final_schedule_selection,
    trace_room_selection,
    trace_split_selection,
    trace_staff_selection,
)
from services.optimization_trace_context import OptimizationTraceContext


def _quality_impact():
    return {"overall_score_delta": 3.0, "fairness_delta": 1.5}


def test_trace_room_selection_records_selection_metadata():
    context = OptimizationTraceContext()

    event = trace_room_selection(
        context,
        entity_type="section",
        entity_id=1,
        candidate_id="R-101",
        selected_candidate={"room_id": "R-101", "capacity": 80},
        accepted_reason="BEST_FIT",
        tradeoffs_accepted=["BUILDING_SPREAD_PENALTY"],
        contributing_constraints=["ROOM_CAPACITY", "ROOM_AVAILABILITY"],
        quality_impact=_quality_impact(),
        governance_relevance="LOW",
        confidence_level="HIGH",
    )

    assert event["event_type"] == "CANDIDATE_ACCEPTED"
    assert event["candidate_type"] == "ROOM"
    assert event["reason_code"] == "BEST_FIT"
    assert event["metadata"]["selected_candidate"]["room_id"] == "R-101"
    assert event["metadata"]["tradeoffs_accepted"] == ["BUILDING_SPREAD_PENALTY"]
    assert event["metadata"]["contributing_constraints"] == ["ROOM_CAPACITY", "ROOM_AVAILABILITY"]
    assert event["metadata"]["quality_impact"]["overall_score_delta"] == 3.0
    assert event["metadata"]["governance_relevance"] == "LOW"
    assert event["metadata"]["confidence_level"] == "HIGH"


def test_trace_staff_selection_uses_staff_candidate_type():
    context = OptimizationTraceContext()

    event = trace_staff_selection(
        context,
        entity_type="section",
        entity_id=2,
        candidate_id=2001,
        selected_candidate={"staff_id": 2001},
        accepted_reason="LOWEST_CURRENT_LOAD",
    )

    assert event["candidate_type"] == "STAFF"
    assert event["candidate_id"] == 2001


def test_trace_distribution_selection_uses_distributor_type():
    context = OptimizationTraceContext()

    event = trace_distribution_selection(
        context,
        entity_type="section",
        entity_id=3,
        candidate_id=3001,
        selected_candidate={"user_id": 3001},
        accepted_reason="COVERAGE_AVAILABLE",
    )

    assert event["candidate_type"] == CANDIDATE_TYPE_DISTRIBUTOR


def test_trace_split_selection_uses_split_candidate_type():
    context = OptimizationTraceContext()

    event = trace_split_selection(
        context,
        entity_type="section",
        entity_id=4,
        candidate_id="split-2",
        selected_candidate={"split_count": 2},
        accepted_reason="SPLIT_REQUIRED",
    )

    assert event["candidate_type"] == "SPLIT"
    assert event["metadata"]["selected_candidate"]["split_count"] == 2


def test_trace_final_schedule_selection_uses_final_selection_event():
    context = OptimizationTraceContext()

    event = trace_final_schedule_selection(
        context,
        entity_type="section",
        entity_id=5,
        candidate_id="schedule-5",
        selected_candidate={
            "room_id": "R-5",
            "staff_ids": [501, 502],
            "time_slot": "2026-05-14 09:00-12:00",
        },
        accepted_reason="FINAL_OPTIMAL_COMBINATION",
        contributing_constraints=["ROOM_CAPACITY", "STAFFING_AVAILABILITY"],
        confidence_level="MEDIUM",
    )

    assert event["event_type"] == "FINAL_SELECTION_ACCEPTED"
    assert event["candidate_type"] == CANDIDATE_TYPE_SCHEDULE
    assert event["metadata"]["selected_candidate"]["room_id"] == "R-5"
    assert event["metadata"]["confidence_level"] == "MEDIUM"


def test_selection_adapter_uses_context_sanitization():
    context = OptimizationTraceContext()

    event = trace_room_selection(
        context,
        entity_type="section",
        entity_id=6,
        candidate_id="R-6",
        selected_candidate={"room_id": "R-6"},
        accepted_reason="BEST_FIT",
        metadata={"candidate_name": "Alice Student", "safe_count": 2},
    )

    assert event["metadata"]["candidate_name"] == "[REDACTED]"
    assert event["metadata"]["safe_count"] == 2


def test_selection_adapter_appends_events_to_context():
    context = OptimizationTraceContext()

    trace_room_selection(
        context,
        entity_type="section",
        entity_id=7,
        candidate_id="R-7",
        selected_candidate={"room_id": "R-7"},
    )
    trace_staff_selection(
        context,
        entity_type="section",
        entity_id=7,
        candidate_id=7001,
        selected_candidate={"staff_id": 7001},
    )
    trace_final_schedule_selection(
        context,
        entity_type="section",
        entity_id=7,
        candidate_id="schedule-7",
        selected_candidate={"room_id": "R-7", "staff_ids": [7001]},
    )

    assert len(context.events) == 3
