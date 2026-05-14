"""Executive risk service.

Aggregates existing quality/governance/readiness outputs into a single
executive-facing risk view. Does NOT recompute metrics — pulls from the
outputs of compute_quality_report(), determine_governance_state(), and
assess_publication_readiness().

Pure logic. No DB, no ORM, no HTTP.
"""
from __future__ import annotations

from typing import Any

_PDPA_KEYWORDS: frozenset[str] = frozenset({"pdpa", "pii", "personal", "privacy", "data protection"})


def compute_executive_risk_report(
    *,
    quality_report: dict[str, Any],
    governance: dict[str, Any],
    recheck_summary: dict[str, Any],
    readiness_dict: dict[str, Any],
) -> dict[str, Any]:
    """Build an executive risk view aggregating existing service outputs.

    Args:
        quality_report:  Output of compute_quality_report() or quality_breakdown key
                         from build_optimization_report().
        governance:      Output of determine_governance_state().
        recheck_summary: Dict with hard_fail_count and warning_count.
        readiness_dict:  asdict(PublicationReadiness) from assess_publication_readiness().

    Returns:
        Executive risk dict with overall_risk_band, publishability_score,
        governance_health, critical_blockers, and categorized risk lists.
    """
    gov_state = governance.get("governance_state", "")
    hard_fail_count = int(recheck_summary.get(
        "hard_fail_count", recheck_summary.get("hard_error_count", 0)
    ))
    warning_count = int(recheck_summary.get("warning_count", 0))
    risk_score = float(readiness_dict.get("risk_score", 100.0))

    overall_risk_band = _compute_risk_band(gov_state, hard_fail_count, risk_score, warning_count)
    governance_health = _compute_governance_health(gov_state)
    publishability_score = round(max(0.0, 100.0 - risk_score), 2)

    critical_blockers = [
        b for b in readiness_dict.get("blockers", [])
        if isinstance(b, dict) and b.get("severity") == "HARD_FAIL"
    ]

    all_warnings: list[str] = list(quality_report.get("warnings", []))
    pdpa_risks = [w for w in all_warnings if any(kw in w.lower() for kw in _PDPA_KEYWORDS)]
    other_warnings = [w for w in all_warnings if w not in pdpa_risks]

    quality_snap = {
        "overall_score": quality_report.get("overall_score"),
        "quality_band":  quality_report.get("quality_band", ""),
        "risk_level":    quality_report.get("risk_level", ""),
    }

    return {
        "overall_risk_band":    overall_risk_band,
        "publishability_score": publishability_score,
        "governance_health":    governance_health,
        "critical_blockers":    critical_blockers,
        "operational_risks":    list(quality_report.get("future_operational_risks", [])),
        "pdpa_risks":           pdpa_risks,
        "fairness_risks":       list(quality_report.get("fairness_instability_warnings", [])),
        "staffing_risks":       list(quality_report.get("staffing_fragility_warnings", [])),
        "overloaded_day_risks": list(quality_report.get("overloaded_day_warnings", [])),
        "quality_snapshot":     quality_snap,
        "risk_summary":         quality_report.get("risk_summary", ""),
        "hard_fail_count":      hard_fail_count,
        "warning_count":        warning_count,
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _compute_risk_band(
    gov_state: str,
    hard_fail_count: int,
    risk_score: float,
    warning_count: int,
) -> str:
    if gov_state == "BLOCKED" or hard_fail_count > 0:
        return "CRITICAL"
    if risk_score >= 70 or gov_state in ("ESCALATION_REQUIRED", "MANUAL_REVIEW_REQUIRED"):
        return "HIGH"
    if risk_score >= 40 or warning_count > 3:
        return "MEDIUM"
    return "LOW"


def _compute_governance_health(gov_state: str) -> str:
    if gov_state == "BLOCKED":
        return "BLOCKED"
    if gov_state in ("ESCALATION_REQUIRED", "MANUAL_REVIEW_REQUIRED", "APPROVAL_REQUIRED"):
        return "REVIEW_REQUIRED"
    return "HEALTHY"
