"""unit_context_service.py — Centralized faculty/unit context resolution.

Rules:
- Additive only
- Safe fallback to default faculty (POL)
- No DB schema change required
- Backend is source of truth
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class UnitContext:
    unit_code: str
    unit_name_en: str
    unit_name_th: str
    faculty_code: str
    scope_level: str = "faculty"
    is_default: bool = False
    source: str = "default"


DEFAULT_UNIT = UnitContext(
    unit_code="POL",
    unit_name_en="Faculty of Political Science and Public Administration",
    unit_name_th="คณะรัฐศาสตร์และรัฐประศาสนศาสตร์",
    faculty_code="POL",
    is_default=True,
    source="default",
)


class UnitContextService:
    @staticmethod
    def get_default_unit_context() -> UnitContext:
        return DEFAULT_UNIT

    @staticmethod
    def resolve_unit_context(
        user: Any | None = None,
        requested_unit_code: str | None = None,
    ) -> UnitContext:
        """Resolve unit context with safe fallback."""
        if requested_unit_code:
            # In real impl this would check permissions
            return UnitContext(
                unit_code=requested_unit_code,
                unit_name_en=requested_unit_code,
                unit_name_th=requested_unit_code,
                faculty_code=requested_unit_code,
                source="requested",
            )
        return DEFAULT_UNIT

    @staticmethod
    def ensure_user_can_access_unit(user: Any | None, context: UnitContext) -> bool:
        """Placeholder permission check."""
        return True  # Will be replaced by real permission logic in D5

    @staticmethod
    def serialize_unit_context(context: UnitContext) -> dict[str, Any]:
        return {
            "unit_code": context.unit_code,
            "unit_name_en": context.unit_name_en,
            "unit_name_th": context.unit_name_th,
            "faculty_code": context.faculty_code,
            "is_default": context.is_default,
        }
