"""dashboard_alert_service.py — Operational dashboard alert foundation.

Provides lightweight alert generation for dashboard intelligence without
requiring full async notification infrastructure.

Rules:
- Pure logic. No DB writes, no email/SMS/LINE.
- Returns alert dicts suitable for dashboard rendering.
- Tolerates missing data — never crashes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DashboardAlertService:
    """Generate operational alerts for dashboard consumption."""

    @staticmethod
    def generate_operational_alerts(
        dashboard_stats: dict | None = None,
        governance_analytics: dict | None = None,
        workload_analytics: dict | None = None,
        optimization_quality: dict | None = None,
        pdpa_alerts: list[dict] | None = None,
        print_queue_size: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate operational alerts from available data sources.

        Returns list of alert dicts with:
        - alert_code: unique identifier
        - severity: info | warning | critical
        - title_i18n_key: translation key for title
        - body_i18n_key: translation key for body
        - metric_codes: list of related metric codes
        - recommended_action_i18n_key: translation key for action
        - timestamp: ISO-8601 timestamp
        """
        alerts: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        # ── Missing Rooms Alert ─────────────────────────────────────────────
        if dashboard_stats:
            unscheduled = int(dashboard_stats.get("unscheduled_sections", 0))
            if unscheduled > 10:
                alerts.append(
                    {
                        "alert_code": "missing_rooms",
                        "severity": "warning",
                        "title_i18n_key": "dashboard.alerts.missingRooms",
                        "body_i18n_key": "dashboard.alerts.missingRooms",
                        "metric_codes": ["unscheduled_sections"],
                        "recommended_action_i18n_key": "dashboard.actions.assignMissingRooms",
                        "timestamp": now,
                    }
                )

        # ── Missing Invigilators Alert ──────────────────────────────────────
        if dashboard_stats:
            missing_invigilators = int(dashboard_stats.get("missing_invigilators", 0))
            if missing_invigilators > 5:
                alerts.append(
                    {
                        "alert_code": "missing_invigilators",
                        "severity": "warning",
                        "title_i18n_key": "dashboard.alerts.missingInvigilators",
                        "body_i18n_key": "dashboard.alerts.missingInvigilators",
                        "metric_codes": ["missing_invigilators"],
                        "recommended_action_i18n_key": "dashboard.actions.reviewSupervisionCoverage",
                        "timestamp": now,
                    }
                )

        # ── Publication Blocked Alert ───────────────────────────────────────
        if governance_analytics:
            blockers = int(governance_analytics.get("blocker_count", 0))
            if blockers > 0:
                alerts.append(
                    {
                        "alert_code": "blocked_publication",
                        "severity": "critical",
                        "title_i18n_key": "dashboard.alerts.blockedPublication",
                        "body_i18n_key": "dashboard.alerts.blockedPublication",
                        "metric_codes": ["blocker_count"],
                        "recommended_action_i18n_key": "dashboard.actions.reviewGovernanceBlockers",
                        "timestamp": now,
                    }
                )

        # ── Optimization Hard Fail Alert ────────────────────────────────────
        if optimization_quality:
            quality_score = float(optimization_quality.get("average_score", 100.0))
            if quality_score < 40.0:
                alerts.append(
                    {
                        "alert_code": "optimization_hard_fail",
                        "severity": "critical",
                        "title_i18n_key": "dashboard.alerts.optimizationHardFail",
                        "body_i18n_key": "dashboard.alerts.optimizationHardFail",
                        "metric_codes": ["optimization_quality_avg"],
                        "recommended_action_i18n_key": "dashboard.actions.reviewOptimizerTrace",
                        "timestamp": now,
                    }
                )

        # ── PDPA Suspicious Activity Alert ──────────────────────────────────
        if pdpa_alerts and len(pdpa_alerts) > 5:
            alerts.append(
                {
                    "alert_code": "pdpa_suspicious_activity",
                    "severity": "critical",
                    "title_i18n_key": "dashboard.alerts.pdpaAlert",
                    "body_i18n_key": "dashboard.alerts.pdpaAlert",
                    "metric_codes": ["pdpa_alert_count_24h"],
                    "recommended_action_i18n_key": "dashboard.actions.reviewPDPALog",
                    "timestamp": now,
                }
            )

        # ── Print Queue Overload Alert ──────────────────────────────────────
        if print_queue_size is not None and print_queue_size > 50:
            alerts.append(
                {
                    "alert_code": "print_queue_overload",
                    "severity": "warning",
                    "title_i18n_key": "dashboard.alerts.printQueueOverload",
                    "body_i18n_key": "dashboard.alerts.printQueueOverload",
                    "metric_codes": ["print_queue_size"],
                    "recommended_action_i18n_key": "dashboard.actions.checkPrintQueue",
                    "timestamp": now,
                }
            )

        # ── Workload Imbalance Alert ────────────────────────────────────────
        if workload_analytics:
            imbalance = float(workload_analytics.get("imbalance_score", 0.0))
            if imbalance > 0.5:
                alerts.append(
                    {
                        "alert_code": "workload_imbalance",
                        "severity": "warning",
                        "title_i18n_key": "dashboard.alerts.workloadImbalance",
                        "body_i18n_key": "dashboard.alerts.workloadImbalance",
                        "metric_codes": ["staff_imbalance_score"],
                        "recommended_action_i18n_key": "dashboard.actions.reviewSupervisionCoverage",
                        "timestamp": now,
                    }
                )

        return alerts

    @staticmethod
    def generate_governance_pending_alert(
        pending_approvals: int,
        hours_threshold: int = 48,
    ) -> dict[str, Any] | None:
        """Generate alert if governance approvals pending too long."""
        if pending_approvals > 0:
            return {
                "alert_code": "governance_pending_too_long",
                "severity": "warning",
                "title_i18n_key": "dashboard.alerts.governancePendingTooLong",
                "body_i18n_key": "dashboard.alerts.governancePendingTooLong",
                "metric_codes": ["pending_approvals"],
                "recommended_action_i18n_key": "dashboard.actions.reviewGovernanceBlockers",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return None

    @staticmethod
    def generate_health_alerts(
        backend_ok: bool = True,
        db_ok: bool = True,
        storage_usage_pct: float | None = None,
        warning_count: int | None = None,
        optimization_runtime_ms: int | None = None,
    ) -> list[dict[str, Any]]:
        """Generate system-health alerts for operational monitoring."""
        alerts: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        if not backend_ok:
            alerts.append({
                "alert_code": "backend_degraded",
                "category": "system-health",
                "severity": "critical",
                "title_i18n_key": "dashboard.alerts.systemDegraded",
                "description_key": "dashboard.alerts.backendDegraded",
                "recommended_action_key": "dashboard.actions.checkBackendLogs",
                "owner_role": "admin",
                "source": "health_service",
                "timestamp": now,
            })

        if not db_ok:
            alerts.append({
                "alert_code": "db_unavailable",
                "category": "system-health",
                "severity": "critical",
                "title_i18n_key": "dashboard.alerts.dbUnavailable",
                "description_key": "dashboard.alerts.dbUnavailable",
                "recommended_action_key": "dashboard.actions.contactIT",
                "owner_role": "admin",
                "source": "health_service",
                "timestamp": now,
            })

        if storage_usage_pct is not None and storage_usage_pct > 85:
            alerts.append({
                "alert_code": "storage_high",
                "category": "system-health",
                "severity": "high",
                "title_i18n_key": "dashboard.alerts.storageHigh",
                "description_key": "dashboard.alerts.storageHigh",
                "recommended_action_key": "dashboard.actions.reviewStorage",
                "owner_role": "admin",
                "source": "health_service",
                "actual_value": storage_usage_pct,
                "threshold_value": 85,
                "timestamp": now,
            })

        if warning_count is not None and warning_count > 20:
            alerts.append({
                "alert_code": "warning_count_high",
                "category": "system-health",
                "severity": "medium",
                "title_i18n_key": "dashboard.alerts.warningCountHigh",
                "description_key": "dashboard.alerts.warningCountHigh",
                "recommended_action_key": "dashboard.actions.reviewWarnings",
                "owner_role": "admin",
                "source": "dashboard_intelligence",
                "actual_value": warning_count,
                "threshold_value": 20,
                "timestamp": now,
            })

        if optimization_runtime_ms is not None and optimization_runtime_ms > 30000:
            alerts.append({
                "alert_code": "optimization_runtime_warning",
                "category": "system-health",
                "severity": "medium",
                "title_i18n_key": "dashboard.alerts.optimizationRuntimeWarning",
                "description_key": "dashboard.alerts.optimizationRuntimeWarning",
                "recommended_action_key": "dashboard.actions.reviewOptimization",
                "owner_role": "admin",
                "source": "optimization_service",
                "actual_value": optimization_runtime_ms,
                "threshold_value": 30000,
                "timestamp": now,
            })

        return alerts

