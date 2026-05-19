"""
governance_serializer.py — governance response shaping.

Owns:
- governance report shaping
- publication readiness shaping
- capability shaping
- executive risk shaping
"""
from typing import Any


class GovernanceSerializer:
    """Serializes governance responses."""

    @staticmethod
    def serialize_governance_report(report: dict[str, Any]) -> dict[str, Any]:
        return {
            "governance": report.get("governance", {}),
            "quality_breakdown": report.get("quality_breakdown", {}),
            "severity_summary": report.get("severity_summary", {}),
            "derived_schedule_state": report.get("derived_schedule_state", ""),
            "valid_next_states": report.get("valid_next_states", []),
            "session_status": report.get("session_status", ""),
        }

    @staticmethod
    def serialize_publication_readiness(result: dict[str, Any]) -> dict[str, Any]:
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
    def serialize_capabilities(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "can_sign": result.get("can_sign", False),
            "can_reject": result.get("can_reject", False),
            "can_open_swap": result.get("can_open_swap", False),
            "can_publish": result.get("can_publish", False),
            "blocker_codes": result.get("blocker_codes", []),
        }

    @staticmethod
    def serialize_transition_check(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed": result.get("allowed", False),
            "reason": result.get("reason", ""),
            "blockers": result.get("blockers", []),
        }

    @staticmethod
    def serialize_executive_risk(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "risk_score": result.get("risk_score", 0.0),
            "risk_band": result.get("risk_band", "red"),
            "top_risks": result.get("top_risks", []),
            "recommended_actions": result.get("recommended_actions", []),
        }
