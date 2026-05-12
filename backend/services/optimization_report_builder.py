"""Build normalized, exportable optimization governance reports."""
from __future__ import annotations

from typing import Any, Dict

from services.optimization_pipeline_observer_service import observe_optimization_result


def build_optimization_report(
    *,
    period: object,
    schedules: list,
    submissions_by_section: dict | None = None,
    enrollments_by_section: dict | None = None,
) -> Dict[str, Any]:
    observer = observe_optimization_result(
        period=period,
        schedules=schedules,
        submissions_by_section=submissions_by_section or {},
        enrollments_by_section=enrollments_by_section or {},
    )

    quality = observer.get("quality_summary", {})
    recheck_summary = observer.get("recheck_summary", {})
    issues = observer.get("issues", [])
    governance = observer.get("governance", {})
    explanation = observer.get("explanation_summary", {})

    executive = {
        "status": observer.get("status", "UNKNOWN"),
        "quality_score": quality.get("overall_score"),
        "quality_band": quality.get("quality_band"),
        "governance_state": governance.get("governance_state"),
        "review_priority": governance.get("review_priority"),
        "checked_schedule_count": observer.get("checked_schedule_count", 0),
    }

    severity_summary = {
        "hard_fail_count": recheck_summary.get("hard_fail_count", recheck_summary.get("hard_error_count", 0)),
        "hard_error_count": recheck_summary.get("hard_error_count", recheck_summary.get("hard_fail_count", 0)),
        "warning_count": recheck_summary.get("warning_count", 0),
        "info_count": recheck_summary.get("info_count", 0),
        "suggestion_count": recheck_summary.get("suggestion_count", 0),
    }

    issue_summary = [
        {
            "code": issue.get("code"),
            "severity": issue.get("severity"),
            "category": issue.get("category"),
            "message": issue.get("message"),
            "blocking": issue.get("blocking"),
        }
        for issue in issues
    ]

    return {
        "executive_summary": executive,
        "issue_summary": issue_summary,
        "severity_summary": severity_summary,
        "quality_breakdown": quality,
        "governance": governance,
        "explanation_summary": explanation,
        "raw_observer": observer,
    }
