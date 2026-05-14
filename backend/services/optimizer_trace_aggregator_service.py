"""Optimizer trace aggregator service.

Facade over the 4 existing optimization trace services. Aggregates all
trace outputs into a single unified dict. Does NOT duplicate trace logic —
delegates entirely to the underlying services.

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

from typing import Any

from services.optimization_candidate_trace_service import (
    build_candidate_traces,
    candidate_traces_to_dicts,
)
from services.optimization_constraint_trace_service import (
    build_constraint_summary,
    build_constraint_traces,
    constraint_traces_to_dicts,
)
from services.optimization_decision_log_service import (
    build_decision_log,
    decision_log_to_dicts,
)
from services.optimization_trace_service import (
    trace_from_observer_payload,
    trace_from_recheck_issues,
)


def aggregate_optimization_traces(
    *,
    observer_payload: dict[str, Any],
    recheck_issues: list[dict[str, Any]],
    session_id: str | None = None,
) -> dict[str, Any]:
    """Aggregate all optimization trace outputs into a unified dict.

    Args:
        observer_payload: Output of observe_optimization_result().
        recheck_issues:   List of recheck issue dicts from build_recheck_report().
        session_id:       Optional session identifier for trace correlation.

    Returns:
        Dict with candidate_traces, constraint_traces, decision_log,
        trace_events, constraint_summary, and rejection_breakdown.
    """
    schedule_entries: list[dict[str, Any]] = observer_payload.get("schedule_entries") or []

    candidate_trace_objs = build_candidate_traces(schedule_entries)
    candidate_traces = candidate_traces_to_dicts(candidate_trace_objs)

    constraint_trace_objs = build_constraint_traces(recheck_issues)
    constraint_traces = constraint_traces_to_dicts(constraint_trace_objs)
    constraint_summary = build_constraint_summary(constraint_trace_objs)

    decision_log_entries = build_decision_log(observer_payload)
    decision_log = decision_log_to_dicts(decision_log_entries)

    trace_events = (
        trace_from_observer_payload(observer_payload, session_id=session_id)
        + trace_from_recheck_issues(recheck_issues)
    )

    rejection_breakdown = _compute_rejection_breakdown(candidate_traces)

    return {
        "candidate_traces":    candidate_traces,
        "constraint_traces":   constraint_traces,
        "decision_log":        decision_log,
        "trace_events":        trace_events,
        "constraint_summary":  constraint_summary,
        "rejection_breakdown": rejection_breakdown,
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _compute_rejection_breakdown(candidate_traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Count rejections by candidate_type from serialized candidate trace dicts."""
    room_rejections = 0
    staff_rejections = 0
    timeslot_rejections = 0

    for trace in candidate_traces:
        if trace.get("decision") != "REJECTED":
            continue
        ctype = str(trace.get("candidate_type", "")).upper()
        if ctype == "ROOM":
            room_rejections += 1
        elif ctype == "STAFF":
            staff_rejections += 1
        elif ctype == "TIMESLOT":
            timeslot_rejections += 1

    return {
        "room_rejections":     room_rejections,
        "staff_rejections":    staff_rejections,
        "timeslot_rejections": timeslot_rejections,
        "total_rejections":    room_rejections + staff_rejections + timeslot_rejections,
    }
