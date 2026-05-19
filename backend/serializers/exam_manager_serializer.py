"""
exam_manager_serializer.py — exam ownership and manager payloads.
"""
from typing import Any


class ExamManagerSerializer:
    """Serializes exam manager / ownership related responses."""

    @staticmethod
    def serialize_ownership(ownership: dict[str, Any]) -> dict[str, Any]:
        return {
            "section_id": ownership.get("section_id"),
            "owner_id": ownership.get("owner_id"),
            "owner_name": ownership.get("owner_name"),
            "assigned_at": ownership.get("assigned_at"),
        }
