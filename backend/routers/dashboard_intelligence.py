"""dashboard_intelligence.py — Role-based dashboard intelligence API.

Endpoints (all additive, no existing routes modified):
  GET /api/dashboard/admin-intelligence  — Admin 10-group intelligence (admin only)
  GET /api/dashboard/role-summary       — Auto-detected role dashboard
  GET /api/dashboard/role-summary/{role}— Explicit role summary
  GET /api/dashboard/ops-health         — System operations health (authenticated)
  GET /api/dashboard/pdpa-health        — PDPA security health (admin/esq/secretary/dpo)
  GET /api/dashboard/executive-summary  — Executive summary (admin/esq/secretary)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
import models, schemas
from auth_utils import get_current_user, get_effective_role
from policies.dashboard_metric_policy import DashboardMetricPolicy
from services.dashboard_metric_service import DashboardMetricService
from services.admin_dashboard_intelligence_service import AdminDashboardIntelligenceService
from services.role_dashboard_service import RoleDashboardService
from services.health_service import get_system_health
from services.pdpa_runtime_guard_service import PDPARuntimeGuardService

router = APIRouter(prefix="/dashboard", tags=["dashboard-intelligence"])


# ── helpers ────────────────────────────────────────────────────────────────

def _eff(user: models.User) -> str:
    """Return effective role lowercase string."""
    return get_effective_role(user).value.lower()


# ── admin intelligence ─────────────────────────────────────────────────────

@router.get("/admin-intelligence", response_model=schemas.AdminIntelligenceDashboard)
def get_admin_intelligence(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    eff = _eff(current_user)
    DashboardMetricPolicy.can_view_admin_intelligence(eff)
    payload = AdminDashboardIntelligenceService.build_admin_intelligence_dashboard(
        db, current_user, semester, academic_year
    )
    return payload


# ── role summary ───────────────────────────────────────────────────────────

@router.get("/role-summary/{role}", response_model=schemas.RoleDashboardPayload)
def get_role_summary(
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    req = _eff(current_user)
    DashboardMetricPolicy.can_view_role_summary(req, role)
    payload = RoleDashboardService.build_role_dashboard(role, {"db": db, "user": current_user})
    return payload


@router.get("/role-summary", response_model=schemas.RoleDashboardPayload)
def get_my_role_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = _eff(current_user)
    payload = RoleDashboardService.build_role_dashboard(role, {"db": db, "user": current_user})
    return payload


# ── ops-health ─────────────────────────────────────────────────────────────

@router.get("/ops-health")
def get_ops_health(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    health = get_system_health(db)
    groups = DashboardMetricService.build_ops_health_groups(health)
    return {
        "groups": groups,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


# ── pdpa-health ────────────────────────────────────────────────────────────

@router.get("/pdpa-health")
def get_pdpa_health(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    eff = _eff(current_user)
    DashboardMetricPolicy.can_view_pdpa_health(eff)
    alerts = PDPARuntimeGuardService.get_recent_alerts(db, hours=24)
    groups = DashboardMetricService.build_pdpa_health_groups(alerts)
    return {
        "groups": groups,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


# ── executive summary ──────────────────────────────────────────────────────

@router.get("/executive-summary", response_model=schemas.ExecutiveDashboardSummary)
def get_executive_summary(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    from services.executive_dashboard_projection_service import (
        ExecutiveDashboardProjectionService,
    )

    eff = _eff(current_user)
    DashboardMetricPolicy.can_view_executive_summary(eff)

    # Reuse the existing projection service — passes context dict directly.
    workload_analytics = None
    governance_analytics = None
    room_analytics = None
    pdpa_guard = None

    try:
        from services.workload_analytics_service import compute_workload_analytics
        workload_analytics = compute_workload_analytics(db, semester, academic_year)
    except Exception:
        workload_analytics = None

    try:
        from services.governance_analytics_service import compute_governance_analytics
        governance_analytics = compute_governance_analytics([], [])
    except Exception:
        governance_analytics = None

    try:
        from services.room_utilization_analytics_service import compute_room_utilization
        room_analytics = compute_room_utilization(db, semester, academic_year)
    except Exception:
        room_analytics = None

    try:
        pdpa_guard = PDPARuntimeGuardService.get_recent_alerts(db, hours=24)
    except Exception:
        pdpa_guard = []

    summary = ExecutiveDashboardProjectionService.build_executive_dashboard_summary(
        workload_analytics or {},
        governance_analytics or {},
        room_analytics or {},
        pdpa_guard,
    )
    return schemas.ExecutiveDashboardSummary(**summary)
