"""
dashboard_serializer.py — dashboard response shaping.

Owns:
- dashboard stats shaping
- analytics shaping
- role-based field filtering
- PDPA-safe response filtering
"""
from typing import Any, Optional


class DashboardSerializer:
    """Serializes dashboard responses with role-based filtering."""

    @staticmethod
    def serialize_dashboard_stats(stats: dict[str, Any], user_role: str) -> dict[str, Any]:
        result = {
            "total_sections": stats.get("total_sections", 0),
            "total_students": stats.get("total_students", 0),
            "total_sheets": stats.get("total_sheets", 0),
            "total_teachers": stats.get("total_teachers", 0),
            "scheduled_sections": stats.get("scheduled_sections", 0),
            "unscheduled_sections": stats.get("unscheduled_sections", 0),
            "rooms_in_use": stats.get("rooms_in_use", 0),
            "copy_cost": stats.get("copy_cost", 0.0),
        }
        if user_role == "admin":
            result["recent_logs"] = stats.get("recent_logs", [])
        return result

    @staticmethod
    def serialize_analytics(data: dict[str, Any]) -> dict[str, Any]:
        return {
            "submission_status": data.get("submission_status", {}),
            "teacher_stats": data.get("teacher_stats", {}),
            "supervision_stats": data.get("supervision_stats", {}),
            "swap_status": data.get("swap_status", {}),
            "copy_per_room": data.get("copy_per_room", []),
            "checkin_by_date": data.get("checkin_by_date", []),
        }
