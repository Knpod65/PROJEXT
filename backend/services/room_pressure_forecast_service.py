"""room_pressure_forecast_service.py — Room pressure forecasting."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RoomPressureForecast:
    pressure_level: str
    scarcity_risk: str
    split_risk: str
    peak_slots: int
    recommendation_key: str


class RoomPressureForecastService:
    @staticmethod
    def forecast_room_pressure(
        schedules: list[dict],
        room_capacity: dict,
    ) -> RoomPressureForecast:
        high_density = sum(1 for s in schedules if s.get("student_count", 0) > 100)
        pressure = "high" if high_density > 3 else "moderate"

        return RoomPressureForecast(
            pressure_level=pressure,
            scarcity_risk="elevated" if high_density > 2 else "low",
            split_risk="moderate",
            peak_slots=high_density,
            recommendation_key="room.forecast.openAdditionalRooms",
        )
