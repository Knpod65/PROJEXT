"""admin_dashboard_intelligence_service.py — Admin Intelligence Dashboard assembly layer.

Owns:
- 10 Admin metric groups (examOperations, optimizationQuality, … systemOperations)
- Overall health score computation from executive projection
- Safe fallback when any data source is unavailable

Rules:
- Pure logic. Zero direct DB access in this file.
- All data is pre-computed by callers and injected as dicts.
- Tolerates missing/malformed input — never raises, returns fallback groups.
- No raw PII in output.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from contracts.dashboard_metric_contracts import (
    AdminIntelligenceDashboard,
    DashboardMetric,
    DashboardMetricGroup,
)
from services.dashboard_metric_service import DashboardMetricService


# ── i18n-key constants ─────────────────────────────────────────────────────────

_KEYS = {
    "examOperations": {
        "title": "dashboard.admin.group.examOperations",
        "desc":  "dashboard.admin.group.examOperations.description",
        "unscheduledSections": {
            "title":   "dashboard.metrics.examOperations.unscheduledSections",
            "desc":    "dashboard.metrics.examOperations.unscheduledSections.description",
            "why":     "dashboard.metrics.examOperations.unscheduledSections.whyItMatters",
            "action":  "dashboard.metrics.examOperations.unscheduledSections.action",
        },
    },
    "optimizationQuality": {
        "title": "dashboard.admin.group.optimizationQuality",
        "desc":  "dashboard.admin.group.optimizationQuality.description",
    },
    "governanceApproval": {
        "title": "dashboard.admin.group.governanceApproval",
        "desc":  "dashboard.admin.group.governanceApproval.description",
    },
    "staffWorkload": {
        "title": "dashboard.admin.group.staffWorkload",
        "desc":  "dashboard.admin.group.staffWorkload.description",
    },
    "roomCapacity": {
        "title": "dashboard.admin.group.roomCapacity",
        "desc":  "dashboard.admin.group.roomCapacity.description",
    },
    "teacherSubmission": {
        "title": "dashboard.admin.group.teacherSubmission",
        "desc":  "dashboard.admin.group.teacherSubmission.description",
    },
    "printExport": {
        "title": "dashboard.admin.group.printExport",
        "desc":  "dashboard.admin.group.printExport.description",
    },
    "qrPickup": {
        "title": "dashboard.admin.group.qrPickup",
        "desc":  "dashboard.admin.group.qrPickup.description",
    },
    "pdpaSecurity": {
        "title": "dashboard.admin.group.pdpaSecurity",
        "desc":  "dashboard.admin.group.pdpaSecurity.description",
    },
    "systemOperations": {
        "title": "dashboard.system.title",
        "desc":  "dashboard.system.title",
    },
}

_ALL_GROUP_CODES = list(_KEYS.keys())


# ── core ───────────────────────────────────────────────────────────────────────

class AdminDashboardIntelligenceService:
    """Assemble the Admin Intelligence Dashboard from pre-computed data dicts."""

    @staticmethod
    def build_admin_intelligence_dashboard(
        db: Any = None,
        user: Any = None,
        semester: str = "2",
        academic_year: str = "2568",
        *,
        dashboard_stats: dict | None = None,
        analytics: dict | None = None,
        executive_summary: dict | None = None,
        governance_analytics: dict | None = None,
        workload_analytics: dict | None = None,
        room_analytics: dict | None = None,
        pdpa_alerts: list[dict] | None = None,
        health: dict | None = None,
    ) -> AdminIntelligenceDashboard:
        """Build the complete Admin Intelligence Dashboard.

        All data inputs are optional. If a source is absent or raises during
        population, the corresponding group falls back to an empty metric list
        with a ``data_unavailable`` alert.
        """
        now = datetime.now(timezone.utc).isoformat()

        groups: list[DashboardMetricGroup] = []

        groups.append(_build_exam_ops_group(dashboard_stats, now))
        groups.append(_build_optimization_quality_group(executive_summary, now))
        groups.append(_build_governance_group(governance_analytics, now))
        groups.append(_build_staff_workload_group(workload_analytics, now))
        groups.append(_build_room_capacity_group(room_analytics, now))
        groups.append(_build_teacher_submission_group(analytics, now))
        groups.append(_build_print_export_group(now))
        groups.append(_build_qr_pickup_group(now))
        groups.append(_build_pdpa_security_group(pdpa_alerts or [], now))
        groups.append(_build_system_ops_group(health, now))

        # --- overall health score from executive projection or default -----------
        overall_score: float | None = None
        overall_band: str | None = "green"
        if executive_summary:
            overall_score = _safe_float(executive_summary.get("overall_health_score"))
            raw_band = executive_summary.get("risk_band", "green")
            if raw_band in ("green", "amber", "red"):
                overall_band = raw_band

        return AdminIntelligenceDashboard(
            role="admin",
            overall_health_score=overall_score,
            overall_risk_band=overall_band,
            last_computed_at=now,
            groups=groups,
        )


# ── group builders ─────────────────────────────────────────────────────────────

def _build_exam_ops_group(
    stats: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["examOperations"]
    metrics: list[DashboardMetric] = []
    if stats:
        unscheduled = int(_safe_float(stats.get("unscheduled_sections", 0)))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="unscheduled_sections",
                title_i18n_key=k["unscheduledSections"]["title"],
                description_i18n_key=k["unscheduledSections"]["desc"],
                value=unscheduled,
                unit="sections",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    unscheduled, {"good": 0.0, "info": 1.0, "warning": 10.0, "critical": 50.0}
                ),
                why_it_matters_i18n_key=k["unscheduledSections"]["why"],
                recommended_action_i18n_key=k["unscheduledSections"]["action"],
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        )
        scheduled = int(_safe_float(stats.get("scheduled_sections", 0)))
        metrics.append(
            _mk("scheduled_sections",
                "dashboard.metrics.examOperations.scheduledSections",
                "dashboard.metrics.examOperations.scheduledSections.description",
                scheduled, "sections", "common.unknown", "good", "internal", now)
        )
        room_col = int(_safe_float(stats.get("rooms_in_use", 0)))
        metrics.append(
            _mk("rooms_in_use",
                "dashboard.metrics.examOperations.roomsInUse",
                "dashboard.metrics.examOperations.roomsInUse.description",
                room_col, "rooms", "common.unknown", "info", "public", now)
        )
    alerts = ["data_unavailable"] if not metrics else []
    return DashboardMetricService.build_metric_group(
        group_code="examOperations",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
        alerts=alerts,
    )


def _build_optimization_quality_group(
    exec_summary: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["optimizationQuality"]
    metrics: list[DashboardMetric] = []
    if exec_summary:
        score = _safe_float(exec_summary.get("optimization_quality_avg", 0.0))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="optimization_quality_avg",
                title_i18n_key="dashboard.metrics.optimization.qualityScore",
                description_i18n_key="dashboard.metrics.optimization.qualityScore.description",
                value=round(score, 1),
                unit="score",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    score, {"good": 80.0, "info": 60.0, "warning": 40.0, "critical": 20.0}
                ),
                why_it_matters_i18n_key="dashboard.metrics.optimization.qualityScore.why",
                recommended_action_i18n_key="dashboard.actions.reviewOptimizerTrace",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        )
    return DashboardMetricService.build_metric_group(
        group_code="optimizationQuality",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
    )


def _build_governance_group(
    governance_analytics: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["governanceApproval"]
    metrics: list[DashboardMetric] = []
    if governance_analytics:
        blockers = int(_safe_float(governance_analytics.get("blocker_count", 0)))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="blocker_count",
                title_i18n_key="dashboard.metrics.governance.blockerCount",
                description_i18n_key="dashboard.metrics.governance.blockerCount.description",
                value=blockers,
                unit="blockers",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    blockers, {"good": 0.0, "info": 1.0, "warning": 5.0, "critical": 20.0}
                ),
                why_it_matters_i18n_key="dashboard.metrics.governance.blockerCount.why",
                recommended_action_i18n_key="dashboard.actions.reviewGovernanceBlockers",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        )
        pending = int(_safe_float(governance_analytics.get("pending_approvals", 0)))
        metrics.append(
            _mk("pending_approvals",
                "dashboard.metrics.governance.pendingApprovals",
                "dashboard.metrics.governance.pendingApprovals.description",
                pending, "approvals", "common.unknown", "info", "internal", now)
        )
    return DashboardMetricService.build_metric_group(
        group_code="governanceApproval",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
    )


def _build_staff_workload_group(
    workload_analytics: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["staffWorkload"]
    metrics: list[DashboardMetric] = []
    if workload_analytics:
        imbalance = _safe_float(workload_analytics.get("imbalance_score", 0.0))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="staff_imbalance_score",
                title_i18n_key="dashboard.metrics.workload.imbalanceScore",
                description_i18n_key="dashboard.metrics.workload.imbalanceScore.description",
                value=round(imbalance, 3),
                unit="score",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    imbalance, {"good": 0.15, "info": 0.30, "warning": 0.50, "critical": 0.80}
                ),
                why_it_matters_i18n_key="dashboard.metrics.workload.imbalanceScore.why",
                recommended_action_i18n_key="dashboard.actions.reviewSupervisionCoverage",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        )
    return DashboardMetricService.build_metric_group(
        group_code="staffWorkload",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
    )


def _build_room_capacity_group(
    room_analytics: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["roomCapacity"]
    metrics: list[DashboardMetric] = []
    if room_analytics:
        utilization = _safe_float(room_analytics.get("average_utilization", 0.0))
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="room_utilization_score",
                title_i18n_key="dashboard.metrics.rooms.utilizationScore",
                description_i18n_key="dashboard.metrics.rooms.utilizationScore.description",
                value=round(utilization, 1),
                unit="%",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    utilization, {"good": 80.0, "info": 60.0, "warning": 40.0, "critical": 20.0}
                ),
                why_it_matters_i18n_key="dashboard.metrics.rooms.utilizationScore.why",
                recommended_action_i18n_key="dashboard.actions.assignMissingRooms",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        )
    return DashboardMetricService.build_metric_group(
        group_code="roomCapacity",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
    )


def _build_teacher_submission_group(
    analytics: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["teacherSubmission"]
    metrics: list[DashboardMetric] = []
    if analytics and "teacher_stats" in analytics:
        ts = analytics["teacher_stats"]
        total = int(_safe_float(ts.get("submitted", 0))) + int(_safe_float(ts.get("not_submitted", 0)))
        submitted = int(_safe_float(ts.get("submitted", 0)))
        rate = (submitted / total * 100.0) if total > 0 else 0.0
        metrics.append(
            DashboardMetricService.build_metric(
                metric_code="submission_rate",
                title_i18n_key="dashboard.metrics.submissions.submissionRate",
                description_i18n_key="dashboard.metrics.submissions.submissionRate.description",
                value=round(rate, 1),
                unit="%",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity=DashboardMetricService.classify_metric_severity(
                    rate, {"good": 95.0, "info": 80.0, "warning": 60.0, "critical": 40.0}
                ),
                why_it_matters_i18n_key="dashboard.metrics.submissions.submissionRate.why",
                recommended_action_i18n_key="dashboard.actions.checkPrintQueue",
                owner_role="admin",
                pdpa_level="public",
                updated_at=now,
            )
        )
    return DashboardMetricService.build_metric_group(
        group_code="teacherSubmission",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=metrics,
    )


def _build_print_export_group(
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["printExport"]
    # Stub — print batch data will be wired once export_service exposes a dict
    return DashboardMetricService.build_metric_group(
        group_code="printExport",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=[
            DashboardMetricService.build_metric(
                metric_code="print_queue_size",
                title_i18n_key="dashboard.metrics.print.queueSize",
                description_i18n_key="dashboard.metrics.print.queueSize.description",
                value=0,
                unit="items",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity="info",
                why_it_matters_i18n_key="dashboard.metrics.print.queueSize.why",
                recommended_action_i18n_key="dashboard.actions.checkPrintQueue",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        ],
    )


def _build_qr_pickup_group(
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["qrPickup"]
    return DashboardMetricService.build_metric_group(
        group_code="qrPickup",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=[
            DashboardMetricService.build_metric(
                metric_code="qr_redeems_24h",
                title_i18n_key="dashboard.metrics.qr.redeems24h",
                description_i18n_key="dashboard.metrics.qr.redeems24h.description",
                value=0,
                unit="scans",
                trend="unknown",
                trend_label_i18n_key="common.unknown",
                severity="info",
                why_it_matters_i18n_key="dashboard.metrics.qr.redeems24h.why",
                recommended_action_i18n_key="dashboard.actions.checkPrintQueue",
                owner_role="admin",
                pdpa_level="internal",
                updated_at=now,
            )
        ],
    )


def _build_pdpa_security_group(
    pdpa_alerts: list[dict],
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["pdpaSecurity"]
    alert_cnt = len(pdpa_alerts)
    metric = DashboardMetricService.build_metric(
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
    return DashboardMetricService.build_metric_group(
        group_code="pdpaSecurity",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=[metric],
    )


def _build_system_ops_group(
    health: dict | None,
    now: str,
) -> DashboardMetricGroup:
    k = _KEYS["systemOperations"]
    groups_from_health = DashboardMetricService.build_ops_health_groups(health or {})
    if groups_from_health:
        return groups_from_health[0]
    return DashboardMetricService.build_metric_group(
        group_code="systemOperations",
        title_i18n_key=k["title"],
        description_i18n_key=k["desc"],
        metrics=[
            DashboardMetricService.safe_empty_metric("api_uptime"),
            DashboardMetricService.safe_empty_metric("db_connection"),
            DashboardMetricService.safe_empty_metric("storage_usage"),
        ],
    )


# ── helpers ────────────────────────────────────────────────────────────────────

def _mk(
    code: str,
    title_key: str,
    desc_key: str,
    value: int | float | str,
    unit: str,
    trend_label_key: str,
    severity: str,
    pdpa_level: str,
    updated_at: str,
    **kwargs: Any,
) -> DashboardMetric:
    return DashboardMetricService.build_metric(
        metric_code=code,
        title_i18n_key=title_key,
        description_i18n_key=desc_key,
        value=value,
        unit=unit,
        trend="unknown",
        trend_label_i18n_key=trend_label_key,
        severity=severity,
        why_it_matters_i18n_key=kwargs.get("why_it_matters_i18n_key", title_key),
        recommended_action_i18n_key=kwargs.get("recommended_action_i18n_key", ""),
        owner_role="admin",
        pdpa_level=pdpa_level,
        updated_at=updated_at,
    )


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default
