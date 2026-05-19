"""Analytics router foundation.

Defines the /api/analytics endpoint group with read-only endpoints.
All endpoints delegate to AnalyticsService for orchestration.
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
from services.analytics_service import AnalyticsService
from validators.analytics_validator import AnalyticsValidator
from serializers.analytics_serializer import AnalyticsSerializer
from database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/metrics")
def list_analytics_metrics():
    return list_metrics()


@router.get("/metrics/{metric_code}")
def get_analytics_metric(metric_code: str):
    metric_code = AnalyticsValidator.validate_metric_code(metric_code)
    try:
        raw = get_metric(metric_code)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_code}' not found")
    return AnalyticsSerializer.serialize_metric(raw)


@router.get("/executive-summary")
def get_executive_summary(db: Session = Depends(get_db)):
    raw = project_executive_dashboard()
    return AnalyticsSerializer.serialize_executive_summary(raw)


@router.get("/integration-contracts")
def list_integration_contracts():
    return list_contracts()


@router.get("/optimization-trace/{session_id}")
def get_optimization_trace(
    session_id: int,
    db: Session = Depends(get_db),
):
    AnalyticsValidator.validate_session_id(session_id)
    try:
        trace = AnalyticsService.build_optimization_trace(db, session_id)
    except Exception as exc:
        now_iso = AnalyticsService.get_utcnow_iso()
        trace = AnalyticsService.build_empty_trace_stub(session_id, now_iso, f"trace unavailable: {exc}")
    return AnalyticsSerializer.serialize_trace(trace)


@router.get("/governance-timeline")
def get_governance_timeline():
    events = AnalyticsService.build_governance_timeline()
    return AnalyticsSerializer.serialize_governance_timeline(events)


@router.get("/lifecycle-timeline/{session_id}")
def get_lifecycle_timeline(session_id: int):
    AnalyticsValidator.validate_session_id(session_id)
    events = AnalyticsService.build_lifecycle_timeline(session_id)
    return AnalyticsSerializer.serialize_lifecycle_timeline(events)
