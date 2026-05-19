"""Governance analytics service.

Pure logic. No DB. No ORM. No HTTP.  All inputs are plain dicts / lists of dicts.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ── Helper ────────────────────────────────────────────────────────────────────

_STATE_BLOCKED = frozenset({
    "BLOCKED", "ESCALATION_REQUIRED", "ESCALATED",
})
_STATE_ROLLBACK = frozenset({"ROLLBACK_REQUIRED", "ROLLED_BACK"})


# ── Public API ────────────────────────────────────────────────────────────────

def compute_governance_analytics(
    governance_decisions: list[dict],
    audit_actions: list[dict],
    period_info: dict | None = None,
) -> dict:
    """Compute governance analytics from pre-computed data.

    Args:
        governance_decisions: [{governance_state, escalation_reason,
                                 override_recommendation, timestamp}]
        audit_actions:         [{action, http_status, duration_ms, timestamp}]
        period_info:           Optional {academic_year, semester, exam_type}

    Returns:
        Governance*Summary-shaped dict.
    """
    total = len(governance_decisions)

    if total == 0:
        return _empty_result(period_info)

    blocker_count = sum(
        1 for d in governance_decisions
        if d.get("governance_state") in _STATE_BLOCKED
    )
    override_count = sum(
        1 for d in governance_decisions
        if d.get("override_recommendation") == "override_approved"
    )
    rollback_count = sum(
        1 for d in governance_decisions
        if d.get("governance_state") in _STATE_ROLLBACK
    )

    # Escalation rate
    escalation_count = sum(
        1 for d in governance_decisions
        if d.get("governance_state") in ("ESCALATION_REQUIRED", "ESCALATED")
    )
    escalation_rate = round(escalation_count / max(total, 1), 4)

    # Governance health score: inverse of blocker ratio
    # 100% auto-approved = 100; 100% blocked = 0
    health_score = round(
        max(0.0, min(100.0, 100.0 * (1.0 - blocker_count / max(total, 1)))), 1
    )

    # Average approval cycle hours from timestamp pairs in governance_decisions
    # Compute from `submitted_at` to `approved_at` within decisions.
    cycle_times = []
    for d in governance_decisions:
        submitted_at = d.get("submitted_at") or d.get("created_at")
        approved_at = d.get("approved_at")
        if submitted_at and approved_at:
            try:
                from datetime import datetime
                fmt = "%Y-%m-%dT%H:%M:%S.%f%z" if "." in submitted_at else "%Y-%m-%dT%H:%M:%S%z"
                s = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
                e = datetime.fromisoformat(approved_at.replace("Z", "+00:00"))
                diff_hrs = abs((e - s).total_seconds()) / 3600
                if diff_hrs > 0:
                    cycle_times.append(diff_hrs)
            except (ValueError, TypeError):
                pass

    avg_cycle = round(
        sum(cycle_times) / len(cycle_times), 2
    ) if cycle_times else 0.0

    # Manual review rate: audit_actions that involve manual review
    MANUAL_REVIEW_ACTIONS = frozenset({
        "sensitive_data_access", "admin_override", "rollback",
    })
    manual_review_count = sum(
        1 for act in audit_actions
        if act.get("action", "") in MANUAL_REVIEW_ACTIONS
    )
    total_audit = max(len(audit_actions), 1)
    manual_review_rate = round(manual_review_count / total_audit, 4)

    # Publication success rate (from publication_triggers in governance decisions)
    total_pub_decisions = sum(
        1 for d in governance_decisions
        if d.get("governance_state") in (
            "AUTO_APPROVED", "APPROVED", "PUBLISHED"
        )
    )
    pub_decisions_total = sum(
        1 for d in governance_decisions
        if "can_publish" in d or d.get("governance_state") in ("AUTO_APPROVED", "APPROVED", "PUBLISHED", "BLOCKED")
    )
    pub_success_rate = round(
        total_pub_decisions / max(pub_decisions_total, 1), 4
    )

    # Top governance risks — sorted by severity priority
    risk_counts: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "severity": "low"}
    )
    SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}
    for d in governance_decisions:
        reason = d.get("escalation_reason") or d.get("governance_state", "UNKNOWN")
        sev = d.get("severity", "medium")
        risk_counts[reason]["count"] += 1
        if SEVERITY_RANK.get(sev, 0) > SEVERITY_RANK.get(risk_counts[reason]["severity"], 0):
            risk_counts[reason]["severity"] = sev

    sorted_risks = sorted(
        risk_counts.items(),
        key=lambda x: (-SEVERITY_RANK.get(x[1]["severity"], 0), -x[1]["count"]),
    )[:5]

    top_governance_risks = [
        {"reason": reason, "count": stats["count"], "severity": stats["severity"]}
        for reason, stats in sorted_risks
    ]

    return {
        "governance_health_score":   health_score,
        "average_approval_cycle_hours": avg_cycle,
        "blocker_count":             blocker_count,
        "override_count":            override_count,
        "rollback_count":            rollback_count,
        "escalation_rate":           escalation_rate,
        "manual_review_rate":        manual_review_rate,
        "publication_success_rate":  pub_success_rate,
        "top_governance_risks":      top_governance_risks,
        "period_info":               period_info or {},
        "_meta": {
            "total_decisions":  total,
            "total_audit_actions": len(audit_actions),
        },
    }


def _empty_result(period_info: dict | None) -> dict:
    return {
        "governance_health_score":    0.0,
        "average_approval_cycle_hours": 0.0,
        "blocker_count":              0,
        "override_count":             0,
        "rollback_count":             0,
        "escalation_rate":            0.0,
        "manual_review_rate":         0.0,
        "publication_success_rate":   0.0,
        "top_governance_risks":       [],
        "period_info":                period_info or {},
    }
