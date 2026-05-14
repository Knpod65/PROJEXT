"""Optimization trace service.

Wraps existing optimizer service outputs (observer payload, recheck issues,
explanation factors, governance decisions) into structured TraceEvent dicts.

ADDITIVE ONLY — this module never calls the CP-SAT solver or modifies
optimizer decisions. It reads already-generated output and annotates it.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from policies.optimization_trace_policy import (
    TraceEvent,
    TraceEventType,
    TraceSource,
    TraceSeverity,
    strip_pii,
)

# Mapping from explanation_service category constants → TraceEventType
_EXPLANATION_CATEGORY_MAP: dict[str, str] = {
    "ROOM_SELECTION": TraceEventType.ROOM_SELECTED,
    "STAFF_ASSIGNMENT": TraceEventType.STAFF_SELECTED,
    "DISTRIBUTION_ASSIGNMENT": TraceEventType.DISTRIBUTOR_SELECTED,
    "SPLIT_DECISION": TraceEventType.SPLIT_DECISION_MADE,
    "TIMESLOT_SELECTION": TraceEventType.CANDIDATE_SCORED,
    "CONFLICT_AVOIDANCE": TraceEventType.CONSTRAINT_APPLIED,
    "FAIRNESS_BALANCING": TraceEventType.PENALTY_APPLIED,
}

# Mapping from explanation source constants → TraceSource
_SOURCE_MAP: dict[str, str] = {
    "SOLVER_TRACE": TraceSource.SOLVER_TRACE,
    "INPUT_CONSTRAINT": TraceSource.POLICY_RULE,
    "POST_HOC_HEURISTIC": TraceSource.POST_HOC_TRACE,
    "POLICY_RULE": TraceSource.POLICY_RULE,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_trace_event(
    event_type: str,
    *,
    entity_type: str | None = None,
    entity_id: Any = None,
    constraint_code: str | None = None,
    reason_code: str | None = None,
    score_delta: float | None = None,
    severity: str = TraceSeverity.INFO,
    source: str = TraceSource.POST_HOC_TRACE,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build and return a single trace event dict with PII stripped from metadata."""
    event = TraceEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        constraint_code=constraint_code,
        reason_code=reason_code,
        score_delta=score_delta,
        severity=severity,
        source=source,
        metadata=strip_pii(metadata or {}),
        timestamp=_now_iso(),
    )
    return asdict(event)


