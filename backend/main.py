"""
EMS — Exam Management System
คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่
FastAPI + PostgreSQL  |  Phase 1: Foundation + M2 Scheduler
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

from database import engine, Base, get_db
import permissions
from sqlalchemy import text
from sqlalchemy.orm import Session
from cmu_sso import router as sso_router
from config.policy import ALLOWED_ORIGINS, LOGIN_RATE_MAX, LOGIN_RATE_WINDOW
from routers import auth, courses, schedule, users, dashboard, pdf, public, settings, submissions, swaps, checkins, exports, swaps_v2, documents, period, external_exams, optimize_workflow, co_exam, exam_manager, printing, historical_schedules, invigilation_advance_batch, invigilation_rate_rules, payment_document_reviews, analytics as analytics_router
from routers import scheduler, exports_excel, health as health_router
from routers import admin as admin_router
from routers import dashboard_intelligence
import models
import logging
import os

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Warn if SECRET_KEY is using dev default
if os.getenv("SECRET_KEY", "") in ("", "dev-secret-key-change-me"):
    logging.warning("SECRET_KEY is using the default dev value. In production, set a random 32+ character SECRET_KEY.")

# Event handler registration (side-effect imports)
import event_handlers.optimization_handler  # noqa: F401
import event_handlers.governance_handler    # noqa: F401
import event_handlers.publication_handler   # noqa: F401
import event_handlers.audit_handler         # noqa: F401

try:
    from routers import imports, imports_v2
    IMPORT_ROUTERS_ERROR = None
except Exception as exc:
    imports = None
    imports_v2 = None
    IMPORT_ROUTERS_ERROR = exc

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Security: validate secrets before anything else
    from security import validate_production_secrets
    validate_production_secrets()

    # Required: bind RBAC dependency guards so role checks do not stay as stubs.
    permissions.build_dependencies()

    # Create tables + seed dev data — only in deliberate development mode.
    # Production and pilot environments must manage schema via migrations.
    env = getattr(settings, "environment", "development")
    if env == "development":
        import logging as _startup_logging
        _startup_logging.getLogger(__name__).warning(
            "STARTUP MUTATION ENABLED: schema create_all() and seed_data() are running. "
            "This is intended for local development only. "
            "Do not run production or pilot startup with ENVIRONMENT=development."
        )
        Base.metadata.create_all(bind=engine)
        from seed import seed_data
        from sqlalchemy.orm import Session
        db = Session(engine)
        seed_data(db)
        db.close()
    else:
        import logging as _startup_logging
        _startup_logging.getLogger(__name__).info(
            "ENVIRONMENT=%s: skipping create_all()/seed_data() — schema must be managed via migrations."
            % env
        )
    yield



# ── Request Logging + Correlation ID Middleware ───────────────
import uuid, time, logging, hashlib, os
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
from collections import defaultdict

def get_request_id() -> str:
    return ""

try:
    from logging_config import setup_logging, _request_id_var, _user_id_var, app_log, get_request_id
    _JSON_LOGS = os.getenv("JSON_LOGS", "true").lower() == "true"
    setup_logging(os.getenv("LOG_LEVEL", "INFO"), json_logs=_JSON_LOGS)
except ImportError:
    _request_id_var = ContextVar("request_id", default="")
    _user_id_var    = ContextVar("user_id",    default=0)
    app_log         = logging.getLogger("ems")

if IMPORT_ROUTERS_ERROR is not None:
    app_log.warning(
        "Import routes disabled during startup: %s",
        IMPORT_ROUTERS_ERROR,
    )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ทุก request:
      - สร้าง X-Request-ID (UUID) → ติดตามใน logs และ response header
      - วัด duration_ms
      - log path + status + duration
      - เพิ่มใน AuditLog ถ้า action สำคัญ
    """
    async def dispatch(self, request: StarletteRequest, call_next):
        # correlation ID — sanitize client-provided value to prevent log injection
        client_req_id = request.headers.get("X-Request-ID", "")
        import re
        if client_req_id and re.match(r'^[a-zA-Z0-9\-]{1,64}$', client_req_id):
            req_id = client_req_id
        else:
            req_id = str(uuid.uuid4())
        _request_id_var.set(req_id)

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            app_log.error(
                f"Unhandled exception: {e}",
                extra={"path": request.url.path, "method": request.method,
                       "request_id": req_id}
            )
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)

        status = response.status_code
        # log ทุก request (ยกเว้น /health)
        if request.url.path != "/health":
            level = logging.WARNING if status >= 400 else logging.INFO
            app_log.log(
                level,
                f"{request.method} {request.url.path} {status} {duration_ms}ms",
                extra={
                    "method":      request.method,
                    "path":        request.url.path,
                    "status_code": status,
                    "duration_ms": duration_ms,
                    "request_id":  req_id,
                }
            )

        # เพิ่ม response headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response

