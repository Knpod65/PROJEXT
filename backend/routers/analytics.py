"""Analytics router foundation.

Defines the /api/analytics endpoint group with four read-only endpoints:
- GET /api/metrics          → list all metric definitions
- GET /api/metrics/{code}   → get single metric definition
- GET /api/executive-summary→ current executive dashboard view
- GET /api/integration-contracts → list all integration contracts

All endpoints are read-only, idempotent, and return JSON-safe data.
No PII is ever exposed in outputs.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.analytics_metric_registry_service import (
    list_metrics,
    get_metric,
)
from services.executive_dashboard_projection_service import (
    project_executive_dashboard,
)
from services.integration_contract_registry_service import (
    list_contracts,
)
from database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/metrics")
def list_analytics_metrics():
    """Return all metric definitions from the registry."""
    return list_metrics()


@router.get("/metrics/{metric_code}")
def get_analytics_metric(metric_code: str):
    """Return a single metric definition or 404 if not found."""
    try:
        return get_metric(metric_code)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Metric '{metric_code}' not found",
        )


@router.get("/executive-summary")
def get_executive_summary(db: Session = Depends(get_db)):
    """Return the current executive dashboard view.

    For D4, this returns a safe default (zeroed) view since no actual
    data inputs are wired yet. The endpoint is ready to accept
    pre-computed dicts from existing EMS services in future slices.
    """
    # TODO: Wire actual service outputs from:
    # - workload_analytics_service.compute_workload_analytics()
    # - room_utilization_analytics_service.compute_room_analytics()
    # - governance_analytics_service.compute_governance_analytics()
    # - analytics_projection_service.*_trend()
    # - executive_risk_service.compute_executive_risk_report()
    return project_executive_dashboard()


@router.get("/integration-contracts")
def list_integration_contracts():
    """Return all registered integration contracts for audit/admin view."""
    return list_contracts()
