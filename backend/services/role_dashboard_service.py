"""role_dashboard_service.py — Role-specific dashboard builders.

Each builder returns a (summary, groups) tuple. The factory dispatches
to the correct builder based on role string.

Rules:
- Pure logic. No DB, no ORM, no HTTP.
- PDPA-aware: builders respect the clearance table in the metrics model doc.
- Tolerates absent context — returns safe stub metrics rather than raising.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from contracts.dashboard_metric_contracts import (
    DashboardMetric,
    DashboardMetricGroup,
    DashboardRoleSummary,
    RoleDashboardPayload,
)
from services.dashboard_metric_service import DashboardMetricService


# ── private helpers ───────────────────────────────────────────────────────────

def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _safe_get(ctx: dict, key: str) -> Any:
    return ctx.get(key) if ctx else None


def _sev(
    value: int | float,
    good: float, info: float, warning: float,
    *,
    inverse: bool = False,
) -> str:
    """Return severity band for a numeric value against thresholds."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if inverse:
        if v <= good:   return "good"
        if v <= info:   return "info"
        if v <= warning: return "warning"
        return "critical"
    if v >= warning:  return "critical"
    if v >= info:     return "warning"
    if v >= good:     return "info"
    return "good"


def _metric(
    code: str,
    title_k: str, desc_k: str,
    value: int | float | str,
    unit: str, severity: str,
    owner: str, pdpa: str,
    now: str,
    why_k: str | None = None,
    action_k: str = "",
) -> DashboardMetric:
    return DashboardMetricService.build_metric(
        metric_code=code,
        title_i18n_key=title_k,
        description_i18n_key=desc_k,
        value=value,
        unit=unit,
        trend="unknown",
        trend_label_i18n_key="common.unknown",
        severity=severity,
        why_it_matters_i18n_key=why_k or title_k,
        recommended_action_i18n_key=action_k,
        owner_role=owner,
        pdpa_level=pdpa,
        updated_at=now,
    )


def _group(
    code: str, title_k: str, desc_k: str,
    metrics: list[DashboardMetric],
) -> DashboardMetricGroup:
    return DashboardMetricService.build_metric_group(
        group_code=code,
        title_i18n_key=title_k,
        description_i18n_key=desc_k,
        metrics=metrics,
    )


def _empty_summary(
    role: str, metrics: list[DashboardMetric], now: str
) -> DashboardRoleSummary:
    return DashboardRoleSummary(
        role=role,
        role_label_i18n_key=f"dashboard.role.{role}",
        health_score=None,
        risk_band=None,
        key_metrics=metrics,
        alerts=[],
        recommended_actions=[],
        last_updated=now,
    )


# ── factory ───────────────────────────────────────────────────────────────────

class RoleDashboardService:
    """Dispatch to the role-specific builder."""

    @staticmethod
    def build_role_dashboard(
        role: str,
        context: dict[str, Any] | None = None,
    ) -> RoleDashboardPayload:
        role_key = role.lower()

        # Admin has a full 10-group intelligence dashboard; wrap into RoleDashboardPayload
        if role_key == "admin":
            ctx = context or {}
            try:
                from services.admin_dashboard_intelligence_service import (
                    AdminDashboardIntelligenceService,
                )
                admin_dash = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
                    db=ctx.get("db"),
                    user=ctx.get("user"),
                    semester=ctx.get("semester", "2"),
                    academic_year=ctx.get("academic_year", "2568"),
                )
                overall = admin_dash.get("overall_health_score")
                band = admin_dash.get("overall_risk_band", "green")
                groups = [g for g in admin_dash.get("groups", [])]
                summary = DashboardRoleSummary(
                    role="admin",
                    role_label_i18n_key="dashboard.role.admin",
                    health_score=overall,
                    risk_band=band,
                    key_metrics=[
                        m for g in groups for m in g.get("metrics", [])[:3]
                    ],
                    alerts=[],
                    recommended_actions=[],
                    last_updated=admin_dash.get("last_computed_at"),
                )
                return RoleDashboardPayload(
                    role="admin",
                    role_label_i18n_key="dashboard.role.admin",
                    summary=summary,
                    groups=groups,
                    unauthorized=False,
                )
            except Exception:
                pass  # fall through to _BUILDERS / unauthorized

        builder = _BUILDERS.get(role_key)
        if builder is None:
            return _build_unauthorized(role)

        from policies.dashboard_metric_policy import DashboardMetricPolicy
        try:
            DashboardMetricPolicy.authorize_role_dashboard_access(role_key)
        except ValueError:
            return _build_unauthorized(role)

        ctx = context or {}
        try:
            summary, groups = builder(ctx)
        except Exception:
            summary, groups = _build_fallback(role_key)

        return RoleDashboardPayload(
            role=role_key,
            role_label_i18n_key=f"dashboard.role.{role_key}",
            summary=summary,
            groups=groups,
            unauthorized=False,
        )


