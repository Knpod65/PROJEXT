"""Decision log service for optimization outcomes.

Produces a structured DecisionLogEntry per scheduled section, capturing what
was decided (room, staff, date, split) and why (decision factors, confidence,
governance relevance). All data is read from the observer payload — post-hoc,
read-only, no solver changes.

Data source: output of observe_optimization_result() from the pipeline
observer service, plus the explanation_summary it contains.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DecisionLogEntry:
    """One optimizer decision record per scheduled section."""

    log_id: str
    section_id: Any
    course_id: str | None
    chosen_room_id: Any
    chosen_room_capacity: int | None
    chosen_staff_ids: tuple           # immutable, may be empty
    exam_date: str | None
    exam_time: str | None
    split_count: int
    decision_factors: tuple           # category names from explanation factors
    confidence: str                   # "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN"
    policy_source: str
    governance_relevance: str         # "NONE" | "REVIEW_REQUIRED" | "BLOCKED"
    audit_metadata: dict
    timestamp: str                    # ISO 8601 UTC


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_id() -> str:
    return str(uuid.uuid4())


_GOVERNANCE_STATE_TO_RELEVANCE: dict[str, str] = {
    "AUTO_APPROVED": "NONE",
    "APPROVAL_REQUIRED": "REVIEW_REQUIRED",
    "MANUAL_REVIEW_REQUIRED": "REVIEW_REQUIRED",
    "ESCALATION_REQUIRED": "REVIEW_REQUIRED",
    "BLOCKED": "BLOCKED",
}


def _governance_relevance(observer_payload: dict[str, Any]) -> str:
    governance = observer_payload.get("governance") or {}
    state = governance.get("governance_state", "AUTO_APPROVED")
    return _GOVERNANCE_STATE_TO_RELEVANCE.get(state, "NONE")


def _extract_decision_factors(entry: dict[str, Any]) -> tuple[str, ...]:
    """Extract decision factor category names from a schedule entry.

    The pipeline observer stores per-entry explanation data indirectly through
    the explanation_summary. At the entry level, split_reason and
    avoided_conflicts provide partial factor signals.
    """
    factors: list[str] = []
    if entry.get("split_count", 1) > 1:
        factors.append("SPLIT_DECISION")
    if entry.get("avoided_conflicts"):
        factors.append("CONFLICT_AVOIDANCE")
    if entry.get("course_preferred_building") and entry.get("room", {}).get("building"):
        factors.append("ROOM_SELECTION")
    if entry.get("assigned_staff"):
        factors.append("STAFF_ASSIGNMENT")
    if entry.get("paper_distributor"):
        factors.append("DISTRIBUTION_ASSIGNMENT")
    if not factors:
        factors.append("TIMESLOT_SELECTION")
    return tuple(factors)


def _extract_confidence(observer_payload: dict[str, Any]) -> str:
    """Derive overall confidence from the explanation summary."""
    explanation = observer_payload.get("explanation_summary") or {}
    # explanation_summary contains per-section explanations; derive overall
    factors = explanation.get("factors", [])
    if not factors:
        return "LOW"
    confidences = [f.get("source", "") for f in factors if isinstance(f, dict)]
    if any("SOLVER" in c for c in confidences):
        return "HIGH"
    if any("POLICY" in c for c in confidences):
        return "MEDIUM"
    return "LOW"


def _extract_policy_source(observer_payload: dict[str, Any]) -> str:
    explanation = observer_payload.get("explanation_summary") or {}
    factors = explanation.get("factors", [])
    if not factors:
        return "POST_HOC_HEURISTIC"
    sources = [f.get("source", "") for f in factors if isinstance(f, dict)]
    if any("SOLVER" in s for s in sources):
        return "SOLVER_TRACE"
    if any("POLICY" in s for s in sources):
        return "POLICY_RULE"
    return "POST_HOC_HEURISTIC"


def build_decision_log(
    observer_payload: dict[str, Any],
) -> list[DecisionLogEntry]:
    """Build one DecisionLogEntry per schedule entry in the observer payload.

    Args:
        observer_payload: dict returned by observe_optimization_result().
                          Expected keys: schedules (normalized entries),
                          governance, explanation_summary, status.

    Returns:
        List of DecisionLogEntry — one per section in the schedule.
    """
    schedules = observer_payload.get("schedules") or []
    governance_relevance = _governance_relevance(observer_payload)
    confidence = _extract_confidence(observer_payload)
    policy_source = _extract_policy_source(observer_payload)
    timestamp = _now_iso()

    entries: list[DecisionLogEntry] = []
    for entry in schedules:
        if not isinstance(entry, dict):
            continue
        room = entry.get("room") or {}
        entries.append(DecisionLogEntry(
            log_id=_log_id(),
            section_id=entry.get("section_id"),
            course_id=entry.get("course_id"),
            chosen_room_id=room.get("id"),
            chosen_room_capacity=room.get("capacity"),
            chosen_staff_ids=tuple(
                s for s in (entry.get("assigned_staff") or []) if s is not None
            ),
            exam_date=entry.get("exam_date"),
            exam_time=entry.get("exam_time"),
            split_count=int(entry.get("split_count") or 1),
            decision_factors=_extract_decision_factors(entry),
            confidence=confidence,
            policy_source=policy_source,
            governance_relevance=governance_relevance,
            audit_metadata={
                "num_students": entry.get("num_students"),
                "paper_distributor": entry.get("paper_distributor"),
                "split_reason": entry.get("split_reason"),
            },
            timestamp=timestamp,
        ))
    return entries


def decision_log_to_dicts(entries: list[DecisionLogEntry]) -> list[dict[str, Any]]:
    """Serialize DecisionLogEntry objects to plain dicts for API/audit output."""
    result: list[dict[str, Any]] = []
    for e in entries:
        d = asdict(e)
        d["chosen_staff_ids"] = list(e.chosen_staff_ids)
        d["decision_factors"] = list(e.decision_factors)
        result.append(d)
    return result
