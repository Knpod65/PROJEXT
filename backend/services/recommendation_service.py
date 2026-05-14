"""AI recommendation layer skeleton.

Generates structured, human-approval-gated recommendations from quality
signals, governance decisions, and predictive balancing heuristics.

ARCHITECTURE CONTRACTS (non-negotiable):
- AI must NOT auto-publish or mutate any schedule.
- Every recommendation requires a human approval step before any action.
- Every recommendation must cite rule / reason / source (never free-text blobs).
- No PII in recommendation payloads.
- No governance bypass.
- All output is structured dicts — auditable, loggable, diffable.
"""
from __future__ import annotations

from typing import Any


# ── Category constants ────────────────────────────────────────────────────

CATEGORY_WORKLOAD = "WORKLOAD_BALANCE"
CATEGORY_QUALITY = "QUALITY_IMPROVEMENT"
CATEGORY_GOVERNANCE = "GOVERNANCE_RESOLUTION"
CATEGORY_ROOM = "ROOM_OPTIMIZATION"
CATEGORY_STAFFING = "STAFFING_RISK"


# ── Source constants ──────────────────────────────────────────────────────

SOURCE_PREDICTIVE_HEURISTIC = "predictive_balancing_service"
SOURCE_QUALITY_SCORE = "optimization_quality_service"
SOURCE_GOVERNANCE_STATE = "optimization_governance_service"
SOURCE_RULE_ENGINE = "optimization_rules"


# ── Core recommendation builder ───────────────────────────────────────────

def _rec(
    priority: int,
    category: str,
    action: str,
    message: str,
    source: str,
    *,
    rule: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "priority": priority,
        "category": category,
        "action": action,
        "message": message,
        "source": source,
        "rule": rule,
        "reason": reason,
    }


# ── Main entry point ──────────────────────────────────────────────────────

