"""dashboard_metric_serializer.py — Serialize dashboard metric contracts to API-safe dicts.

Rules:
- Pure Python. Zero DB, zero ORM, zero FastAPI / HTTP.
- All output is JSON-safe plain dicts / lists.
"""

from __future__ import annotations

from typing import Any

from contracts.dashboard_metric_contracts import (
    AdminIntelligenceDashboard,
    DashboardMetric,
    DashboardMetricGroup,
    RoleDashboardPayload,
)
from services.dashboard_metric_service import DashboardMetricService


class DashboardMetricSerializer:
    """Serialize pre-shaped dashboard metric dicts into API-safe responses."""

    # ── single metric ──────────────────────────────────────────────────────────

    @staticmethod
    def serialize_dashboard_metric(
        metric: DashboardMetric,
        role: str | None = None,
    ) -> dict[str, Any]:
        if role:
            role = role.lower()
            allowed = _clearance_set(role)
            if metric["pdpa_level"] not in allowed:
                return _redacted_metric(metric)
        return dict(metric)

    # ── group ──────────────────────────────────────────────────────────────────

    @staticmethod
    def serialize_metric_group(
        group: DashboardMetricGroup,
        role: str | None = None,
    ) -> dict[str, Any]:
        role = (role or "").lower()
        allowed = _clearance_set(role)
        safe_metrics = [
            m if m["pdpa_level"] in allowed else _redacted_metric(m)
            for m in group["metrics"]
        ]
        return {
            "group_code": group["group_code"],
            "title_i18n_key": group["title_i18n_key"],
            "description_i18n_key": group["description_i18n_key"],
            "metrics": safe_metrics,
            "alerts": group["alerts"],
            "recommended_actions": group["recommended_actions"],
        }

    # ── full payloads ──────────────────────────────────────────────────────────

    @staticmethod
    def serialize_admin_intelligence(
        payload: AdminIntelligenceDashboard,
    ) -> dict[str, Any]:
        return {
            "role": payload["role"],
            "overall_health_score": payload["overall_health_score"],
            "overall_risk_band": payload["overall_risk_band"],
            "last_computed_at": payload["last_computed_at"],
            "groups": [
                DashboardMetricSerializer.serialize_metric_group(g, "admin")
                for g in payload["groups"]
            ],
        }

    @staticmethod
    def serialize_role_payload(
        payload: RoleDashboardPayload,
        role: str | None = None,
    ) -> dict[str, Any]:
        active_role = role or payload["role"]
        return {
            "role": payload["role"],
            "role_label_i18n_key": payload["role_label_i18n_key"],
            "summary": {
                "role": payload["summary"]["role"],
                "role_label_i18n_key": payload["summary"]["role_label_i18n_key"],
                "health_score": payload["summary"]["health_score"],
                "risk_band": payload["summary"]["risk_band"],
                "key_metrics": [
                    DashboardMetricSerializer.serialize_dashboard_metric(m, active_role)
                    for m in payload["summary"]["key_metrics"]
                ],
                "alerts": [dict(a) if isinstance(a, dict) else a for a in payload["summary"]["alerts"]],
                "recommended_actions": (
                    [dict(a) if isinstance(a, dict) else a
                     for a in payload["summary"]["recommended_actions"]]
                ),
                "last_updated": payload["summary"]["last_updated"],
            },
            "groups": [
                DashboardMetricSerializer.serialize_metric_group(g, active_role)
                for g in payload["groups"]
            ],
            "unauthorized": payload["unauthorized"],
        }


# ── internal helpers ───────────────────────────────────────────────────────────


def _clearance_set(role: str) -> set[str]:
    """Return the set of pdpa_level values a *role* can receive."""
    role = role.lower()
    if role in {"admin", "esq_head", "secretary", "dpo"}:
        return {"public", "internal", "confidential", "restricted"}
    if role in {"staff", "teacher", "dept_supervisor", "print_shop", "it"}:
        return {"public", "internal"}
    return {"public"}   # student, unknown


def _redacted_metric(metric: DashboardMetric) -> dict[str, Any]:
    return {
        "metric_code": metric["metric_code"],
        "title_i18n_key": metric["title_i18n_key"],
        "description_i18n_key": metric["description_i18n_key"],
        "value": "[RESTRICTED]",
        "unit": metric["unit"],
        "trend": "unknown",
        "trend_label_i18n_key": "common.unknown",
        "severity": "info",
        "why_it_matters_i18n_key": metric["why_it_matters_i18n_key"],
        "recommended_action_i18n_key": metric["recommended_action_i18n_key"],
        "owner_role": metric["owner_role"],
        "drilldown_route": None,
        "updated_at": metric["updated_at"],
        "pdpa_level": metric["pdpa_level"],
    }