def trace_from_observer_payload(
    observer_payload: dict[str, Any],
    *,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Wrap the dict output of observe_optimization_result() into trace events.

    Produces one OPTIMIZATION_STARTED event plus per-entry FINAL_SELECTION_ACCEPTED
    events for each schedule entry in the payload. Does not call the solver.
    """
    events: list[dict[str, Any]] = []
    ts = _now_iso()

    # Opening event
    summary = observer_payload.get("summary") or {}
    quality = observer_payload.get("quality_report") or {}
    events.append(build_trace_event(
        TraceEventType.OPTIMIZATION_STARTED,
        entity_type="period",
        entity_id=observer_payload.get("period_id"),
        metadata={
            "checked_count": summary.get("checked_schedule_count"),
            "overall_score": quality.get("overall_score"),
            "quality_band": quality.get("quality_band"),
            "session_id": session_id,
        },
    ))

    # Per-entry selection events
    for entry in (observer_payload.get("schedule_entries") or []):
        room = entry.get("room") or {}
        events.append(build_trace_event(
            TraceEventType.FINAL_SELECTION_ACCEPTED,
            entity_type="schedule_entry",
            entity_id=entry.get("section_id"),
            metadata={
                "course_id": entry.get("course_id"),
                "exam_date": entry.get("exam_date"),
                "exam_time": entry.get("exam_time"),
                "room_id": room.get("id"),
                "room_capacity": room.get("capacity"),
                "staff_count": entry.get("staff_load"),
                "split_count": entry.get("split_count"),
            },
        ))

    return events


def trace_from_recheck_issues(
    issues: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Map each recheck issue dict into RECHECK_STARTED/RECHECK_COMPLETED events.

    Issues are the dicts produced by asdict(RecheckIssue(...)) from
    optimization_recheck_service.
    """
    events: list[dict[str, Any]] = []
    issue_list = list(issues)

    events.append(build_trace_event(
        TraceEventType.RECHECK_STARTED,
        entity_type="recheck_session",
        metadata={"issue_count": len(issue_list)},
    ))

    for issue in issue_list:
        severity_raw = (issue.get("severity") or "INFO").upper()
        severity = (
            TraceSeverity.HIGH_RISK
            if severity_raw in ("HARD_FAIL", "HARD_ERROR")
            else TraceSeverity.WARNING
            if severity_raw == "WARNING"
            else TraceSeverity.INFO
        )
        events.append(build_trace_event(
            TraceEventType.CONSTRAINT_APPLIED,
            entity_type=issue.get("category"),
            entity_id=issue.get("course_id"),
            constraint_code=issue.get("code"),
            reason_code=issue.get("code"),
            severity=severity,
            source=_SOURCE_MAP.get(issue.get("source") or "", TraceSource.POST_HOC_TRACE),
            metadata={
                "section": issue.get("section"),
                "exam_date": issue.get("exam_date"),
                "room_id": issue.get("room_id"),
                "message": issue.get("message"),
                "blocking": issue.get("blocking"),
                "can_override": issue.get("can_override"),
            },
        ))

    events.append(build_trace_event(
        TraceEventType.RECHECK_COMPLETED,
        entity_type="recheck_session",
        metadata={
            "total_issues": len(issue_list),
            "blocking_count": sum(1 for i in issue_list if i.get("blocking")),
        },
    ))

    return events


def trace_from_explanation_factors(
    per_entry_explanations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Map each explanation factor from explain_schedule() output into trace events.

    explanation_service.explain_schedule() returns a list of per-entry dicts.
    Each entry has a 'factors' list where each factor has a 'category' key
    that maps to a TraceEventType.
    """
    events: list[dict[str, Any]] = []

    for entry in per_entry_explanations:
        section_id = entry.get("section_id")
        for factor in (entry.get("factors") or []):
            category = factor.get("category") or ""
            event_type = _EXPLANATION_CATEGORY_MAP.get(category, TraceEventType.CANDIDATE_SCORED)
            source_raw = factor.get("source") or "POST_HOC_HEURISTIC"
            source = _SOURCE_MAP.get(source_raw, TraceSource.POST_HOC_TRACE)
            events.append(build_trace_event(
                event_type,
                entity_type="schedule_entry",
                entity_id=section_id,
                reason_code=factor.get("explanation_type"),
                source=source,
                metadata={
                    "summary": factor.get("summary"),
                    "category": category,
                },
            ))

    return events


def trace_governance_decision(
    governance_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return a single GOVERNANCE_DECISION_CREATED trace event from a governance dict."""
    state = governance_payload.get("governance_state", "UNKNOWN")
    priority = governance_payload.get("review_priority", "NORMAL")
    quality = governance_payload.get("quality_snapshot") or {}
    severity = (
        TraceSeverity.HIGH_RISK
        if state in ("BLOCKED", "ESCALATION_REQUIRED")
        else TraceSeverity.WARNING
        if state in ("MANUAL_REVIEW_REQUIRED", "APPROVAL_REQUIRED")
        else TraceSeverity.INFO
    )
    return build_trace_event(
        TraceEventType.GOVERNANCE_DECISION_CREATED,
        entity_type="governance_decision",
        severity=severity,
        source=TraceSource.POLICY_RULE,
        metadata={
            "governance_state": state,
            "review_priority": priority,
            "overall_score": quality.get("overall_score"),
            "quality_band": quality.get("quality_band"),
            "risk_level": quality.get("risk_level"),
        },
    )
