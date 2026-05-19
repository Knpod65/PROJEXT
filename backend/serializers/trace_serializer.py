"""
trace_serializer.py — optimization trace event serialization.
"""
from typing import Any


class TraceSerializer:
    """Serializes optimization trace events and summaries."""

    @staticmethod
    def serialize_trace_event(event: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_id": event.get("event_id"),
            "stage": event.get("stage", ""),
            "event_type": event.get("event_type", ""),
            "timestamp": event.get("timestamp", ""),
            "severity": event.get("severity", "info"),
            "detail": event.get("detail", ""),
        }

    @staticmethod
    def serialize_trace_summary(summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": summary.get("session_id"),
            "trace_id": summary.get("trace_id"),
            "generated_at": summary.get("generated_at"),
            "overall_quality_score": summary.get("overall_quality_score", 0.0),
            "traceability_completeness_score": summary.get("traceability_completeness_score", 0.0),
            "events": [TraceSerializer.serialize_trace_event(e) for e in summary.get("events", [])],
            "rejected_alternatives_count": summary.get("rejected_alternatives_count", 0),
        }
