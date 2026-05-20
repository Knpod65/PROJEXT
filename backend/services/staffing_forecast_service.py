"""staffing_forecast_service.py — Staffing shortage forecasting."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class StaffingForecast:
    shortage_risk: str
    affected_slots: int
    staffing_gap: float
    confidence_band: str
    recommendation_key: str


class StaffingForecastService:
    @staticmethod
    def forecast_shortage(
        schedules: list[dict],
        available_staff: int,
        historical_overload: list[dict],
    ) -> StaffingForecast:
        required = len(schedules) * 2  # rough heuristic
        gap = max(0, required - available_staff)
        risk = "high" if gap > 5 else "moderate" if gap > 0 else "low"

        return StaffingForecast(
            shortage_risk=risk,
            affected_slots=gap,
            staffing_gap=round(gap / max(required, 1), 2),
            confidence_band="moderate",
            recommendation_key="staffing.forecast.increaseInvigilators",
        )
