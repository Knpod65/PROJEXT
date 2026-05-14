"""Candidate trace service for optimization decisions.

Builds structured CandidateTrace objects from normalized schedule entries.
All data comes from the pipeline observer output — this service is post-hoc
and read-only. It does NOT call the solver or change optimizer behavior.

Data source: `rejected_room_candidates` and `rejected_staff_candidates` fields
that the pipeline observer normalizes from schedule ORM objects.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from events.optimization_events import (
    OPTIMIZATION_DOMAIN,
    STAGE_CONSTRAINT_EVALUATION,
    STAGE_SELECTION,
    OptimizationEventType,
)


@dataclass(frozen=True)
class CandidateTrace:
    """Structured record of one candidate selection/rejection decision."""

    trace_id: str
    section_id: Any
    candidate_type: str        # "ROOM" | "STAFF" | "TIMESLOT"
    candidate_id: Any
    decision: str              # "ACCEPTED" | "REJECTED"
    reason: str
    constraint_name: str | None
    severity: str              # "INFO" | "WARNING" | "HARD_FAIL"
    optimization_stage: str
    domain: str
    timestamp: str             # ISO 8601 UTC


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trace_id() -> str:
    return str(uuid.uuid4())


def _parse_rejected_room_candidates(
    section_id: Any,
    candidates: list,
) -> list[CandidateTrace]:
    traces: list[CandidateTrace] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        room_id = item.get("room_id") or item.get("id") or item.get("candidate_id")
        reason = item.get("reason") or item.get("rejection_reason") or "CANDIDATE_REJECTED"
        constraint = item.get("constraint") or item.get("violated_constraint") or item.get("constraint_name")
        severity = item.get("severity", "INFO")
        traces.append(CandidateTrace(
            trace_id=_trace_id(),
            section_id=section_id,
            candidate_type="ROOM",
            candidate_id=room_id,
            decision="REJECTED",
            reason=reason,
            constraint_name=constraint,
            severity=severity,
            optimization_stage=STAGE_CONSTRAINT_EVALUATION,
            domain=OPTIMIZATION_DOMAIN,
            timestamp=_now_iso(),
        ))
    return traces


def _parse_rejected_staff_candidates(
    section_id: Any,
    candidates: list,
) -> list[CandidateTrace]:
    traces: list[CandidateTrace] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        staff_id = item.get("staff_id") or item.get("user_id") or item.get("id") or item.get("candidate_id")
        reason = item.get("reason") or item.get("rejection_reason") or "CANDIDATE_REJECTED"
        constraint = item.get("constraint") or item.get("violated_constraint") or item.get("constraint_name")
        severity = item.get("severity", "INFO")
        traces.append(CandidateTrace(
            trace_id=_trace_id(),
            section_id=section_id,
            candidate_type="STAFF",
            candidate_id=staff_id,
            decision="REJECTED",
            reason=reason,
            constraint_name=constraint,
            severity=severity,
            optimization_stage=STAGE_CONSTRAINT_EVALUATION,
            domain=OPTIMIZATION_DOMAIN,
            timestamp=_now_iso(),
        ))
    return traces


def _accepted_room_trace(entry: dict[str, Any]) -> CandidateTrace | None:
    room = entry.get("room") or {}
    room_id = room.get("id")
    if room_id is None:
        return None
    return CandidateTrace(
        trace_id=_trace_id(),
        section_id=entry.get("section_id"),
        candidate_type="ROOM",
        candidate_id=room_id,
        decision="ACCEPTED",
        reason="BEST_FIT_SELECTED",
        constraint_name=None,
        severity="INFO",
        optimization_stage=STAGE_SELECTION,
        domain=OPTIMIZATION_DOMAIN,
        timestamp=_now_iso(),
    )


def _accepted_staff_traces(entry: dict[str, Any]) -> list[CandidateTrace]:
    traces: list[CandidateTrace] = []
    section_id = entry.get("section_id")
    for staff_id in entry.get("assigned_staff", []) or []:
        if staff_id is None:
            continue
        traces.append(CandidateTrace(
            trace_id=_trace_id(),
            section_id=section_id,
            candidate_type="STAFF",
            candidate_id=staff_id,
            decision="ACCEPTED",
            reason="ASSIGNED",
            constraint_name=None,
            severity="INFO",
            optimization_stage=STAGE_SELECTION,
            domain=OPTIMIZATION_DOMAIN,
            timestamp=_now_iso(),
        ))
    return traces


def build_candidate_traces(
    schedule_entries: list[dict[str, Any]],
) -> list[CandidateTrace]:
    """Build CandidateTrace objects from normalized schedule entries.

    Each entry is a dict as produced by the pipeline observer's
    `_normalize_schedule_entry()`. The fields `rejected_room_candidates` and
    `rejected_staff_candidates` hold lists of rejection metadata dicts (or
    empty lists / missing keys if the optimizer did not populate them).

    Returns all candidate traces: accepted rooms/staff + all rejections.
    """
    traces: list[CandidateTrace] = []
    for entry in schedule_entries:
        section_id = entry.get("section_id")

        # Accepted candidates
        room_trace = _accepted_room_trace(entry)
        if room_trace:
            traces.append(room_trace)
        traces.extend(_accepted_staff_traces(entry))

        # Rejected candidates
        rejected_rooms = entry.get("rejected_room_candidates") or []
        if isinstance(rejected_rooms, list):
            traces.extend(_parse_rejected_room_candidates(section_id, rejected_rooms))

        rejected_staff = entry.get("rejected_staff_candidates") or []
        if isinstance(rejected_staff, list):
            traces.extend(_parse_rejected_staff_candidates(section_id, rejected_staff))

    return traces


def candidate_traces_to_dicts(traces: list[CandidateTrace]) -> list[dict[str, Any]]:
    """Serialize CandidateTrace objects to plain dicts for API responses."""
    return [asdict(t) for t in traces]
