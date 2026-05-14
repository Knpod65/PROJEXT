"""Optimization comparison service.

Compares two quality reports (real vs simulated) and returns a structured
diff showing score deltas per dimension.

The input is the dict output of compute_quality_report() — the same structure
for both baseline and alternative, making them directly comparable.
"""
from __future__ import annotations

from typing import Any

# Dimensions tracked by the comparison. These must match keys in
# compute_quality_report() output. Non-numeric or missing keys are skipped.
SCORED_DIMENSIONS = (
    "fairness_score",
    "room_efficiency_score",
    "invigilator_balance_score",
    "distribution_balance_score",
    "conflict_risk_score",
    "operational_complexity_score",
    "document_readiness_score",
    "qr_readiness_score",
    "governance_readiness_score",
)


def compare_quality_reports(
    baseline: dict[str, Any],
    alternative: dict[str, Any],
    *,
    label_baseline: str = "current",
    label_alternative: str = "simulated",
) -> dict[str, Any]:
    """Return a structured comparison between baseline and alternative quality reports.

    Returns:
      {
        "dimension_deltas": {
          "fairness_score": {"current": 75, "simulated": 82, "delta": 7, "improved": True},
          ...
        },
        "overall_delta": float,
        "alternative_is_better": bool,
        "baseline_band": str | None,
        "alternative_band": str | None,
        "baseline_score": float | None,
        "alternative_score": float | None,
        "improved_dimensions": [str, ...],
        "regressed_dimensions": [str, ...],
      }
    """
    deltas: dict[str, dict[str, Any]] = {}
    improved: list[str] = []
    regressed: list[str] = []

    for dim in SCORED_DIMENSIONS:
        base_val = baseline.get(dim)
        alt_val = alternative.get(dim)
        if base_val is None or alt_val is None:
            continue
        try:
            base_f = float(base_val)
            alt_f = float(alt_val)
        except (TypeError, ValueError):
            continue

        delta = alt_f - base_f
        deltas[dim] = {
            label_baseline: base_f,
            label_alternative: alt_f,
            "delta": round(delta, 2),
            "improved": delta > 0,
        }
        if delta > 0:
            improved.append(dim)
        elif delta < 0:
            regressed.append(dim)

    base_overall = baseline.get("overall_score")
    alt_overall = alternative.get("overall_score")
    overall_delta: float | None = None
    if base_overall is not None and alt_overall is not None:
        try:
            overall_delta = round(float(alt_overall) - float(base_overall), 2)
        except (TypeError, ValueError):
            overall_delta = None

    return {
        "dimension_deltas": deltas,
        "overall_delta": overall_delta,
        "alternative_is_better": (overall_delta is not None and overall_delta > 0),
        "baseline_band": baseline.get("quality_band"),
        "alternative_band": alternative.get("quality_band"),
        "baseline_score": base_overall,
        "alternative_score": alt_overall,
        "improved_dimensions": improved,
        "regressed_dimensions": regressed,
    }


def compare_governance_decisions(
    baseline_governance: dict[str, Any],
    alternative_governance: dict[str, Any],
    *,
    label_baseline: str = "current",
    label_alternative: str = "simulated",
) -> dict[str, Any]:
    """Compare two governance decision payloads and return state delta.

    Returns:
      {
        "baseline_state": str,
        "alternative_state": str,
        "state_improved": bool,  # lower severity = improved
        "baseline_priority": str,
        "alternative_priority": str,
      }
    """
    _severity_order = {
        "AUTO_APPROVED": 0,
        "APPROVAL_REQUIRED": 1,
        "MANUAL_REVIEW_REQUIRED": 2,
        "ESCALATION_REQUIRED": 3,
        "BLOCKED": 4,
    }
    base_state = baseline_governance.get("governance_state", "UNKNOWN")
    alt_state = alternative_governance.get("governance_state", "UNKNOWN")
    base_sev = _severity_order.get(base_state, 99)
    alt_sev = _severity_order.get(alt_state, 99)

    return {
        "baseline_state": base_state,
        "alternative_state": alt_state,
        "state_improved": alt_sev < base_sev,
        "baseline_priority": baseline_governance.get("review_priority", "UNKNOWN"),
        "alternative_priority": alternative_governance.get("review_priority", "UNKNOWN"),
    }
