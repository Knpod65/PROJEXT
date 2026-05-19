"""
analytics_serializer.py — analytics response shaping.

Owns:
- metric response shaping
- executive summary shaping
- trace response shaping
- PDPA-safe response filtering
"""
from typing import Any, Optional


class AnalyticsSerializer:
    """Serializes analytics responses with PDPA-safe filtering."""

    @staticmethod
    def serialize_metric(metric: dict[str, Any]) -> dict[str, Any]:
        return {
            "metric_code": metric.get("metric_code", ""),
            "name": metric.get("name", ""),
            "category": metric.get("category", ""),
            "description": metric.get("description", ""),
            "unit": metric.get("unit", ""),
        }

    @staticmethod
    def serialize_metric_list(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [AnalyticsSerializer.serialize_metric(m) for m in metrics]

    @staticmethod
    def serialize_metric_raw(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Pass-through for backward compatibility."""
        return metrics

    @staticmethod
    def serialize_executive_summary(summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "overall_health_score": summary.get("overall_health_score", 0.0),
            "risk_band": summary.get("risk_band", "red"),
            "optimization_quality_avg": summary.get("optimization_quality_avg", 0.0),
            "governance_blocker_count": summary.get("governance_blocker_count", 0),
            "publication_ready_count": summary.get("publication_ready_count", 0),
            "workload_balance_score": summary.get("workload_balance_score", 0.0),
            "room_utilization_score": summary.get("room_utilization_score", 0.0),
            "pdpa_alert_count": summary.get("pdpa_alert_count", 0),
            "top_risks": summary.get("top_risks", []),
            "recommended_actions": summary.get("recommended_actions", []),
        }

    @staticmethod
    def serialize_trace(trace: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": trace.get("session_id"),
            "trace_id": trace.get("trace_id"),
            "generated_at": trace.get("generated_at"),
            "overall_quality_score": trace.get("overall_quality_score", 0.0),
            "traceability_completeness_score": trace.get("traceability_completeness_score", 0.0),
            "candidates": trace.get("candidates", []),
            "constraint_hits": trace.get("constraint_hits", []),
            "events": trace.get("events", []),
            "rejected_alternatives_count": trace.get("rejected_alternatives_count", 0),
            "recheck_issues": trace.get("recheck_issues", []),
            "quality_note": trace.get("quality_note", ""),
        }

    @staticmethod
    def serialize_governance_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "id": e.get("id"),
                "actor": e.get("actor", "system"),
                "action": e.get("action", ""),
                "timestamp": e.get("timestamp", ""),
                "detail": e.get("detail", ""),
            }
            for e in events
        ]

    @staticmethod
    def serialize_lifecycle_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "id": e.get("id"),
                "event_type": e.get("event_type", ""),
                "timestamp": e.get("timestamp", ""),
                "detail": e.get("detail", ""),
            }
            for e in events
        ]

    @staticmethod
    def filter_pii_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
        """Remove any PII fields from aggregate summary."""
        pii_keys = {"email", "phone", "mobile", "address", "id_card", "ip_address"}
        return {k: v for k, v in summary.items() if k.lower() not in pii_keys}
