"""Observer service for read-only optimization analysis artifacts."""
from __future__ import annotations

from typing import Any, Dict, Iterable

from services.optimization_explanation_service import explain_schedule
from services.optimization_governance_service import determine_governance_state
from services.optimization_quality_service import compute_quality_report
from services.optimization_recheck_service import build_recheck_report
from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_EVENT_CANDIDATE_ACCEPTED,
    TRACE_EVENT_CANDIDATE_GENERATED,
    TRACE_EVENT_CANDIDATE_REJECTED,
    TRACE_EVENT_CONSTRAINT_TRIGGERED,
    TRACE_EVENT_FINAL_SELECTION,
    TRACE_EVENT_TRADEOFF_CHOSEN,
    TRACE_SOURCE_POST_HOC,
)

_TRACE_SEVERITY_ORDER: dict[str, int] = {
    "INFO": 0,
    "SUGGESTION": 1,
    "WARNING": 2,
    "HIGH_RISK": 3,
    "HARD_FAIL": 4,
}


def _coerce_trace_payload(
    trace_context: OptimizationTraceContext | dict[str, Any] | None,
) -> dict[str, Any]:
    if trace_context is None:
        return {"trace_id": None, "session_id": None, "events": []}
    if isinstance(trace_context, OptimizationTraceContext):
        payload = trace_context.to_dict()
    elif isinstance(trace_context, dict):
        payload = dict(trace_context)
    else:
        payload = {}
    events = payload.get("events") or []
    if not isinstance(events, list):
        events = []
    return {
        "trace_id": payload.get("trace_id"),
        "session_id": payload.get("session_id"),
        "events": [event for event in events if isinstance(event, dict)],
    }


def _trace_source_breakdown(
    trace_events: list[dict[str, Any]],
    *,
    fallback_count: int,
) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for event in trace_events:
        source = str(event.get("source") or "UNKNOWN")
        breakdown[source] = breakdown.get(source, 0) + 1
    if not breakdown:
        breakdown[TRACE_SOURCE_POST_HOC] = fallback_count
    return breakdown


def _highest_trace_severity(trace_events: list[dict[str, Any]]) -> str | None:
    if not trace_events:
        return None
    ranked = sorted(
        (str(event.get("severity") or "INFO") for event in trace_events),
        key=lambda value: _TRACE_SEVERITY_ORDER.get(value, 0),
    )
    return ranked[-1] if ranked else None


def _native_trace_summary(
    trace_payload: dict[str, Any],
    *,
    source_breakdown: dict[str, int],
) -> dict[str, Any]:
    events = trace_payload["events"]
    candidate_count = sum(
        1
        for event in events
        if event.get("event_type") in {
            TRACE_EVENT_CANDIDATE_GENERATED,
            TRACE_EVENT_CANDIDATE_REJECTED,
            TRACE_EVENT_CANDIDATE_ACCEPTED,
        }
    )
    constraint_count = sum(
        1
        for event in events
        if event.get("event_type") == TRACE_EVENT_CONSTRAINT_TRIGGERED
    )
    selection_count = sum(
        1
        for event in events
        if (
            event.get("event_type") == TRACE_EVENT_CANDIDATE_ACCEPTED
            and event.get("stage") == "SELECTION"
        ) or event.get("event_type") == TRACE_EVENT_TRADEOFF_CHOSEN
    )
    final_selection_count = sum(
        1
        for event in events
        if event.get("event_type") == TRACE_EVENT_FINAL_SELECTION
    )
    return {
        "trace_id": trace_payload.get("trace_id"),
        "session_id": trace_payload.get("session_id"),
        "mode": "NATIVE" if events else "POST_HOC_FALLBACK",
        "total_events": len(events),
        "candidate_trace_count": candidate_count,
        "constraint_trace_count": constraint_count,
        "selection_trace_count": selection_count,
        "final_selection_trace_count": final_selection_count,
        "highest_severity": _highest_trace_severity(events),
        "source_breakdown": dict(source_breakdown),
    }


def _traceability_score(
    trace_summary: dict[str, Any],
    *,
    has_post_hoc_context: bool,
) -> float:
    candidate = 25.0 if trace_summary.get("candidate_trace_count", 0) > 0 else 0.0
    constraint = 25.0 if trace_summary.get("constraint_trace_count", 0) > 0 else 0.0
    selection = 25.0 if trace_summary.get("selection_trace_count", 0) > 0 else 0.0
    final_selection = 25.0 if trace_summary.get("final_selection_trace_count", 0) > 0 else 0.0
    score = candidate + constraint + selection + final_selection
    if score == 0.0 and has_post_hoc_context:
        score = 20.0
    return round(min(100.0, score), 2)


