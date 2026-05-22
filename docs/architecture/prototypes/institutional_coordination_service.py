"""institutional_coordination_service.py — Cross-unit coordination orchestration."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class CoordinationStatus:
    coordination_state: str
    dependent_units: list[str]
    blocking_units: list[str]
    synchronization_risk: str
    recommendations: list[str]


class InstitutionalCoordinationService:
    @staticmethod
    def coordinate_units(
        units: list[str],
        operational_state: dict[str, Any],
    ) -> CoordinationStatus:
        """Provide coordination status across units."""
        blocking = [u for u in units if operational_state.get(u, {}).get("blocked", False)]
        risk = "high" if len(blocking) > 1 else "moderate" if blocking else "low"

        return CoordinationStatus(
            coordination_state="synchronized" if not blocking else "partial",
            dependent_units=units,
            blocking_units=blocking,
            synchronization_risk=risk,
            recommendations=["review blocking units"] if blocking else ["maintain current coordination"],
        )
