"""
lifecycle_serializer.py — schedule lifecycle and transition serialization.
"""
from typing import Any


class LifecycleSerializer:
    """Serializes schedule lifecycle and transition responses."""

    @staticmethod
    def serialize_lifecycle_event(event: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": event.get("id"),
            "event_type": event.get("event_type", ""),
            "timestamp": event.get("timestamp", ""),
            "detail": event.get("detail", ""),
        }

    @staticmethod
    def serialize_transition_result(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed": result.get("allowed", False),
            "reason": result.get("reason", ""),
            "blockers": result.get("blockers", []),
        }

    @staticmethod
    def serialize_capability_matrix(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "can_sign": result.get("can_sign", False),
            "can_reject": result.get("can_reject", False),
            "can_open_swap": result.get("can_open_swap", False),
            "can_publish": result.get("can_publish", False),
            "blocker_codes": result.get("blocker_codes", []),
        }
