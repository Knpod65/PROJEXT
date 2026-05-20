"""role_dashboard_service.py — Role-specific dashboard builders.

In s2 this is the factory skeleton (builders implemented in OPS-DASH-s4).

Rules:
- Pure logic. No DB, no ORM, no HTTP.
- PDPA-aware: each builder must respect the role clearance table in
  ROLE_BASED_SIGNIFICANT_METRICS_MODEL.md.
"""
from __future__ import annotations

from typing import Any

from contracts.dashboard_metric_contracts import (
    DashboardRoleSummary,
    DashboardMetricGroup,
    RoleDashboardPayload,
    build_minimal_metric,
    build_minimal_group,
    build_minimal_payload,
)

from services.dashboard_metric_service import DashboardMetricService


class RoleDashboardService:
    """Factory that dispatches to role-specific builders."""

    @staticmethod
    def build_role_dashboard(
        role: str,
        context: dict[str, Any] | None = None,
    ) -> RoleDashboardPayload:
        """Build a full role dashboard payload for *role*.

        context may contain ``db`` and ``user`` keys for data queries.
        OPS-DASH-s4 adds the actual builder implementations;
        this version returns a safe minimal payload so the rest of the
        system can be developed and tested against it.
        """
        try:
            from contracts.dashboard_metric_contracts import build_minimal_payload
            return build_minimal_payload(role)
        except Exception:
            return _build_unauthorized(role)

    @staticmethod
    def build_minimal_payload(role: str) -> RoleDashboardPayload:
        return build_minimal_payload(role)

    # ── placeholder — populated in s4 ─────────────────────────────────────────

    @staticmethod
    def build_staff_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_teacher_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_student_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_print_shop_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_department_supervisor_dashboard(
        context: dict | None = None,
    ) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_esq_secretary_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_it_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_dpo_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")

    @staticmethod
    def build_executive_dashboard(context: dict | None = None) -> RoleDashboardPayload:
        raise NotImplementedError("Implemented in OPS-DASH-s4")


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_unauthorized(role: str) -> RoleDashboardPayload:
    return RoleDashboardPayload(
        role=role,
        role_label_i18n_key=f"dashboard.role.{role}",
        summary=_build_empty_summary(role),
        groups=[],
        unauthorized=True,
    )


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