# ── Security Headers Middleware ───────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]        = "SAMEORIGIN"
        response.headers["X-XSS-Protection"]       = "1; mode=block"
        response.headers["Referrer-Policy"]        = "strict-origin-when-cross-origin"
        # ลบ server header เพื่อไม่บอก attacker ว่าใช้ FastAPI
        if "server" in response.headers:
            del response.headers["server"]
        return response


# ── Simple in-memory rate limiter สำหรับ login ────────────────
_login_attempts: dict = defaultdict(list)

class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        if request.url.path == "/api/auth/login" and request.method == "POST":
            from security import get_real_ip
            ip = get_real_ip(request)
            now = time.time()
            # ล้าง attempts เก่า
            _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < LOGIN_RATE_WINDOW]
            if len(_login_attempts[ip]) >= LOGIN_RATE_MAX:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"พยายาม login มากเกินไป — รอ {LOGIN_RATE_WINDOW//60} นาที"}
                )
            _login_attempts[ip].append(now)
        return await call_next(request)


app = FastAPI(
    title="EMS — ระบบจัดการข้อสอบ มช.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoginRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Routers
app.include_router(health_router.router, prefix="/api/health", tags=["health"])
app.include_router(public.router,  prefix="/api/public",  tags=["public"])
app.include_router(submissions.router,  prefix="/api/submissions",  tags=["submissions"])
app.include_router(swaps.router,  prefix="/api/swaps",  tags=["swaps"])
app.include_router(swaps_v2.router,  prefix="/api/swaps2",  tags=["swaps-v2"])
app.include_router(checkins.router,  prefix="/api/checkins",  tags=["checkins"])
app.include_router(exports.router,  prefix="/api/exports",  tags=["exports"])
app.include_router(settings.router,  prefix="/api/settings",  tags=["settings"])
app.include_router(auth.router,      prefix="/api/auth",     tags=["auth"])
app.include_router(sso_router,       prefix="/api/auth/sso", tags=["auth-sso"])
app.include_router(users.router,     prefix="/api/users",    tags=["users"])
app.include_router(courses.router,   prefix="/api/courses",  tags=["courses"])
app.include_router(schedule.router,  prefix="/api/schedule", tags=["schedule"])
app.include_router(dashboard.router, prefix="/api/dashboard",tags=["dashboard"])
app.include_router(pdf.router,       prefix="/api/pdf",      tags=["pdf"])
if imports is not None:
    app.include_router(imports.router,   prefix="/api/import",   tags=["import"])
if imports_v2 is not None:
    app.include_router(imports_v2.router, prefix="/api/import/v2", tags=["import-v2"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(printing.router, prefix="/api/printing", tags=["printing"])
app.include_router(period.router,         prefix="/api/period",    tags=["period"])
app.include_router(external_exams.router,      prefix="/api/external",  tags=["external"])
app.include_router(optimize_workflow.router, prefix="/api/workflow",  tags=["workflow"])
app.include_router(co_exam.router,          prefix="/api/co-exam",      tags=["co-exam"])
app.include_router(exam_manager.router,      prefix="/api/exam-manager",    tags=["exam-manager"])
app.include_router(historical_schedules.router, prefix="/api/historical-schedules", tags=["historical-schedules"])
app.include_router(invigilation_advance_batch.router, prefix="/api/invigilation-advance-batch", tags=["invigilation-advance-batch"])
app.include_router(invigilation_rate_rules.router, prefix="/api/invigilation-payment", tags=["invigilation-payment"])
app.include_router(payment_document_reviews.router, prefix="/api/payment-document-reviews", tags=["payment-document-reviews"])
app.include_router(scheduler.router,         prefix="/api/scheduler",       tags=["scheduler"])
app.include_router(exports_excel.router,     prefix="/api/exports",         tags=["exports-excel"])
app.include_router(admin_router.router,      prefix="/api/admin",           tags=["admin"])
app.include_router(dashboard_intelligence.router, prefix="/api/dashboard", tags=["dashboard-intelligence"])

# Analytics router (D4.9)
app.include_router(analytics_router.router, tags=["analytics"])

# Serve frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    logging.warning("Static directory not found; skipping static mount: %s", STATIC_DIR)



# ── Global Exception Handler ─────────────────────────────────
from fastapi import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: FastAPIRequest, exc: RequestValidationError):
    """Pydantic validation errors → Thai-friendly messages"""
    errors = []
    for e in exc.errors():
        field = " → ".join(str(x) for x in e["loc"] if x != "body")
        msg   = e["msg"]
        errors.append(f"{field}: {msg}" if field else msg)
    return JSONResponse(
        status_code=422,
        content={"detail": "ข้อมูลไม่ถูกต้อง: " + "; ".join(errors)},
        headers={"X-Request-ID": get_request_id() or ""}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: FastAPIRequest, exc: Exception):
    """จับ unhandled exceptions — log แบบ structured แล้ว return 500"""
    req_id = get_request_id() or "unknown"
    app_log.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        extra={
            "request_id": req_id,
            "path":       str(request.url.path),
            "traceback":  traceback.format_exc()[-2000:],  # truncate
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "เกิดข้อผิดพลาดภายในระบบ กรุณาแจ้ง Admin พร้อม Request ID: " + req_id},
        headers={"X-Request-ID": req_id}
    )

# ── Serve landing page ─────────────────────────────────────────
from fastapi.responses import FileResponse, RedirectResponse
import os as _os

@app.get("/")
def landing_page():
    """Public landing page — timeline + student search"""
    path = _os.path.join(_os.path.dirname(__file__), "static", "landing.html")
    return FileResponse(path)

@app.get("/app")
def app_page():
    """Main SPA — requires login"""
    path = _os.path.join(_os.path.dirname(__file__), "static", "index.html")
    return FileResponse(path)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check สำหรับ Docker / load balancer"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "db":     "connected",
            "version": "2.0.0",
        }
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": type(e).__name__},
        )

# Route cache: maps "/api/X" → "/api/X/" when a slash-version exists.
# Starlette's redirect_slashes can't fire because this catch-all matches first.
# We replicate that behaviour here, but only for GET requests to /api/* paths.
_api_slash_cache: dict[str, str | None] = {}

def _find_slash_route(app_routes: list, path: str) -> str | None:
    slash = path.rstrip("/") + "/"
    for route in app_routes:
        rp = getattr(route, "path", "")
        rm = getattr(route, "methods", None) or set()
        if rp == slash and "GET" in rm:
            return slash
    return None

@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: FastAPIRequest):
    normalized = full_path.lstrip("/")
    if normalized.startswith("api/") or normalized == "api":
        req_path = "/" + normalized
        # Cache lookup so we only scan routes once per path
        if req_path not in _api_slash_cache:
            _api_slash_cache[req_path] = _find_slash_route(request.app.routes, req_path)
        slash_path = _api_slash_cache[req_path]
        if slash_path:
            qs = str(request.query_params)
            return RedirectResponse(
                url=slash_path + (f"?{qs}" if qs else ""),
                status_code=307,
            )
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    path = _os.path.join(_os.path.dirname(__file__), "static", "index.html")
    return FileResponse(path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