def generate_recommendations(
    quality_report: dict[str, Any],
    governance_decision: dict[str, Any],
    schedule: list[dict[str, Any]],
    *,
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return prioritized, structured recommendations for human review.

    Args:
        quality_report:      Output of compute_quality_report() — scored dims.
        governance_decision: Output of compute_governance_decision() — state.
        schedule:            Current schedule entries (normalized dicts).
        context:             Optional caller metadata (session_id, actor_id).
                             Never used to alter output logic — audit only.

    Returns:
        List of recommendation dicts, sorted ascending by priority (1 = highest).
        Each dict has: priority, category, action, message, source, rule, reason.

    HUMAN-APPROVAL GATE:
        Callers MUST present every item to an authorized user before taking any
        action. This function is advisory only — it never mutates state.
    """
    recs: list[dict[str, Any]] = []

    recs.extend(_recommendations_from_governance(governance_decision))
    recs.extend(_recommendations_from_quality(quality_report))
    recs.extend(_recommendations_from_predictive(schedule))

    recs.sort(key=lambda r: r["priority"])
    return recs


# ── Governance recommendations ────────────────────────────────────────────

_GOVERNANCE_PRIORITY: dict[str, int] = {
    "BLOCKED": 1,
    "ESCALATION_REQUIRED": 2,
    "MANUAL_REVIEW_REQUIRED": 3,
    "APPROVAL_REQUIRED": 4,
    "AUTO_APPROVED": 10,
}


def _recommendations_from_governance(
    governance_decision: dict[str, Any],
) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    state = governance_decision.get("governance_state", "AUTO_APPROVED")
    priority = _GOVERNANCE_PRIORITY.get(state, 5)

    if state == "BLOCKED":
        recs.append(_rec(
            priority=1,
            category=CATEGORY_GOVERNANCE,
            action="RESOLVE_BLOCKING_ISSUES",
            message=(
                "Schedule is BLOCKED. Resolve all HARD_FAIL governance issues "
                "before publishing. Check governance_issues for required actions."
            ),
            source=SOURCE_GOVERNANCE_STATE,
            rule="GOVERNANCE_BLOCKED",
            reason="Schedule cannot be published while BLOCKED state is active.",
        ))

    elif state == "ESCALATION_REQUIRED":
        recs.append(_rec(
            priority=2,
            category=CATEGORY_GOVERNANCE,
            action="ESCALATE_TO_AUTHORITY",
            message=(
                "Schedule requires escalation to academic authority. "
                "Route for approval before any further action."
            ),
            source=SOURCE_GOVERNANCE_STATE,
            rule="GOVERNANCE_ESCALATION",
            reason="Escalation-required state mandates authority sign-off.",
        ))

    elif state == "MANUAL_REVIEW_REQUIRED":
        recs.append(_rec(
            priority=3,
            category=CATEGORY_GOVERNANCE,
            action="REQUEST_MANUAL_REVIEW",
            message=(
                "Schedule requires manual review by a scheduling officer. "
                "Do not auto-approve."
            ),
            source=SOURCE_GOVERNANCE_STATE,
            rule="GOVERNANCE_MANUAL_REVIEW",
            reason="Policy requires human review when issues cannot be auto-cleared.",
        ))

    elif state == "APPROVAL_REQUIRED":
        recs.append(_rec(
            priority=4,
            category=CATEGORY_GOVERNANCE,
            action="OBTAIN_APPROVAL",
            message=(
                "Schedule is pending approval. Submit for coordinator sign-off."
            ),
            source=SOURCE_GOVERNANCE_STATE,
            rule="GOVERNANCE_APPROVAL",
            reason="Approval-required state must be cleared before publishing.",
        ))

    return recs


# ── Quality recommendations ───────────────────────────────────────────────

def _recommendations_from_quality(
    quality_report: dict[str, Any],
) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    overall = quality_report.get("overall_score")
    if overall is None:
        return recs

    try:
        score = float(overall)
    except (TypeError, ValueError):
        return recs

    if score < 55.0:
        recs.append(_rec(
            priority=2,
            category=CATEGORY_QUALITY,
            action="TRIGGER_REOPTIMIZATION",
            message=(
                f"Overall quality score {score:.1f} is critically low (< 55). "
                "Run re-optimization with relaxed constraints or add resources."
            ),
            source=SOURCE_QUALITY_SCORE,
            rule="QUALITY_CRITICAL_THRESHOLD",
            reason="Scores below 55 indicate the schedule cannot meet minimum standards.",
        ))
    elif score < 70.0:
        recs.append(_rec(
            priority=5,
            category=CATEGORY_QUALITY,
            action="REVIEW_LOW_SCORING_DIMENSIONS",
            message=(
                f"Overall quality score {score:.1f} is below acceptable threshold (70). "
                "Investigate low-scoring dimensions before publishing."
            ),
            source=SOURCE_QUALITY_SCORE,
            rule="QUALITY_REVIEW_THRESHOLD",
            reason="Scores between 55–70 require dimension-level review.",
        ))

    # Per-dimension low scores
    dim_thresholds = {
        "room_efficiency_score": (60.0, 6, "ROOM_EFFICIENCY_LOW"),
        "invigilator_balance_score": (65.0, 6, "INVIGILATOR_BALANCE_LOW"),
        "fairness_score": (65.0, 7, "FAIRNESS_LOW"),
    }
    for dim, (threshold, priority, rule) in dim_thresholds.items():
        val = quality_report.get(dim)
        if val is None:
            continue
        try:
            dim_score = float(val)
        except (TypeError, ValueError):
            continue
        if dim_score < threshold:
            label = dim.replace("_score", "").replace("_", " ").title()
            recs.append(_rec(
                priority=priority,
                category=CATEGORY_QUALITY,
                action="IMPROVE_DIMENSION",
                message=(
                    f"{label} score {dim_score:.1f} is below {threshold:.0f}. "
                    f"Review {dim} drivers and consider targeted adjustments."
                ),
                source=SOURCE_QUALITY_SCORE,
                rule=rule,
                reason=f"{label} below threshold degrades overall schedule acceptability.",
            ))

    return recs


# ── Predictive balancing recommendations ─────────────────────────────────

def _recommendations_from_predictive(
    schedule: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    from services.predictive_balancing_service import recommend_rebalancing

    recs: list[dict[str, Any]] = []
    balancing_recs = recommend_rebalancing(schedule)

    _severity_to_priority = {"HIGH_RISK": 2, "WARNING": 7}

    for b in balancing_recs:
        priority = _severity_to_priority.get(b.get("severity", "WARNING"), 7)
        recs.append(_rec(
            priority=priority,
            category=_risk_type_to_category(b.get("risk_type", "")),
            action=b.get("action", "REVIEW"),
            message=b.get("message", ""),
            source=SOURCE_PREDICTIVE_HEURISTIC,
            rule=b.get("risk_type"),
            reason=b.get("severity"),
        ))

    return recs


def _risk_type_to_category(risk_type: str) -> str:
    mapping = {
        "WORKLOAD_IMBALANCE": CATEGORY_WORKLOAD,
        "FRAGILE_STAFFING_DAY": CATEGORY_STAFFING,
        "SAME_DAY_OVERLOAD": CATEGORY_WORKLOAD,
        "ROOM_BOTTLENECK": CATEGORY_ROOM,
    }
    return mapping.get(risk_type, CATEGORY_STAFFING)