# ── individual builders ─────────────────────────────────────────────────────────

def _build_fallback(
    role: str,
) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    summary = _build_empty_summary(role)
    return summary, []


def _build_empty_summary(role: str) -> DashboardRoleSummary:
    return DashboardRoleSummary(
        role=role,
        role_label_i18n_key=f"dashboard.role.{role}",
        health_score=None,
        risk_band=None,
        key_metrics=[],
        alerts=[],
        recommended_actions=[],
        last_updated=None,
    )


# ── staff ─────────────────────────────────────────────────────────────────────

def _build_staff(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    groups: list[DashboardMetricGroup] = []
    stats = _safe_get(ctx, "dashboard_stats")

    supervision_count = int(_safe_float((stats or {}).get("total_teachers", 0)))
    metrics: list[DashboardMetric] = [
        _metric(
            code="active_invigilations", title_k="dashboard.metrics.role.staff.activeInvigilations",
            desc_k="dashboard.metrics.role.staff.activeInvigilations.description",
            value=supervision_count, unit="assignments", severity=_sev(supervision_count, 0, 5, 20),
            owner="staff", pdpa="public", now=now,
        ),
        _metric(
            code="upcoming_blocks", title_k="dashboard.metrics.role.staff.upcomingBlocks",
            desc_k="dashboard.metrics.role.staff.upcomingBlocks.description",
            value=0, unit="blocks", severity="info",
            owner="staff", pdpa="internal", now=now,
        ),
        _metric(
            code="my_supervision_count", title_k="dashboard.metrics.role.staff.mySupervisionCount",
            desc_k="dashboard.metrics.role.staff.mySupervisionCount.description",
            value=supervision_count, unit="records",
            severity="info", owner="staff", pdpa="public", now=now,
        ),
    ]

    groups.append(_group("operations", "dashboard.metrics.role.group.operations",
                          "dashboard.metrics.role.group.operations.description",
                          metrics))

    summary = DashboardRoleSummary(
        role="staff",
        role_label_i18n_key="dashboard.role.staff",
        health_score=None,
        risk_band=None,
        key_metrics=metrics,
        alerts=[],
        recommended_actions=[],
        last_updated=now,
    )
    return summary, groups


# ── teacher ───────────────────────────────────────────────────────────────────

def _build_teacher(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    stats = _safe_get(ctx, "dashboard_stats")
    exam_count = int(_safe_float((stats or {}).get("total_sections", 0)))

    metrics: list[DashboardMetric] = [
        _metric(
            code="my_exam_count", title_k="dashboard.metrics.role.teacher.myExamCount",
            desc_k="dashboard.metrics.role.teacher.myExamCount.description",
            value=exam_count, unit="sections", severity=_sev(exam_count, 0, 1, 5),
            owner="teacher", pdpa="public", now=now,
        ),
        _metric(
            code="submission_status", title_k="dashboard.metrics.role.teacher.submissionStatus",
            desc_k="dashboard.metrics.role.teacher.submissionStatus.description",
            value="n/a", unit="", severity="info",
            owner="teacher", pdpa="public", now=now,
        ),
        _metric(
            code="next_exam_date", title_k="dashboard.metrics.role.teacher.examDate",
            desc_k="dashboard.metrics.role.teacher.examDate.description",
            value="—", unit="", severity="info",
            owner="teacher", pdpa="public", now=now,
        ),
    ]

    groups = [_group("myExamWork", "dashboard.metrics.role.group.myExamWork",
                      "dashboard.metrics.role.group.myExamWork.description", metrics)]
    summary = _empty_summary("teacher", metrics, now)
    return summary, groups


# ── student ───────────────────────────────────────────────────────────────────

def _build_student(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    stats = _safe_get(ctx, "dashboard_stats")
    unscheduled = int(_safe_float((stats or {}).get("unscheduled_sections", 0)))

    metrics: list[DashboardMetric] = [
        _metric(
            code="up_next_count", title_k="dashboard.metrics.role.student.nextExam",
            desc_k="dashboard.metrics.role.student.nextExam.description",
            value=0, unit="exams", severity="info",
            owner="student", pdpa="public", now=now,
        ),
        _metric(
            code="schedule_completeness_pct", title_k="dashboard.metrics.role.student.scheduleCompleteness",
            desc_k="dashboard.metrics.role.student.scheduleCompleteness.description",
            value=100.0 if unscheduled == 0 else max(0.0, 100.0 - unscheduled * 2),
            unit="%", severity=_sev(unscheduled, 0, 5, 20, inverse=True),
            owner="student", pdpa="public", now=now,
        ),
    ]

    groups = [_group("studentSchedule", "dashboard.metrics.role.group.studentSchedule",
                      "dashboard.metrics.role.group.studentSchedule.description", metrics)]
    summary = _empty_summary("student", metrics, now)
    return summary, groups


# ── print shop ────────────────────────────────────────────────────────────────

def _build_print_shop(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    metrics: list[DashboardMetric] = [
        _metric(
            code="queue_size", title_k="dashboard.metrics.role.printShop.queueSize",
            desc_k="dashboard.metrics.role.printShop.queueSize.description",
            value=0, unit="items", severity="info",
            owner="print_shop", pdpa="internal", now=now,
        ),
        _metric(
            code="ready_to_print", title_k="dashboard.metrics.role.printShop.readyToPrint",
            desc_k="dashboard.metrics.role.printShop.readyToPrint.description",
            value=0, unit="batches", severity="good",
            owner="print_shop", pdpa="internal", now=now,
        ),
        _metric(
            code="awaiting_pickup", title_k="dashboard.metrics.role.printShop.awaitingPickup",
            desc_k="dashboard.metrics.role.printShop.awaitingPickup.description",
            value=0, unit="items", severity="info",
            owner="print_shop", pdpa="public", now=now,
        ),
    ]
    groups = [_group("printQueue", "dashboard.metrics.role.group.printQueue",
                      "dashboard.metrics.role.group.printQueue.description", metrics)]
    summary = _empty_summary("print_shop", metrics, now)
    return summary, groups


# ── department supervisor ─────────────────────────────────────────────────────

def _build_department_supervisor(
    ctx: dict,
) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    stats = _safe_get(ctx, "dashboard_stats")
    unscheduled = int(_safe_float((stats or {}).get("unscheduled_sections", 0)))
    published = int(_safe_float((stats or {}).get("scheduled_sections", 0)))

    metrics: list[DashboardMetric] = [
        _metric(
            code="dept_unscheduled_count", title_k="dashboard.metrics.role.deptSupervisor.unscheduledCount",
            desc_k="dashboard.metrics.role.deptSupervisor.unscheduledCount.description",
            value=unscheduled, unit="sections",
            severity=_sev(unscheduled, 0, 2, 10),
            owner="dept_supervisor", pdpa="internal", now=now,
        ),
        _metric(
            code="dept_submission_rate_pct", title_k="dashboard.metrics.role.deptSupervisor.submissionRate",
            desc_k="dashboard.metrics.role.deptSupervisor.submissionRate.description",
            value=0.0, unit="%", severity="info",
            owner="dept_supervisor", pdpa="public", now=now,
        ),
    ]
    groups = [_group("deptOversight", "dashboard.metrics.role.group.deptOversight",
                      "dashboard.metrics.role.group.deptOversight.description", metrics)]
    summary = _empty_summary("dept_supervisor", metrics, now)
    return summary, groups


# ── ESQ head / secretary ──────────────────────────────────────────────────────

def _build_esq_secretary(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    governance = _safe_get(ctx, "governance_analytics")
    metrics: list[DashboardMetric] = []

    if governance:
        blockers = int(_safe_float(governance.get("blocker_count", 0)))
        metrics.append(
            _metric(
                code="pending_approvals", title_k="dashboard.metrics.governance.pendingApprovals",
                desc_k="dashboard.metrics.governance.pendingApprovals.description",
                value=int(_safe_float(governance.get("pending_approvals", blockers))),
                unit="approvals", severity=_sev(blockers, 0, 0, 5),
                owner="esq_head", pdpa="confidential", now=now,
            )
        )

    metrics += [
        _metric(
            code="publication_blockers", title_k="dashboard.metrics.governance.publicationBlockers",
            desc_k="dashboard.metrics.governance.publicationBlockers.description",
            value=0, unit="blockers", severity="info",
            owner="esq_head", pdpa="confidential", now=now,
        ),
        _metric(
            code="rollback_events_recent", title_k="dashboard.metrics.governance.rollbackEvents",
            desc_k="dashboard.metrics.governance.rollbackEvents.description",
            value=0, unit="events", severity="info",
            owner="esq_head", pdpa="confidential", now=now,
        ),
    ]

    groups = [_group("governance", "dashboard.admin.group.governanceApproval",
                      "dashboard.admin.group.governanceApproval.description", metrics)]
    summary = _empty_summary("esq_head", metrics, now)
    return summary, groups


# ── IT ────────────────────────────────────────────────────────────────────────

def _build_it(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    health = _safe_get(ctx, "health") or {}
    ops_groups = DashboardMetricService.build_ops_health_groups(health)
    metrics = ops_groups[0]["metrics"] if ops_groups else []

    groups = [_group("systemHealth", "dashboard.health.title",
                      "dashboard.health.title", metrics or [])]
    summary = DashboardRoleSummary(
        role="it",
        role_label_i18n_key="dashboard.role.it",
        health_score=None,
        risk_band=None,
        key_metrics=metrics,
        alerts=[],
        recommended_actions=[],
        last_updated=now,
    )
    return summary, groups


# ── DPO ───────────────────────────────────────────────────────────────────────

def _build_dpo(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    pdpa_alerts = _safe_get(ctx, "pdpa_alerts") or []
    alert_cnt = len(pdpa_alerts)

    metrics: list[DashboardMetric] = [
        _metric(
            code="pdpa_alert_count_7d", title_k="dashboard.metrics.role.dpo.pdpaAlertCount",
            desc_k="dashboard.metrics.role.dpo.pdpaAlertCount.description",
            value=alert_cnt, unit="alerts",
            severity=_sev(alert_cnt, 0, 1, 5),
            owner="dpo", pdpa="restricted", now=now,
        ),
        _metric(
            code="audit_gap_count", title_k="dashboard.metrics.role.dpo.auditGapCount",
            desc_k="dashboard.metrics.role.dpo.auditGapCount.description",
            value=0, unit="gaps", severity="info",
            owner="dpo", pdpa="confidential", now=now,
        ),
        _metric(
            code="restricted_export_count_7d", title_k="dashboard.pdpa.restrictedExports",
            desc_k="dashboard.pdpa.restrictedExports",
            value=0, unit="exports", severity="info",
            owner="dpo", pdpa="restricted", now=now,
        ),
    ]

    groups = [_group("pdpaSecurity", "dashboard.admin.group.pdpaSecurity",
                      "dashboard.admin.group.pdpaSecurity.description", metrics)]
    summary = _empty_summary("dpo", metrics, now)
    return summary, groups


# ── executive ─────────────────────────────────────────────────────────────────

def _build_executive(ctx: dict) -> tuple[DashboardRoleSummary, list[DashboardMetricGroup]]:
    now = _now()
    exec_summary = _safe_get(ctx, "executive_summary") or {}
    score = _safe_float(exec_summary.get("overall_health_score"))
    raw_band = exec_summary.get("risk_band", "green")

    metrics: list[DashboardMetric] = []
    if score:
        metrics.append(
            _metric(
                code="overall_health_score", title_k="dashboard.admin.overallHealth",
                desc_k="dashboard.admin.overallHealth",
                value=round(score, 1), unit="score",
                severity=_sev(score, 90, 70, 50, inverse=True),
                owner="admin", pdpa="public", now=now,
            )
        )
    else:
        metrics.append(
            _metric(
                code="overall_health_score", title_k="dashboard.admin.overallHealth",
                desc_k="dashboard.admin.overallHealth",
                value=None, unit="score", severity="info",
                owner="admin", pdpa="public", now=now,
            )
        )

    top_risks = exec_summary.get("top_risks", [])
    metrics.append(
        DashboardMetricService.build_metric(
            metric_code="top_risks",
            title_i18n_key="dashboard.metrics.executive.topRisks",
            description_i18n_key="dashboard.metrics.executive.topRisks.description",
            value=len(top_risks),
            unit="risks",
            trend="unknown",
            trend_label_i18n_key="common.unknown",
            severity=_sev(len(top_risks), 0, 1, 5),
            why_it_matters_i18n_key="dashboard.metrics.executive.topRisks.why",
            recommended_action_i18n_key="dashboard.actions.reviewGovernanceBlockers",
            owner_role="admin",
            pdpa_level="internal",
            updated_at=now,
        )
    )

    groups = [_group("executive", "dashboard.role.executive",
                      "dashboard.role.executive", metrics)]
    summary = DashboardRoleSummary(
        role="executive",
        role_label_i18n_key="dashboard.role.executive",
        health_score=score if score else None,
        risk_band=raw_band if raw_band in ("green", "amber", "red") else "green",
        key_metrics=metrics,
        alerts=[],
        recommended_actions=[],
        last_updated=now,
    )
    return summary, groups


# ── unauthorized ──────────────────────────────────────────────────────────────

def _build_unauthorized(role: str) -> RoleDashboardPayload:
    return RoleDashboardPayload(
        role=role,
        role_label_i18n_key=f"dashboard.role.{role}",
        summary=_build_empty_summary(role),
        groups=[],
        unauthorized=True,
    )


# ── private helpers ────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_get(ctx: dict, key: str) -> Any:
    return ctx.get(key) if ctx else None

def _sev(
    value: int | float,
    good: float,
    info: float,
    warning: float,
    *,
    inverse: bool = False,
) -> str:
    """Return severity band for a numeric value against thresholds."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if inverse:
        if v <= good:   return "good"
        if v <= info:   return "info"
        if v <= warning: return "warning"
        return "critical"
    if v >= warning:  return "critical"
    if v >= info:     return "warning"
    if v >= good:     return "info"
    return "good"

def _metric(
    code: str,
    title_k: str,
    desc_k: str,
    value: int | float | str,
    unit: str,
    severity: str,
    owner: str,
    pdpa: str,
    now: str,
    why_k: str | None = None,
    action_k: str = "",
) -> DashboardMetric:
    return DashboardMetricService.build_metric(
        metric_code=code,
        title_i18n_key=title_k,
        description_i18n_key=desc_k,
        value=value,
        unit=unit,
        trend="unknown",
        trend_label_i18n_key="common.unknown",
        severity=severity,
        why_it_matters_i18n_key=why_k or title_k,
        recommended_action_i18n_key=action_k,
        owner_role=owner,
        pdpa_level=pdpa,
        updated_at=now,
    )

def _group(
    code: str, title_k: str, desc_k: str, metrics: list[DashboardMetric]
) -> DashboardMetricGroup:
    return DashboardMetricService.build_metric_group(
        group_code=code,
        title_i18n_key=title_k,
        description_i18n_key=desc_k,
        metrics=metrics,
    )

def _empty_summary(
    role: str, metrics: list[DashboardMetric], now: str
) -> DashboardRoleSummary:
    return DashboardRoleSummary(
        role=role,
        role_label_i18n_key=f"dashboard.role.{role}",
        health_score=None,
        risk_band=None,
        key_metrics=metrics,
        alerts=[],
        recommended_actions=[],
        last_updated=now,
    )


# ── builder registry (module-level — avoids class-def forward-ref) ─────────────

_BUILDERS: dict[str, Any] = {
    "staff":            _build_staff,
    "teacher":          _build_teacher,
    "student":          _build_student,
    "print_shop":       _build_print_shop,
    "dept_supervisor":  _build_department_supervisor,
    "esq_head":         _build_esq_secretary,
    "secretary":        _build_esq_secretary,
    "it":               _build_it,
    "dpo":              _build_dpo,
    "executive":        _build_executive,
}
