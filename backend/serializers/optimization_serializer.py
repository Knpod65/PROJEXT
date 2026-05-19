"""
optimization_serializer.py — optimization result and quality serialization.
"""
from typing import Any


class OptimizationSerializer:
    """Serializes optimizer and trace results."""

    @staticmethod
    def serialize_optimizer_result(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": result.get("session_id"),
            "overall_quality_score": result.get("overall_quality_score", 0.0),
            "traceability_completeness_score": result.get("traceability_completeness_score", 0.0),
            "candidates": result.get("candidates", []),
            "constraint_hits": result.get("constraint_hits", []),
            "quality_note": result.get("quality_note", ""),
        }

    @staticmethod
    def serialize_recheck_report(report: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": report.get("status", "UNKNOWN"),
            "summary": report.get("summary", {}),
            "hard_fail_count": report.get("hard_fail_count", 0),
            "issues": report.get("issues", []),
        }