def _normalize_schedule_entry(
    schedule: object,
    submissions_by_section: Dict[int, object],
    enrollments_by_section: Dict[int, set],
) -> Dict[str, Any]:
    section = getattr(schedule, "section", None)
    room = getattr(schedule, "room", None) or {}
    section_id = getattr(section, "id", None)
    submission = submissions_by_section.get(section_id)
    students = enrollments_by_section.get(section_id, set())
    student_ids = set(students)
    supervisions = list(getattr(schedule, "supervisions", []) or [])
    assigned_staff = [
        getattr(s.user, "id", None)
        for s in supervisions
        if getattr(s, "user", None) is not None
    ]
    split_count = getattr(schedule, "split_count", None) or 1
    submission_pages = getattr(submission, "a4_pages_count", None) if submission else None
    schedule_pages = getattr(schedule, "num_pages", None)

    return {
        "course_id": getattr(getattr(section, "course", None), "course_id", None),
        "section_id": section_id,
        "num_students": getattr(section, "num_students", 0) or len(student_ids),
        "room": {
            "id": getattr(room, "id", None),
            "capacity": getattr(room, "capacity", None),
            "building": getattr(room, "building", None),
            "is_accessible": getattr(room, "is_accessible", None),
        },
        "course_preferred_building": getattr(getattr(section, "teaching_room", None), "building", None),
        "assigned_staff": [staff for staff in assigned_staff if staff is not None],
        "student_ids": list(student_ids),
        "paper_distributor": getattr(schedule, "paper_distributor", None),
        "exam_date": str(getattr(schedule, "exam_date", None)) if getattr(schedule, "exam_date", None) else None,
        "exam_time": getattr(schedule, "exam_time", None),
        "staff_load": len([staff for staff in assigned_staff if staff is not None]),
        "split_count": split_count,
        "split_reason": getattr(schedule, "split_reason", None),
        "pickup_qr_ready": bool(getattr(schedule, "pickup_qr_tokens", None)),
        "document_ready": bool(getattr(schedule, "pickup_qr_tokens", None)) and bool(schedule_pages),
        "submission_page_count": submission_pages,
        "schedule_page_count": schedule_pages,
        "accessibility_ready": getattr(room, "is_accessible", None),
        "continuity_group": getattr(schedule, "continuity_group", None),
        "avoided_conflicts": getattr(schedule, "avoided_conflicts", []) or [],
        "rejected_room_candidates": getattr(schedule, "rejected_room_candidates", []) or [],
        "rejected_staff_candidates": getattr(schedule, "rejected_staff_candidates", []) or [],
        "rejected_distributor_candidates": getattr(schedule, "rejected_distributor_candidates", []) or [],
        "rejected_timeslot_candidates": getattr(schedule, "rejected_timeslot_candidates", []) or [],
        "rejected_split_candidates": getattr(schedule, "rejected_split_candidates", []) or [],
    }


def observe_optimization_result(
    *,
    period: object,
    schedules: Iterable,
    submissions_by_section: Dict[int, object] | None = None,
    enrollments_by_section: Dict[int, set] | None = None,
    trace_context: OptimizationTraceContext | dict[str, Any] | None = None,
) -> Dict[str, Any]:
    submissions_by_section = submissions_by_section or {}
    enrollments_by_section = enrollments_by_section or {}

    schedule_list = list(schedules)
    normalized = [
        _normalize_schedule_entry(schedule, submissions_by_section, enrollments_by_section)
        for schedule in schedule_list
    ]

    try:
        explanations = explain_schedule(normalized)
    except Exception:
        explanations = []

    try:
        quality = compute_quality_report(normalized)
    except Exception:
        quality = {"overall_score": 0, "warnings": [], "critical_issues": []}

    try:
        recheck = build_recheck_report(
            period=period,
            schedules=schedule_list,
            submissions_by_section=submissions_by_section,
            enrollments_by_section=enrollments_by_section,
        )
    except Exception:
        recheck = {"status": "UNKNOWN", "summary": {}, "issues": []}

    issues = recheck.get("issues", [])
    governance = determine_governance_state(recheck.get("summary", {}), quality, issues)
    warning_issues = [issue for issue in issues if issue.get("severity") in ("WARNING", "HARD_FAIL")]

    confidences = [
        explanation.get("confidence")
        for explanation in explanations
        if isinstance(explanation, dict) and explanation.get("confidence") is not None
    ]
    avg_confidence = int(sum(confidences) / len(confidences)) if confidences else None
    confidence_levels = [
        explanation.get("confidence_level")
        for explanation in explanations
        if isinstance(explanation, dict) and explanation.get("confidence_level")
    ]

    trace_payload = _coerce_trace_payload(trace_context)
    native_trace_events = trace_payload["events"]
    trace_source_breakdown = _trace_source_breakdown(
        native_trace_events,
        fallback_count=len(normalized),
    )
    native_trace_summary = _native_trace_summary(
        trace_payload,
        source_breakdown=trace_source_breakdown,
    )
    traceability_completeness_score = _traceability_score(
        native_trace_summary,
        has_post_hoc_context=bool(normalized or explanations or issues),
    )

    payload = {
        "quality_summary": quality,
        "explanation_summary": {
            "per_entry": explanations,
            "average_confidence": avg_confidence,
            "confidence_levels": confidence_levels,
            "categories_seen": sorted(
                {
                    category
                    for explanation in explanations
                    for category in explanation.get("explanation_categories", [])
                }
            ),
        },
        "recheck_summary": recheck.get("summary", {}),
        "issues": issues,
        "warning_issues": warning_issues,
        "governance": governance,
        "checked_schedule_count": len(schedule_list),
        "schedule_entries": normalized,
        "schedules": normalized,
        "period_id": getattr(period, "id", None),
        "native_trace_summary": native_trace_summary,
        "native_trace_events": native_trace_events,
        "traceability_completeness_score": traceability_completeness_score,
        "trace_source_breakdown": trace_source_breakdown,
    }
    return payload
