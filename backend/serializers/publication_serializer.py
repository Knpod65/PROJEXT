"""
publication_serializer.py — publication readiness and blocker serialization.
"""
from typing import Any


class PublicationSerializer:
    """Serializes publication readiness responses."""

    @staticmethod
    def serialize_readiness(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "can_publish": result.get("can_publish", False),
            "risk_score": result.get("risk_score", 0.0),
            "blockers": result.get("blockers", []),
            "warnings": result.get("warnings", []),
            "derived_schedule_state": result.get("derived_schedule_state", ""),
            "valid_next_states": result.get("valid_next_states", []),
            "session_status": result.get("session_status", ""),
        }

    @staticmethod
    def serialize_blocker(blocker: dict[str, Any]) -> dict[str, Any]:
        return {
            "code": blocker.get("code", ""),
            "message": blocker.get("message", ""),
            "severity": blocker.get("severity", "warning"),
        }
