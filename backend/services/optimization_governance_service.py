"""Governance decision model for optimization results.

This module stays deterministic and additive. It evaluates already-generated
recheck/quality artifacts without changing optimizer behavior.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


LOCAL_GOVERNANCE_THRESHOLDS: dict[str, float] = {
    "hard_fail_block": 1,
    "warning_approval_required": 1,
    "fairness_review_threshold": 72,
    "room_efficiency_review_threshold": 68,
    "staffing_fragility_threshold": 70,
    "split_complexity_threshold": 55,
    "quality_escalation_threshold": 55,
    "quality_review_threshold": 70,
    "conflict_escalation_threshold": 60,
    "staff_review_load_score": 50,
}


def _review_priority(governance_state: str) -> str:
    if governance_state == "BLOCKED":
        return "CRITICAL"
    if governance_state == "ESCALATION_REQUIRED":
        return "HIGH"
    if governance_state == "MANUAL_REVIEW_REQUIRED":
        return "HIGH"
    if governance_state == "APPROVAL_REQUIRED":
        return "NORMAL"
    return "LOW"


def _collect_issue_constraints(issues: Iterable[Dict[str, Any]] | None) -> List[str]:
    constraints: List[str] = []
    for issue in issues or []:
        code = issue.get("code")
        if code and code not in constraints:
            constraints.append(code)
    return constraints


def analyze_override_safety(
    recheck_summary: Dict[str, Any],
    quality_report: Dict[str, Any],
    issues: Iterable[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    thresholds = LOCAL_GOVERNANCE_THRESHOLDS
    issues = list(issues or [])
    violated_constraints = _collect_issue_constraints(issues)
    introduced_risks = []
    override_changes = []

    if recheck_summary.get("hard_fail_count", 0) > 0:
        override_changes.append("Allows progression despite hard validation failures.")
        introduced_risks.append("Operational blockers would remain active after override.")
    if quality_report.get("quality_band") in {"HIGH_RISK", "NEEDS_REVIEW"}:
        override_changes.append("Accepts a lower-quality allocation without re-optimization.")
        introduced_risks.append("Manual execution burden may increase during the exam period.")
    if quality_report.get("document_readiness_score", 100) < 85:
        introduced_risks.append("Document or QR readiness may still be incomplete.")
    if quality_report.get("invigilator_balance_score", 100) < 70:
        introduced_risks.append("Workload balance could trigger staffing complaints or fatigue.")

    if (
        recheck_summary.get("hard_fail_count", 0) > 0
        or quality_report.get("quality_band") == "HIGH_RISK"
        or quality_report.get("overall_score", 100) < thresholds["quality_escalation_threshold"]
        or quality_report.get("invigilator_balance_score", 100) <= thresholds["staff_review_load_score"]
    ):
        severity = "HIGH_RISK"
    elif (
        quality_report.get("quality_band") == "NEEDS_REVIEW"
        or recheck_summary.get("warning_count", 0) > 0
        or quality_report.get("overall_score", 100) < thresholds["quality_review_threshold"]
    ):
        severity = "REVIEW_REQUIRED"
    else:
        severity = "SAFE"

    requires_escalation = severity == "HIGH_RISK"
    if severity == "HIGH_RISK":
        recommendation = "DO_NOT_OVERRIDE_WITHOUT_ESCALATION"
    elif severity == "REVIEW_REQUIRED":
        recommendation = "OVERRIDE_REQUIRES_DOCUMENTED_REVIEW"
    else:
        recommendation = "SAFE_TO_OVERRIDE_IF_OPERATIONALLY_NECESSARY"

    return {
        "override_severity": severity,
        "override_recommendation": recommendation,
        "override_changes": override_changes,
        "introduced_risks": introduced_risks,
        "violated_constraints": violated_constraints,
        "requires_escalation": requires_escalation,
    }


def determine_governance_state(
    recheck_summary: Dict[str, Any],
    quality_report: Dict[str, Any],
    issues: Iterable[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Return a governance decision payload.

    Thresholds are currently embedded here and will be extracted to policy in
    the next slice.
    """
    issues = list(issues or [])
    thresholds = LOCAL_GOVERNANCE_THRESHOLDS
    hard_fail_count = recheck_summary.get("hard_fail_count", recheck_summary.get("hard_error_count", 0))
    warning_count = recheck_summary.get("warning_count", 0)
    fairness_score = quality_report.get("fairness_score", 100)
    room_efficiency_score = quality_report.get("room_efficiency_score", 100)
    invigilator_balance_score = quality_report.get("invigilator_balance_score", 100)
    operational_complexity_score = quality_report.get("operational_complexity_score", 100)
    conflict_risk_score = quality_report.get("conflict_risk_score", 100)
    quality_band = quality_report.get("quality_band", "GOOD")

    governance_notes: List[str] = []
    approval_reasoning: List[str] = []
    escalation_reason = None

    if hard_fail_count >= thresholds["hard_fail_block"]:
        governance_state = "BLOCKED"
        approval_reasoning.append("Hard validation failures are still present in the generated schedule.")
        escalation_reason = "Blocking validation issues must be resolved before release."
        governance_notes.append("Governance cannot accept overrides that leave hard failures unresolved.")
    elif quality_band == "HIGH_RISK" or conflict_risk_score < thresholds["conflict_escalation_threshold"]:
        governance_state = "ESCALATION_REQUIRED"
        approval_reasoning.append("The allocation quality profile is high risk for operational execution.")
        escalation_reason = "Quality risk exceeds standard staff-level approval authority."
        governance_notes.append("Escalate to governance or executive review before any override.")
    elif (
        recheck_summary.get("manual_review_required")
        or fairness_score < thresholds["fairness_review_threshold"]
        or room_efficiency_score < thresholds["room_efficiency_review_threshold"]
        or invigilator_balance_score < thresholds["staffing_fragility_threshold"]
        or operational_complexity_score < thresholds["split_complexity_threshold"]
        or quality_band == "NEEDS_REVIEW"
    ):
        governance_state = "MANUAL_REVIEW_REQUIRED"
        approval_reasoning.append("The allocation requires manual governance review before approval.")
        governance_notes.append("Review fairness, staffing balance, and operational complexity together.")
    elif warning_count >= thresholds["warning_approval_required"] or quality_band == "ACCEPTABLE":
        governance_state = "APPROVAL_REQUIRED"
        approval_reasoning.append("The schedule is usable but still carries warnings that need explicit approval.")
        governance_notes.append("Approval should confirm that warnings are acceptable for the period context.")
    else:
        governance_state = "AUTO_APPROVED"
        approval_reasoning.append("No blocking issues and the quality profile is strong enough for automatic approval.")
        governance_notes.append("Continue to monitor only routine operational readiness items.")

    override_analysis = analyze_override_safety(recheck_summary, quality_report, issues)
    if override_analysis["requires_escalation"] and not escalation_reason:
        escalation_reason = "Override risk is high enough to require higher-level approval."

    review_priority = _review_priority(governance_state)
    readable_reasoning = " ".join(approval_reasoning)

    return {
        "governance_state": governance_state,
        "approval_reasoning": readable_reasoning,
        "escalation_reason": escalation_reason,
        "override_recommendation": override_analysis["override_recommendation"],
        "governance_notes": governance_notes,
        "review_priority": review_priority,
        "override_analysis": override_analysis,
        # Compatibility fields kept for downstream callers.
        "reason": readable_reasoning if readable_reasoning else escalation_reason,
        "quality_snapshot": {
            "overall_score": quality_report.get("overall_score"),
            "quality_band": quality_band,
            "risk_level": quality_report.get("risk_level"),
        },
        "recheck_summary": recheck_summary,
    }
