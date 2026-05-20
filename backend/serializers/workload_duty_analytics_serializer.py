"""workload_duty_analytics_serializer.py — response shaping for workload duty analytics."""
from __future__ import annotations

from typing import Any


class WorkloadDutyAnalyticsSerializer:
    """Serialize the workload duty analytics payload as JSON-safe dicts."""

    @staticmethod
    def serialize_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "filters": dict(payload.get("filters") or {}),
            "summary": dict(payload.get("summary") or {}),
            "by_person": [dict(row) for row in payload.get("by_person") or []],
            "daily_series": [dict(row) for row in payload.get("daily_series") or []],
            "time_slot_series": [dict(row) for row in payload.get("time_slot_series") or []],
            "fairness": dict(payload.get("fairness") or {}),
        }
