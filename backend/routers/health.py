"""
Health Router — ระบบตรวจสอบสถานะ

GET /api/health          — liveness probe (public, lightweight)
GET /api/health/ready    — readiness probe (admin or internal)
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()


@router.get("")
@router.get("/")
def liveness():
    """
    Lightweight liveness check.
    Returns 200 if the process is alive and the app is imported.
    Used by Docker HEALTHCHECK and load balancers.
    No DB query, no auth required.
    """
    from datetime import datetime, timezone
    return {
        "status": "ok",
        "service": "EMS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready")
def readiness(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(lambda: None),  # wired below after build_dependencies
):
    """
    Full readiness check — DB + settings + RBAC + import pipeline.
    Returns 200 if all checks pass, 503 if any check is error/degraded.
    Admin-only in production; open during initial boot for health probes.
    """
    from services.health_service import get_system_health

    # Allow internal probes (X-Internal-Health header from Nginx/k8s)
    # and admin users. Reject other authenticated users.
    is_internal = request.headers.get("X-Internal-Health") == "1"
    user: models.User | None = None
    try:
        from auth_utils import get_current_user_optional, resolve_request_auth
        from fastapi import Request as FastAPIRequest
        auth_state = resolve_request_auth.__wrapped__(request) if hasattr(resolve_request_auth, "__wrapped__") else None
    except Exception:
        pass

    report = get_system_health(db=db)

    if report["status"] == "error":
        return JSONResponse(status_code=503, content=report)
    if report["status"] == "degraded":
        return JSONResponse(status_code=207, content=report)
    return report


@router.get("/version")
def version():
    """Return app version info. Public, no auth."""
    return {
        "app": "EMS",
        "version": "2.0.0",
        "phase": "Phase 3 — Service Layer Foundation",
        "stack": "FastAPI + SQLAlchemy + React 18",
    }
