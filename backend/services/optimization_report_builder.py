"""Build normalized, exportable optimization governance reports."""
from __future__ import annotations

from typing import Any, Dict

from policies.optimization_policy import DEFAULT_OPTIMIZATION_GOVERNANCE_THRESHOLDS
from services.optimization_pipeline_observer_service import observe_optimization_result
from services.optimization_trace_context import OptimizationTraceContext


# ── Private helpers for additive analytics sections ───────────────────────────


def _build_risk_matrix(quality: dict) -> list[dict]:
    """Map key quality dimensions to risk levels using governance thresholds."""
    t = DEFAULT_OPTIMIZATION_GOVERNANCE_THRESHOLDS
    dimensions = [
        ("fairness",             "fairness_score",               t["fairness_review_threshold"]),
        ("room_efficiency",      "room_efficiency_score",         t["room_efficiency_review_threshold"]),
        ("staffing_balance",     "invigilator_balance_score",     t["staffing_fragility_threshold"]),
        ("split_complexity",     "operational_complexity_score",  t["split_complexity_threshold"]),
        ("conflict_risk",        "conflict_risk_score",           t["conflict_escalation_threshold"]),
        ("governance_readiness", "governance_readiness_score",    t["quality_review_threshold"]),
    ]
    result = []
    for dim_name, key, threshold in dimensions:
        score = quality.get(key)
        if score is None:
            continue
        if score < threshold * 0.85:
            risk_level = "HIGH"
        elif score < threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        result.append({
            "dimension": dim_name,
            "score": float(score),
            "risk_level": risk_level,
            "threshold": float(threshold),
        })
    return result


def _build_rejected_candidate_analytics(schedules: list) -> dict:
    """Count room/staff candidate rejections from raw schedule ORM objects."""
    total_room = 0
    total_staff = 0
    reason_counts: dict[str, int] = {}

    for s in schedules:
        rejected_rooms = getattr(s, "rejected_room_candidates", None) or []
        rejected_staff = getattr(s, "rejected_staff_candidates", None) or []
        total_room += len(rejected_rooms)
        total_staff += len(rejected_staff)
        for candidate in list(rejected_rooms) + list(rejected_staff):
            reason = candidate.get("reason") if isinstance(candidate, dict) else None
            reason = reason or "UNKNOWN"
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    top_reasons = sorted(
        [{"reason": r, "count": c} for r, c in reason_counts.items()],
        key=lambda x: -x["count"],
    )[:5]

    return {
        "total_room_rejections": total_room,
        "total_staff_rejections": total_staff,
        "top_rejection_reasons": top_reasons,
    }


def _build_invigilator_overload_summary(quality: dict, recheck_summary: dict) -> dict:
    """Derive overload severity from invigilator balance score."""
    inv_balance = quality.get("invigilator_balance_score", 100)
    overloaded_count = 1 if inv_balance < 55 else 0
    at_risk_count = 1 if 55 <= inv_balance < 70 else 0
    fragile_days = int(recheck_summary.get("fragile_day_count", 0))
    return {
        "overloaded_count": overloaded_count,
        "at_risk_count": at_risk_count,
        "fragile_days": fragile_days,
    }


def _build_fairness_summary(quality: dict) -> dict:
    """Summarize fairness state from quality report fields."""
    fairness_score = quality.get("fairness_score")
    inv_balance = quality.get("invigilator_balance_score", 100)
    imbalanced_sections = 1 if (inv_balance is not None and inv_balance < 72) else 0

    if fairness_score is None:
        balance_verdict = "UNKNOWN"
    elif fairness_score >= 90:
        balance_verdict = "BALANCED"
    elif fairness_score >= 72:
        balance_verdict = "ACCEPTABLE"
    elif fairness_score >= 55:
        balance_verdict = "NEEDS_REBALANCING"
    else:
        balance_verdict = "CRITICALLY_IMBALANCED"

    return {
        "fairness_score": float(fairness_score) if fairness_score is not None else None,
        "imbalanced_sections": imbalanced_sections,
        "balance_verdict": balance_verdict,
    }


