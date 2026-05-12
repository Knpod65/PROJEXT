"""Observer service for read-only optimization analysis artifacts."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from services.optimization_explanation_service import explain_schedule
from services.optimization_governance_service import determine_governance_state
from services.optimization_quality_service import compute_quality_report
from services.optimization_recheck_service import build_recheck_report


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
    }
    return payload
