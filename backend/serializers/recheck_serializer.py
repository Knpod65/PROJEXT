"""
recheck_serializer.py — recheck report serialization helpers.
"""
from typing import Any


class RecheckSerializer:
    """Serializes recheck-related payloads."""

    @staticmethod
    def serialize_recheck_issue(issue: dict[str, Any]) -> dict[str, Any]:
        return {
            "issue": issue.get("issue", ""),
            "severity": issue.get("severity", "warning"),
        }
