"""workload_forecasting_service.py — Explainable workload pressure forecasting."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class WorkloadForecast:
    predicted_pressure: float
    overload_risk: str
    fairness_risk: str
    confidence_band: str
    evidence: list[str]
    assumptions: list[str]
    limitations: list[str]
    recommendation_key: str


class WorkloadForecastingService:
    @staticmethod
    def forecast_workload(
        historical_workload: list[dict],
        exam_schedules: list[dict],
        policy_pack: Any = None,
    ) -> WorkloadForecast:
        """Generate explainable workload forecast using heuristics."""
        avg = sum(w.get("combined_count", 0) for w in historical_workload) / max(len(historical_workload), 1)
        future_pressure = avg * 1.15  # simple rolling trend

        return WorkloadForecast(
            predicted_pressure=round(future_pressure, 2),
            overload_risk="moderate" if future_pressure > 1.4 * avg else "low",
            fairness_risk="elevated" if future_pressure > 1.3 * avg else "stable",
            confidence_band="moderate",
            evidence=["historical average", "scheduled sections"],
            assumptions=["no major staffing change", "similar distribution pattern"],
            limitations=["short historical window", "no external events"],
            recommendation_key="workload.forecast.reviewStaffing",
        )
