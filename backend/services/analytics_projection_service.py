"""Analytics projection service.

Read-only historical trend analysis across optimization periods.
No DB calls. No solver. No framework. Input is pre-loaded dicts.
All functions return JSON-safe dicts.
"""
from __future__ import annotations

from typing import Any


# ── Private helpers ───────────────────────────────────────────────────────────

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _trend_direction(values: list[float]) -> str:
    """Return 'improving', 'degrading', or 'stable' based on first vs last."""
    if len(values) < 2:
        return "stable"
    delta = values[-1] - values[0]
    if delta > 2.0:
        return "improving"
    if delta < -2.0:
        return "degrading"
    return "stable"


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


# ── Public API ────────────────────────────────────────────────────────────────

def project_governance_trend(governance_snapshots: list[dict]) -> dict:
    """Governance state distribution, escalation rate, auto-approval rate.

    Args:
        governance_snapshots: List of governance dicts from determine_governance_state().
                              Each must have 'governance_state' key.

    Returns:
        Dict with state_distribution, escalation_rate, auto_approval_rate,
        snapshot_count, and trend_summary.
    """
    if not governance_snapshots:
        return {
            "snapshot_count": 0,
            "state_distribution": {},
            "escalation_rate": 0.0,
            "auto_approval_rate": 0.0,
            "trend_summary": "no_data",
        }

    state_counts: dict[str, int] = {}
    escalation_count = 0
    auto_approved_count = 0
    total = len(governance_snapshots)

    for snap in governance_snapshots:
        state = snap.get("governance_state", "UNKNOWN")
        state_counts[state] = state_counts.get(state, 0) + 1
        if state in ("ESCALATION_REQUIRED", "ESCALATED"):
            escalation_count += 1
        if state == "AUTO_APPROVED":
            auto_approved_count += 1

    escalation_rate = _safe_rate(escalation_count, total)
    auto_approval_rate = _safe_rate(auto_approved_count, total)

    if auto_approval_rate > 0.7:
        trend_summary = "healthy"
    elif escalation_rate > 0.3:
        trend_summary = "high_escalation"
    else:
        trend_summary = "moderate"

    return {
        "snapshot_count": total,
        "state_distribution": state_counts,
        "escalation_rate": escalation_rate,
        "auto_approval_rate": auto_approval_rate,
        "trend_summary": trend_summary,
    }


def project_quality_trend(quality_snapshots: list[dict]) -> dict:
    """Quality score trend direction and per-dimension volatility.

    Args:
        quality_snapshots: List of quality_report dicts from compute_quality_report().
                           Each should have 'overall_score' and optional dimension scores.

    Returns:
        Dict with score_series, trend_direction, average_score, min_score, max_score,
        band_history, snapshot_count.
    """
    if not quality_snapshots:
        return {
            "snapshot_count": 0,
            "score_series": [],
            "trend_direction": "stable",
            "average_score": 0.0,
            "min_score": 0.0,
            "max_score": 0.0,
            "band_history": [],
        }

    scores = [_safe_float(s.get("overall_score")) for s in quality_snapshots]
    bands = [s.get("quality_band", "UNKNOWN") for s in quality_snapshots]

    return {
        "snapshot_count": len(quality_snapshots),
        "score_series": [round(s, 2) for s in scores],
        "trend_direction": _trend_direction(scores),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "min_score": round(min(scores), 2) if scores else 0.0,
        "max_score": round(max(scores), 2) if scores else 0.0,
        "band_history": bands,
    }


def project_invigilator_overload_trend(overload_snapshots: list[dict]) -> dict:
    """Overloaded and at-risk invigilator trends across periods.

    Args:
        overload_snapshots: List of dicts with keys: overloaded_count, at_risk_count,
                            fragile_day_count (or similar).

    Returns:
        Dict with overloaded_series, at_risk_series, fragile_days_total,
        peak_overloaded, trend_direction, snapshot_count.
    """
    if not overload_snapshots:
        return {
            "snapshot_count": 0,
            "overloaded_series": [],
            "at_risk_series": [],
            "fragile_days_total": 0,
            "peak_overloaded": 0,
            "trend_direction": "stable",
        }

    overloaded = [int(s.get("overloaded_count", 0)) for s in overload_snapshots]
    at_risk = [int(s.get("at_risk_count", 0)) for s in overload_snapshots]
    fragile_days = sum(int(s.get("fragile_day_count", s.get("fragile_days", 0))) for s in overload_snapshots)

    overloaded_float = [float(v) for v in overloaded]

    return {
        "snapshot_count": len(overload_snapshots),
        "overloaded_series": overloaded,
        "at_risk_series": at_risk,
        "fragile_days_total": fragile_days,
        "peak_overloaded": max(overloaded) if overloaded else 0,
        "trend_direction": _trend_direction(overloaded_float),
    }