def _compute_traceability_score(schedules: list, explanation: dict, governance: dict) -> float:
    """Calculate what fraction of expected trace fields are present, 0–100."""
    if schedules:
        checks = 0
        passed = 0
        for s in schedules:
            checks += 5
            if getattr(s, "exam_date", None):
                passed += 1
            if getattr(s, "exam_time", None):
                passed += 1
            if getattr(s, "room_id", None) or getattr(s, "room", None):
                passed += 1
            if getattr(s, "supervisions", None) is not None:
                passed += 1
            if getattr(s, "section", None) is not None or getattr(s, "section_id", None):
                passed += 1
        base = (passed / checks) * 100.0 if checks else 0.0
    else:
        base = 0.0

    bonus = 0.0
    if explanation.get("per_entry"):
        bonus += 5.0
    if governance.get("governance_state"):
        bonus += 5.0

    return round(min(100.0, base + bonus), 2)


def _build_quality_band_summary(quality: dict, governance: dict) -> dict:
    """Summarize quality band and approval eligibility."""
    band = quality.get("quality_band", "UNKNOWN")
    score = quality.get("overall_score")
    governance_state = governance.get("governance_state", "")
    can_auto_approve = governance_state == "AUTO_APPROVED"
    requires_review = governance_state in (
        "APPROVAL_REQUIRED",
        "MANUAL_REVIEW_REQUIRED",
        "ESCALATION_REQUIRED",
    )
    return {
        "band": band,
        "score": float(score) if score is not None else None,
        "can_auto_approve": can_auto_approve,
        "requires_review": requires_review,
    }


def _compute_confidence_score(explanation: dict) -> float:
    """Return average explanation confidence as 0–100 float."""
    avg = explanation.get("average_confidence")
    return float(avg) if avg is not None else 0.0


# ── Public API ────────────────────────────────────────────────────────────────


def build_optimization_report(
    *,
    period: object,
    schedules: list,
    submissions_by_section: dict | None = None,
    enrollments_by_section: dict | None = None,
    trace_context: OptimizationTraceContext | dict[str, Any] | None = None,
) -> Dict[str, Any]:
    observer = observe_optimization_result(
        period=period,
        schedules=schedules,
        submissions_by_section=submissions_by_section or {},
        enrollments_by_section=enrollments_by_section or {},
        trace_context=trace_context,
    )

    quality = observer.get("quality_summary", {})
    recheck_summary = observer.get("recheck_summary", {})
    issues = observer.get("issues", [])
    governance = observer.get("governance", {})
    explanation = observer.get("explanation_summary", {})
    native_trace_summary = observer.get("native_trace_summary", {})
    native_trace_events = observer.get("native_trace_events", [])
    trace_source_breakdown = observer.get("trace_source_breakdown", {})

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
        # ── existing keys (unchanged) ──
        "executive_summary": executive,
        "issue_summary": issue_summary,
        "severity_summary": severity_summary,
        "quality_breakdown": quality,
        "governance": governance,
        "explanation_summary": explanation,
        "raw_observer": observer,
        # ── additive analytics keys ──
        "risk_matrix": _build_risk_matrix(quality),
        "rejected_candidate_analytics": _build_rejected_candidate_analytics(schedules),
        "invigilator_overload_summary": _build_invigilator_overload_summary(quality, recheck_summary),
        "fairness_summary": _build_fairness_summary(quality),
        "native_trace_summary": native_trace_summary,
        "native_trace_events": native_trace_events,
        "traceability_completeness_score": observer.get(
            "traceability_completeness_score",
            _compute_traceability_score(schedules, explanation, governance),
        ),
        "trace_source_breakdown": trace_source_breakdown,
        "quality_band_summary": _build_quality_band_summary(quality, governance),
        "optimization_confidence_score": _compute_confidence_score(explanation),
    }
