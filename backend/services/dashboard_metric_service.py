"""dashboard_metric_service.py — Pure builder / classifier functions for dashboard metrics.

Rules:
- Pure Python. Zero DB, zero ORM, zero FastAPI, zero HTTP.
- All values are pre-computed by callers; this module only shapes contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from contracts.dashboard_metric_contracts import (
    DashboardMetric,
    DashboardMetricGroup,
    DashboardAlert,
    AdminIntelligenceDashboard,
    validate_metric,
    build_minimal_metric,
    build_minimal_group,
    build_minimal_dashboard,
    build_minimal_payload,
)


class DashboardMetricService:
    """Static builder helpers for dashboard metric contracts."""

    # ── builders ────────────────────────────────────────────────────────────────

    @staticmethod
    def build_metric(
        metric_code: str,
        title_i18n_key: str,
        description_i18n_key: str,
        value: int | float | str,
        unit: str,
        trend: str,
        trend_label_i18n_key: str,
        severity: str,
        why_it_matters_i18n_key: str,
        recommended_action_i18n_key: str,
        owner_role: str,
        drilldown_route: str | None = None,
        updated_at: str | None = None,
        pdpa_level: str = "internal",
    ) -> DashboardMetric:
        return {
            "metric_code": metric_code,
            "title_i18n_key": title_i18n_key,
            "description_i18n_key": description_i18n_key,
            "value": value,
            "unit": unit,
            "trend": trend,
            "trend_label_i18n_key": trend_label_i18n_key,
            "severity": severity,
            "why_it_matters_i18n_key": why_it_matters_i18n_key,
            "recommended_action_i18n_key": recommended_action_i18n_key,
            "owner_role": owner_role,
            "drilldown_route": drilldown_route,
            "updated_at": updated_at,
            "pdpa_level": pdpa_level,
        }

    @staticmethod
    def build_metric_group(
        group_code: str,
        title_i18n_key: str,
        description_i18n_key: str,
        metrics: list[DashboardMetric],
        alerts: list[str] | None = None,
        recommended_actions: list[str] | None = None,
    ) -> DashboardMetricGroup:
        return {
            "group_code": group_code,
            "title_i18n_key": title_i18n_key,
            "description_i18n_key": description_i18n_key,
            "metrics": metrics,
            "alerts": alerts or [],
            "recommended_actions": recommended_actions or [],
        }

    @staticmethod
    def build_alert(
        alert_code: str,
        severity: str,
        title_i18n_key: str,
        body_i18n_key: str,
        metric_codes: list[str],
        pdpa_level: str = "public",
    ) -> DashboardAlert:
        return {
            "alert_code": alert_code,
            "severity": severity,
            "title_i18n_key": title_i18n_key,
            "body_i18n_key": body_i18n_key,
            "metric_codes": metric_codes,
            "pdpa_level": pdpa_level,
        }

    # ── severity classifier ─────────────────────────────────────────────────────

    @staticmethod
    def classify_metric_severity(
        value: int | float,
        thresholds: dict[str, float],
    ) -> str:
        """Classify a numeric value into a severity band.

        Thresholds dict keys (all optional):
          critical — value >= this → 'critical'
          warning  — value >= this → 'warning'
          info     — value >= this → 'info'
        Returns 'unknown' for non-numeric input.
        Returns 'good' when value falls below every threshold.
        """
        try:
            v = float(value)
        except (TypeError, ValueError):
            return "unknown"

        if v >= thresholds.get("critical", float("inf")):
            return "critical"
        if v >= thresholds.get("warning", float("inf")):
            return "warning"
        if v >= thresholds.get("info", float("inf")):
            return "info"
        return "good"

    # ── role filtering ─────────────────────────────────────────────────────────

    @staticmethod
    def filter_metrics_for_role(
        metrics: list[DashboardMetric],
        role: str,
    ) -> list[DashboardMetric]:
        """Drop metrics whose pdpa_level is above this role's clearance.

        Clearance ranking: restricted > confidential > internal > public
        Admin/esq_head/secretary/dpo → all
        Staff/teacher/dept_supervisor → public + internal
        Student → public only
        Print shop → public + internal
        IT → public + internal
        Executive → public + internal + confidential (no restricted)
        """
        role = role.lower()
        if role in {_ADMIN, "esq_head", "secretary", "dpo"}:
            return metrics  # full access

        if _role_gets_internal(role):
            allowed = {"public", "internal"}
        else:
            allowed = {"public"}

        return [m for m in metrics if m["pdpa_level"] in allowed]

    @staticmethod
    def safe_empty_metric(metric_code: str) -> DashboardMetric:
        return build_minimal_metric(
            {
                "metric_code": metric_code,
                "value": 0,
                "severity": "info",
                "pdpa_level": "internal",
            }
        )

    # ── ops-health / pdpa-health helpers ───────────────────────────────────────

    @staticmethod
    def build_ops_health_groups(health: dict) -> list[DashboardMetricGroup]:
        """Convert health_service raw dict into a system-operations group.

        health is expected to carry top-level keys produced by
        HealthService.get_full_health(); the exact shape is not assumed —
        defensively iterate known patterns with .get() fallbacks.
        """
        now = datetime.now(timezone.utc).isoformat()
        metrics: list[DashboardMetric] = []

        # ── API ────────────────────────────────────────────────────────────────
        api_pct = _as_float(health.get("api_uptime_pct"))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="api_uptime_pct",
                title_i18n_key="dashboard.health.apiOk",
                description_i18n_key="dashboard.health.apiOk",
                value=api_pct,
                unit="%",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    api_pct, {"good": 1.0, "info": 0.995, "warning": 0.99, "critical": 0.80}
                ),
                why_it_matters_i18n_key="dashboard.health.apiOk",
                recommended_action_i18n_key="dashboard.actions.checkApi",
                owner_role="it",
                pdpa_level="public",
                updated_at=now,
            )
        )

        # ── DB ────────────────────────────────────────────────────────────────
        db_ok = bool(health.get("db_ok", True))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="db_ok",
                title_i18n_key="dashboard.health.dbOk",
                description_i18n_key="dashboard.health.dbOk",
                value=1.0 if db_ok else 0.0,
                unit="boolean",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity="good" if db_ok else "critical",
                why_it_matters_i18n_key="dashboard.health.dbOk",
                recommended_action_i18n_key="dashboard.actions.restartDb",
                owner_role="it",
                pdpa_level="public",
                updated_at=now,
            )
        )

        # ── Storage ───────────────────────────────────────────────────────────
        storage_pct = _as_float(health.get("storage_usage_pct"))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="storage_usage_pct",
                title_i18n_key="dashboard.health.storagePct",
                description_i18n_key="dashboard.health.storagePct",
                value=storage_pct,
                unit="%",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    storage_pct,
                    {"good": 60.0, "info": 80.0, "warning": 90.0, "critical": 100.0},
                ),
                why_it_matters_i18n_key="dashboard.health.storagePct",
                recommended_action_i18n_key="dashboard.actions.pruneStorage",
                owner_role="it",
                pdpa_level="public",
                updated_at=now,
            )
        )

        return [
            DashboardMetricService.build_metric_group(
                group_code="systemOperations",
                title_i18n_key="dashboard.system.title",
                description_i18n_key="dashboard.system.title",
                metrics=metrics,
            )
        ]

    @staticmethod
    def build_pdpa_health_groups(pdpa_alerts: list[dict]) -> list[DashboardMetricGroup]:
        now = datetime.now(timezone.utc).isoformat()
        alert_cnt = len(pdpa_alerts)
        metrics = [
            DashboardMetricService.build_metric(
                metric_code="pdpa_alert_count_24h",
                title_i18n_key="dashboard.pdpa.alertCount24h",
                description_i18n_key="dashboard.pdpa.alertCount24h",
                value=alert_cnt,
                unit="alerts",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    alert_cnt, {"good": 0.0, "info": 1.0, "warning": 5.0, "critical": 10.0}
                ),
                why_it_matters_i18n_key="dashboard.pdpa.alertCount24h",
                recommended_action_i18n_key="dashboard.actions.reviewPDPALog",
                owner_role="admin",
                pdpa_level="restricted",
                updated_at=now,
            )
        ]
        return [
            DashboardMetricService.build_metric_group(
                group_code="pdpaSecurity",
                title_i18n_key="dashboard.admin.group.pdpaSecurity",
                description_i18n_key="dashboard.admin.group.pdpaSecurity.description",
                metrics=metrics,
            )
        ]


# ── internal helpers ───────────────────────────────────────────────────────────

_ADMIN = "admin"


def _role_gets_internal(role: str) -> bool:
    return role in {
        "staff", "teacher", "dept_supervisor", "print_shop", "it",
        "executive", "esq_head", "secretary",
    }


def _as_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0