def project_room_utilization_trend(observer_snapshots: list[dict]) -> dict:
    """Room utilization trend derived from quality room_efficiency_score.

    Args:
        observer_snapshots: List of observer or quality report dicts with
                            'room_efficiency_score' or nested 'quality_summary'.

    Returns:
        Dict with utilization_series, average_utilization, trend_direction,
        snapshot_count.
    """
    if not observer_snapshots:
        return {
            "snapshot_count": 0,
            "utilization_series": [],
            "average_utilization": 0.0,
            "trend_direction": "stable",
        }

    def _extract_room_score(snap: dict) -> float:
        score = snap.get("room_efficiency_score")
        if score is None:
            qs = snap.get("quality_summary", snap.get("quality_breakdown", {}))
            score = qs.get("room_efficiency_score") if isinstance(qs, dict) else None
        return _safe_float(score)

    series = [_extract_room_score(s) for s in observer_snapshots]

    return {
        "snapshot_count": len(observer_snapshots),
        "utilization_series": [round(v, 2) for v in series],
        "average_utilization": round(sum(series) / len(series), 2) if series else 0.0,
        "trend_direction": _trend_direction(series),
    }


def project_fairness_trend(fairness_snapshots: list[dict]) -> dict:
    """Fairness score trend and balance verdict distribution.

    Args:
        fairness_snapshots: List of dicts with 'fairness_score' and optional
                            'balance_verdict' keys.

    Returns:
        Dict with score_series, trend_direction, average_score,
        verdict_distribution, snapshot_count.
    """
    if not fairness_snapshots:
        return {
            "snapshot_count": 0,
            "score_series": [],
            "trend_direction": "stable",
            "average_score": 0.0,
            "verdict_distribution": {},
        }

    scores = [_safe_float(s.get("fairness_score")) for s in fairness_snapshots]
    verdicts: dict[str, int] = {}
    for snap in fairness_snapshots:
        v = snap.get("balance_verdict", "UNKNOWN")
        verdicts[v] = verdicts.get(v, 0) + 1

    return {
        "snapshot_count": len(fairness_snapshots),
        "score_series": [round(s, 2) for s in scores],
        "trend_direction": _trend_direction(scores),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "verdict_distribution": verdicts,
    }


def compare_periods(baseline_report: dict, current_report: dict) -> dict:
    """Compare two full optimization reports across quality, governance, and risk dimensions.

    Args:
        baseline_report: The earlier period's report dict (output of build_optimization_report).
        current_report:  The current period's report dict.

    Returns:
        Dict with deltas for overall_score, governance_state, risk changes,
        hard_fail_delta, warning_delta, and a summary verdict.
    """
    def _qscore(report: dict) -> float:
        qs = report.get("quality_breakdown", report.get("quality_summary", {}))
        return _safe_float(qs.get("overall_score") if isinstance(qs, dict) else None)

    def _gov_state(report: dict) -> str:
        gov = report.get("governance", {})
        return gov.get("governance_state", "UNKNOWN") if isinstance(gov, dict) else "UNKNOWN"

    def _hard_fails(report: dict) -> int:
        ss = report.get("severity_summary", report.get("recheck_summary", {}))
        return int(ss.get("hard_fail_count", ss.get("hard_error_count", 0))) if isinstance(ss, dict) else 0

    def _warnings(report: dict) -> int:
        ss = report.get("severity_summary", report.get("recheck_summary", {}))
        return int(ss.get("warning_count", 0)) if isinstance(ss, dict) else 0

    baseline_score = _qscore(baseline_report)
    current_score = _qscore(current_report)
    score_delta = round(current_score - baseline_score, 2)

    hard_fail_delta = _hard_fails(current_report) - _hard_fails(baseline_report)
    warning_delta = _warnings(current_report) - _warnings(baseline_report)

    if score_delta > 5 and hard_fail_delta <= 0:
        verdict = "improved"
    elif score_delta < -5 or hard_fail_delta > 0:
        verdict = "degraded"
    else:
        verdict = "stable"

    return {
        "baseline_score": round(baseline_score, 2),
        "current_score": round(current_score, 2),
        "score_delta": score_delta,
        "baseline_governance": _gov_state(baseline_report),
        "current_governance": _gov_state(current_report),
        "hard_fail_delta": hard_fail_delta,
        "warning_delta": warning_delta,
        "verdict": verdict,
    }
