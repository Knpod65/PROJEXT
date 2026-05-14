"""
Optimize Workflow Router
  - User Management (เพิ่ม/แก้/ลบ users + เปลี่ยน role)
  - Staff Unavailability (กำหนดก่อน optimize)
  - Optimize Session (confirm 4 ลายเซ็น + baseline stats)

Endpoints:
  # User Management
  GET  /api/workflow/users/             รายการ users ทั้งหมด
  POST /api/workflow/users/             เพิ่ม user ใหม่
  PUT  /api/workflow/users/{id}         แก้ไข (role, division, unit, is_active)
  POST /api/workflow/users/{id}/toggle  เปิด/ปิดใช้งาน

  # Unavailability
  GET  /api/workflow/unavailability/    รายการทั้งหมดใน active period
  POST /api/workflow/unavailability/    เพิ่ม block
  DELETE /api/workflow/unavailability/{id}  ลบ block

  # Optimize Session
  GET  /api/workflow/session/           session ของ active period
  POST /api/workflow/session/init       สร้าง/reset session หลัง optimize
  POST /api/workflow/session/sign       กดลายเซ็น (ตามลำดับ)
  POST /api/workflow/session/open-swap  เปิด swap (admin)
  GET  /api/workflow/session/signers    ดูว่าใครกดแล้วบ้าง
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import models
import permissions
from auth_utils import (
    require_admin, require_staff_or_admin, get_current_user, log_action, hash_password, get_effective_role,
    require_view_all
)
from config.policy import WORKFLOW_LOCK_TTL_SECONDS
from services.audit_service import audit_event
from services.exceptions import EMSDomainError, EMSPermissionError
from services import workflow_lock_service
from services.optimization_recheck_service import run_optimization_recheck
from services.optimization_report_builder import build_optimization_report
from services.schedule_state_machine import derive_schedule_state, schedule_state_machine
from services.workflow_user_service import format_user_dict, build_external_workflow_issues
from services.workflow_reporting_service import build_staff_workload_report
from services.workflow_signing_service import (
    apply_signature,
    approve_transition,
    audit_action_for_signature,
    build_session_payload,
    get_or_create_session as get_or_create_workflow_session,
    get_signer_list,
    open_swap_transition,
    reject_transition,
)
from staff_workloads import (
    PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS,
    PAPER_DISTRIBUTION_EXCLUDED_USERNAMES,
    get_period_workload_snapshot,
    is_paper_distribution_candidate,
)
from term_lifecycle import ensure_period_record_editable, require_active_period_for_mutation
from time_ranges import normalize_time_range, normalize_time_value, parse_time_range

router = APIRouter()

# ════════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    username:     str
    email:        str
    password:     str
    role:         str          # admin | esq_head | dept_supervisor | staff | teacher
    full_name:    Optional[str] = None
    title:        Optional[str] = None
    division:     Optional[str] = None
    unit:         Optional[str] = None
    dept_code:    Optional[str] = None   # GOV/PA/IR/STB (teacher/dept_supervisor)
    mobile:       Optional[str] = None
    ext:          Optional[str] = None
    employee_id:  Optional[int] = None


class UserUpdate(BaseModel):
    role:         Optional[str] = None
    full_name:    Optional[str] = None
    title:        Optional[str] = None
    division:     Optional[str] = None
    unit:         Optional[str] = None
    dept_code:    Optional[str] = None
    mobile:       Optional[str] = None
    ext:          Optional[str] = None
    email:        Optional[str] = None
    is_active:    Optional[bool] = None
    password:     Optional[str] = None   # ถ้าต้องการ reset password


@router.get("/users/")
def list_users(
    role:    Optional[str] = None,
    active:  Optional[bool] = None,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    q = db.query(models.User)
    if role:
        role_enum = permissions.coerce_user_role(role)
        if role_enum is None:
            raise HTTPException(400, f"role ไม่ถูกต้อง: {role}")
        q = q.filter(models.User.role == role_enum)
    if active is not None:
        q = q.filter(models.User.is_active == active)

    users = q.order_by(models.User.role, models.User.full_name).all()
    return [_user_dict(u) for u in users]


@router.post("/users/")
def create_user(
    data: UserCreate,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    # ตรวจ duplicate
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(400, f"username '{data.username}' มีอยู่แล้ว")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(400, f"email '{data.email}' มีอยู่แล้ว")

    role_enum = permissions.coerce_user_role(data.role)
    if role_enum is None:
        raise HTTPException(400, f"role ไม่ถูกต้อง: {data.role}")

    user = models.User(
        username      = data.username,
        email         = data.email,
        password_hash = hash_password(data.password),
        role          = role_enum,
        full_name     = data.full_name,
        title         = data.title,
        division      = data.division,
        unit          = data.unit,
        dept_code     = data.dept_code,
        mobile        = data.mobile,
        ext           = data.ext,
        employee_id   = data.employee_id,
        is_active     = True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, current_user, "CREATE_USER", "users",
               record_id=user.id, new_values={"username": data.username, "role": data.role},
               request=request)
    return _user_dict(user)


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data:    UserUpdate,
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "ไม่พบ user")

    old = _user_dict(user)

    if data.role is not None:
        role_enum = permissions.coerce_user_role(data.role)
        if role_enum is None:
            raise HTTPException(400, f"role ไม่ถูกต้อง: {data.role}")
        user.role = role_enum
    if data.full_name  is not None: user.full_name  = data.full_name
    if data.title      is not None: user.title      = data.title
    if data.division   is not None: user.division   = data.division
    if data.unit       is not None: user.unit       = data.unit
    if data.dept_code  is not None: user.dept_code  = data.dept_code
    if data.mobile     is not None: user.mobile     = data.mobile
    if data.ext        is not None: user.ext        = data.ext
    if data.email      is not None: user.email      = data.email
    if data.is_active  is not None: user.is_active  = data.is_active
    if data.password:               user.password_hash = hash_password(data.password)

    db.commit()
    log_action(db, current_user, "UPDATE_USER", "users",
               record_id=user_id, old_values=old,
               new_values=data.dict(exclude_none=True, exclude={"password"}),
               request=request)
    return _user_dict(user)


@router.post("/users/{user_id}/toggle")
def toggle_user(
    user_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "ไม่พบ user")
    if user.id == current_user.id:
        raise HTTPException(400, "ไม่สามารถปิดใช้งานตัวเองได้")
    user.is_active = not user.is_active
    db.commit()
    log_action(db, current_user, "TOGGLE_USER", "users",
               record_id=user_id, new_values={"is_active": user.is_active}, request=request)
    return {"user_id": user_id, "is_active": user.is_active, "full_name": user.full_name}


def _user_dict(u: models.User) -> dict:
    return format_user_dict(u)


# ════════════════════════════════════════════════════════════════
# STAFF UNAVAILABILITY
# ════════════════════════════════════════════════════════════════

class UnavailCreate(BaseModel):
    user_id:    int
    block_date: str              # "2026-03-23"
    block_time: Optional[str] = None   # None = ทั้งวัน
    start_time: Optional[str] = None
    end_time:   Optional[str] = None
    reason:     Optional[str] = None


def _normalize_staff_block_fields(data: UnavailCreate) -> tuple[Optional[str], Optional[str], Optional[str]]:
    start_time = normalize_time_value(data.start_time)
    end_time = normalize_time_value(data.end_time)
    block_time = data.block_time.strip() if isinstance(data.block_time, str) and data.block_time.strip() else None

    if start_time or end_time:
        if not start_time or not end_time:
            raise HTTPException(400, "ต้องระบุทั้ง start_time และ end_time ให้ครบ")
        normalized_block = normalize_time_range(start_time, end_time)
        if not normalized_block:
            raise HTTPException(400, "ช่วงเวลาไม่ถูกต้อง")
        return normalized_block, start_time, end_time

    if block_time:
        normalized_block = normalize_time_range(*parse_time_range(block_time))
        if normalized_block:
            start_time, end_time = parse_time_range(normalized_block)
            return normalized_block, start_time, end_time
        normalized_point = normalize_time_value(block_time)
        if normalized_point:
            return normalized_point, normalized_point, normalized_point
        raise HTTPException(400, "block_time ไม่ถูกต้อง")

    return None, None, None


def _get_active_period_or_none(db: Session) -> models.ExamPeriod | None:
    return db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()


def _build_external_workflow_issues(db: Session, period_id: int | None) -> list[dict[str, object]]:
    return build_external_workflow_issues(db, period_id)


@router.get("/unavailability/")
def list_unavailability(
    period_id: Optional[int] = None,
    user_id:   Optional[int] = None,
    db:        Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if not period_id:
        p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
        period_id = p.id if p else None

    q = db.query(models.StaffUnavailability).options(
        joinedload(models.StaffUnavailability.user)
    )
    if period_id:
        q = q.filter(models.StaffUnavailability.exam_period_id == period_id)
    if user_id:
        q = q.filter(models.StaffUnavailability.user_id == user_id)

    rows = q.order_by(
        models.StaffUnavailability.block_date,
        models.StaffUnavailability.block_time
    ).all()

    return [
        {
            "id":         r.id,
            "user_id":    r.user_id,
            "full_name":  r.user.full_name if r.user else None,
            "division":   r.user.division if r.user else None,
            "unit":       r.user.unit if r.user else None,
            "block_date": r.block_date,
            "block_time": normalize_time_range(r.start_time, r.end_time) or normalize_time_range(*parse_time_range(r.block_time)) or r.block_time,
            "start_time": normalize_time_value(r.start_time) or (parse_time_range(r.block_time)[0] if r.block_time and parse_time_range(r.block_time) else None),
            "end_time":   normalize_time_value(r.end_time) or (parse_time_range(r.block_time)[1] if r.block_time and parse_time_range(r.block_time) else None),
            "all_day":    r.block_time is None and not getattr(r, "start_time", None) and not getattr(r, "end_time", None),
            "reason":     r.reason,
        }
        for r in rows
    ]


@router.post("/unavailability/")
def add_unavailability(
    data: UnavailCreate,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    p = require_active_period_for_mutation(db)
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    normalized_block_time, start_time, end_time = _normalize_staff_block_fields(data)

    # เช็ค duplicate
    existing = db.query(models.StaffUnavailability).filter(
        and_(
            models.StaffUnavailability.user_id        == data.user_id,
            models.StaffUnavailability.exam_period_id == p.id,
            models.StaffUnavailability.block_date     == data.block_date,
            models.StaffUnavailability.block_time     == normalized_block_time,
        )
    ).first()
    if existing:
        raise HTTPException(400, "มีการ block นี้อยู่แล้ว")

    row = models.StaffUnavailability(
        user_id        = data.user_id,
        exam_period_id = p.id,
        block_date     = data.block_date,
        block_time     = normalized_block_time,
        start_time     = start_time,
        end_time       = end_time,
        reason         = data.reason,
        created_by     = current_user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    log_action(db, current_user, "ADD_UNAVAILABILITY", "staff_unavailability",
               record_id=row.id,
               new_values={"user": user.full_name if user else data.user_id,
                           "date": data.block_date, "time": normalized_block_time},
               request=request)

    return {"id": row.id, "status": "added"}


@router.delete("/unavailability/{unavail_id}")
def delete_unavailability(
    unavail_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    row = db.query(models.StaffUnavailability).filter(
        models.StaffUnavailability.id == unavail_id
    ).first()
    if not row:
        raise HTTPException(404, "ไม่พบ")
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.id == row.exam_period_id
    ).first()
    ensure_period_record_editable(period)
    db.delete(row)  # term editability already checked
    db.commit()
    log_action(db, current_user, "DELETE_UNAVAILABILITY", "staff_unavailability",
               record_id=unavail_id, request=request)
    return {"status": "deleted"}


# ════════════════════════════════════════════════════════════════
@router.get("/session/")
def get_session(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")
    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
    if not sess:
        return {"status": "no_session", "message": "ยังไม่ได้ optimize"}
    return build_session_payload(sess)


@router.post("/sessions/{session_id}/recheck")
def recheck_generated_schedule(
    session_id: int,
    request: Request,
    override: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if get_effective_role(current_user) not in (
        models.UserRole.admin,
        models.UserRole.staff,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "ไม่มีสิทธิ์ตรวจ recheck")

    report = run_optimization_recheck(db, session_id)
    audit_event(
        db,
        current_user,
        "OPTIMIZATION_RECHECK_RUN",
        table_name="optimize_sessions",
        record_id=session_id,
        metadata={"status": report["status"], "summary": report["summary"]},
        request=request,
    )

    if report["status"] == "FAIL":
        audit_event(
            db,
            current_user,
            "OPTIMIZATION_RECHECK_FAIL",
            table_name="optimize_sessions",
            record_id=session_id,
            metadata={
                "hard_fail_count": report["summary"]["hard_fail_count"],
                "hard_error_count": report["summary"]["hard_error_count"],
            },
            request=request,
        )
        if override:
            audit_event(
                db,
                current_user,
                "OPTIMIZATION_RECHECK_OVERRIDE",
                table_name="optimize_sessions",
                record_id=session_id,
                metadata={"override": True},
                request=request,
            )

    return report


@router.get("/sessions/{session_id}/recheck/latest")
def get_latest_recheck_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if get_effective_role(current_user) not in (
        models.UserRole.admin,
        models.UserRole.staff,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "ไม่มีสิทธิ์ดู recheck report")
    return run_optimization_recheck(db, session_id)


@router.get("/sessions/{session_id}/governance")
def get_session_governance_report(
    session_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_view_all),
):
    """Return the full governance report for a session's current allocation.

    Used by the useOptimizationGovernance and useScheduleGovernance hooks.
    Read-only — no side effects.
    """
    session = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")
    period = session.period
    schedules = (
        db.query(models.ExamSchedule)
        .join(models.Section)
        .filter(
            models.Section.academic_year == period.academic_year,
            models.Section.semester == period.semester,
            models.ExamSchedule.exam_type == period.exam_type,
        )
        .options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions),
        )
        .all()
    )
    report = build_optimization_report(period=period, schedules=schedules)
    governance_state = report.get("governance", {}).get("governance_state", "")
    derived_state = derive_schedule_state(session.status, governance_state)
    report["derived_schedule_state"] = derived_state
    report["valid_next_states"] = schedule_state_machine.valid_next_states(derived_state)
    report["session_status"] = session.status
    return report


@router.get("/sessions/{session_id}/publication-readiness")
def get_publication_readiness(
    session_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_view_all),
):
    """Return publication readiness assessment for a session.

    Used by the usePublicationGovernance hook.
    Read-only — no side effects.
    """
    from services.publication_governance_service import assess_publication_readiness
    session = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")
    period = session.period
    schedules = (
        db.query(models.ExamSchedule)
        .join(models.Section)
        .filter(
            models.Section.academic_year == period.academic_year,
            models.Section.semester == period.semester,
            models.ExamSchedule.exam_type == period.exam_type,
        )
        .all()
    )
    report = build_optimization_report(period=period, schedules=schedules)
    governance_dict = report.get("governance", {})
    governance_state = governance_dict.get("governance_state", "")
    derived_state = derive_schedule_state(session.status, governance_state)
    readiness = assess_publication_readiness(
        quality_report=report.get("quality_breakdown", {}),
        governance=governance_dict,
        recheck_summary=report.get("severity_summary", {}),
        schedule_state=derived_state,
    )
    from dataclasses import asdict
    result = asdict(readiness)
    result["derived_schedule_state"] = derived_state
    result["valid_next_states"] = schedule_state_machine.valid_next_states(derived_state)
    result["session_status"] = session.status
    return result


@router.post("/session/init")
def init_session(
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    p = require_active_period_for_mutation(db)
    """เรียกหลัง optimize เสร็จ — reset session เป็น draft"""
    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    sess = get_or_create_workflow_session(db, p.id)
    if sess:
        # reset signatures ทั้งหมด
        for i in range(1, 5):
            setattr(sess, f"sig{i}_user_id", None)
            setattr(sess, f"sig{i}_at",      None)
            setattr(sess, f"sig{i}r2_user_id", None)
            setattr(sess, f"sig{i}r2_at",      None)
        sess.status          = "draft"
        sess.baseline_saved  = False
    else:
        sess = models.OptimizeSession(exam_period_id=p.id, status="draft")
        db.add(sess)

    db.commit()
    db.refresh(sess)
    log_action(db, current_user, "INIT_OPTIMIZE_SESSION", "optimize_sessions",
               record_id=sess.id, request=request)
    return build_session_payload(sess)


@router.post("/session/sign")
def sign_session(
    round:   int,    # 1 หรือ 2
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    p = require_active_period_for_mutation(db)
    """
    กดลายเซ็น — ต้องเป็นคนที่ถึงลำดับ และยังไม่เคยกด
    round=1: ก่อน swap → บันทึก baseline stats เมื่อครบ
    round=2: หลัง swap → lock เมื่อครบ (ไม่บันทึก stat)
    """
    if round not in (1, 2):
        raise HTTPException(400, "round ต้องเป็น 1 หรือ 2")

    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    # SELECT FOR UPDATE — ป้องกัน race condition 2 คนกด slot เดียวกัน
    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).with_for_update().first()
    if not sess:
        sess = get_or_create_workflow_session(db, p.id)
        sess = db.query(models.OptimizeSession).filter(
            models.OptimizeSession.exam_period_id == p.id
        ).with_for_update().first()

    result = apply_signature(sess, current_user, round)

    if result.round_no == 1 and result.completed:
        _save_baseline_stats(db, p)
        sess.baseline_saved = True

    db.commit()

    log_action(db, current_user, audit_action_for_signature(round, result.slot), "optimize_sessions",
               record_id=sess.id, request=request)

    return build_session_payload(sess)


@router.post("/session/open-swap")
def open_swap(
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    p = require_active_period_for_mutation(db)
    """Admin เปิด swap period หลัง round 1 ครบ"""
    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
    open_swap_transition(sess)
    db.commit()

    log_action(db, current_user, "OPEN_SWAP", "optimize_sessions",
               record_id=sess.id, request=request)
    return build_session_payload(sess)


@router.get("/session/signers")
def get_signers_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ข้อมูล 4 คนที่ต้องกดลายเซ็น"""
    signers = []
    for signer in get_signer_list(current_user):
        u = db.query(models.User).filter(models.User.username == signer["username"]).first()
        signers.append({
            "order": signer["order"],
            "username": signer["username"],
            "full_name": u.full_name if u else signer["username"],
            "is_me": signer["is_me"],
        })
    return signers


@router.get("/session/external-issues")
def list_external_workflow_issues(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_view_all),
):
    period = _get_active_period_or_none(db)
    if not period:
        return []
    return _build_external_workflow_issues(db, period.id)


def _resolve_period_for_reporting(db: Session, period_id: Optional[int]) -> models.ExamPeriod:
    if period_id:
        period = db.query(models.ExamPeriod).filter(models.ExamPeriod.id == period_id).first()
    else:
        period = _get_active_period_or_none(db)
    if not period:
        raise HTTPException(400, "ไม่มี active period")
    return period


@router.get("/staff-workload")
def get_staff_workload_report(
    period_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    period = _resolve_period_for_reporting(db, period_id)
    viewer_role = current_user.role.value if current_user.role else None
    return build_staff_workload_report(db, period, viewer_role)


@router.get("/paper-distribution/assignments")
def list_paper_distribution_assignments(
    period_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    period = _resolve_period_for_reporting(db, period_id)
    assignments = db.query(models.PaperDistributionAssignment).options(
        joinedload(models.PaperDistributionAssignment.user)
    ).filter(
        models.PaperDistributionAssignment.exam_period_id == period.id
    ).order_by(
        models.PaperDistributionAssignment.exam_date,
        models.PaperDistributionAssignment.exam_time,
        models.PaperDistributionAssignment.slot_order,
    ).all()

    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
    ).join(models.Section).filter(
        models.Section.academic_year == period.academic_year,
        models.Section.semester == period.semester,
        models.ExamSchedule.exam_type == period.exam_type,
    ).all()

    slot_context: dict[tuple[str, str], dict[str, list[str]]] = {}
    for schedule in schedules:
        key = (str(schedule.exam_date) if schedule.exam_date else "", schedule.exam_time or "")
        context = slot_context.setdefault(key, {"courses": [], "rooms": []})
        if schedule.section and schedule.section.course:
            label = f"{schedule.section.course.course_id} Sec {schedule.section.section_no}"
            if label not in context["courses"]:
                context["courses"].append(label)
        if schedule.room and schedule.room.room_name not in context["rooms"]:
            context["rooms"].append(schedule.room.room_name)

    rows = []
    for assignment in assignments:
        context = slot_context.get((assignment.exam_date, assignment.exam_time), {"courses": [], "rooms": []})
        rows.append(
            {
                "id": assignment.id,
                "user_id": assignment.user_id,
                "staff_name": assignment.user.full_name if assignment.user else f"User #{assignment.user_id}",
                "department": (assignment.user.division or assignment.user.unit) if assignment.user else "",
                "exam_date": assignment.exam_date,
                "exam_time": assignment.exam_time,
                "start_time": assignment.start_time,
                "end_time": assignment.end_time,
                "duty_type": assignment.duty_type.value if assignment.duty_type else models.StaffDutyType.paper_distribution.value,
                "workload_count": assignment.workload_units or 1,
                "covered_schedule_count": assignment.covered_schedule_count or 0,
                "covered_courses": context["courses"],
                "covered_rooms": context["rooms"],
                "assignment_mode": assignment.assignment_mode,
                "notes": assignment.notes,
            }
        )

    return {
        "period": {
            "id": period.id,
            "semester": period.semester,
            "academic_year": period.academic_year,
            "exam_type": period.exam_type,
            "label": period.label,
        },
        "rows": rows,
        "count": len(rows),
    }


@router.get("/staff-availability/staff")
def list_staff_availability_staff(
    period_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    period = _resolve_period_for_reporting(db, period_id)
    snapshot = get_period_workload_snapshot(db, period)
    summary_map = {row["user_id"]: row for row in snapshot["summary"]}
    block_counts = {
        user_id: count
        for user_id, count in db.query(
            models.StaffUnavailability.user_id,
            func.count(models.StaffUnavailability.id),
        ).filter(
            models.StaffUnavailability.exam_period_id == period.id
        ).group_by(models.StaffUnavailability.user_id).all()
    }

    staff = db.query(models.User).filter(
        models.User.role == models.UserRole.staff,
        models.User.is_active == True,
    ).order_by(models.User.full_name).all()

    rows = []
    for user in staff:
        summary = summary_map.get(user.id, {})
        excluded_reason = None
        if user.username in PAPER_DISTRIBUTION_EXCLUDED_USERNAMES:
            excluded_reason = "Excluded by paper-distribution policy"
        elif any(snippet in (user.full_name or "") for snippet in PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS):
            excluded_reason = "Excluded by paper-distribution policy"
        rows.append(
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "division": user.division,
                "unit": user.unit,
                "department": user.department,
                "is_paper_distribution_candidate": is_paper_distribution_candidate(user),
                "excluded_reason": excluded_reason,
                "availability_block_count": int(block_counts.get(user.id, 0) or 0),
                "invigilation_count": int(summary.get("invigilation_count", 0) or 0),
                "paper_distribution_count": int(summary.get("paper_distribution_count", 0) or 0),
                "external_exam_count": int(summary.get("external_exam_count", 0) or 0),
                "total_workload": int(summary.get("total_workload", 0) or 0),
            }
        )

    return {
        "period": {
            "id": period.id,
            "semester": period.semester,
            "academic_year": period.academic_year,
            "exam_type": period.exam_type,
            "label": period.label,
        },
        "rows": rows,
        "count": len(rows),
    }





# ════════════════════════════════════════════════════════════════
# ROOM UNAVAILABILITY
# ════════════════════════════════════════════════════════════════

class RoomUnavailCreate(BaseModel):
    room_id:    int
    block_date: str
    block_time: Optional[str] = None   # None = ทั้งวัน
    start_time: Optional[str] = None
    end_time:   Optional[str] = None
    reason:     Optional[str] = None


def _normalize_room_block_fields(data: RoomUnavailCreate) -> tuple[Optional[str], Optional[str], Optional[str]]:
    start_time = normalize_time_value(data.start_time)
    end_time = normalize_time_value(data.end_time)
    block_time = data.block_time.strip() if isinstance(data.block_time, str) and data.block_time.strip() else None

    if start_time or end_time:
        if not start_time or not end_time:
            raise HTTPException(400, "ต้องระบุทั้ง start_time และ end_time ให้ครบ")
        normalized_block = normalize_time_range(start_time, end_time)
        if not normalized_block:
            raise HTTPException(400, "ช่วงเวลาไม่ถูกต้อง")
        return normalized_block, start_time, end_time

    if block_time:
        normalized_block = normalize_time_range(*parse_time_range(block_time))
        if normalized_block is None:
            raise HTTPException(400, "block_time ไม่ถูกต้อง")
        parsed = parse_time_range(normalized_block)
        start_time = parsed[0] if parsed else None
        end_time = parsed[1] if parsed else None
        return normalized_block, start_time, end_time

    return None, None, None


@router.get("/room-unavailability/")
def list_room_unavailability(
    period_id: Optional[int] = None,
    room_id:   Optional[int] = None,
    db:        Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if not period_id:
        p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
        period_id = p.id if p else None

    q = db.query(models.RoomUnavailability).options(
        joinedload(models.RoomUnavailability.room)
    )
    if period_id:
        q = q.filter(models.RoomUnavailability.exam_period_id == period_id)
    if room_id:
        q = q.filter(models.RoomUnavailability.room_id == room_id)

    rows = q.order_by(
        models.RoomUnavailability.block_date,
        models.RoomUnavailability.block_time
    ).all()

    return [
        {
            "id":         r.id,
            "room_id":    r.room_id,
            "room_name":  r.room.room_name if r.room else None,
            "capacity":   r.room.capacity  if r.room else None,
            "block_date": r.block_date,
            "block_time": normalize_time_range(r.start_time, r.end_time) or normalize_time_range(*parse_time_range(r.block_time)) or r.block_time,
            "start_time": normalize_time_value(r.start_time) or (parse_time_range(r.block_time)[0] if r.block_time and parse_time_range(r.block_time) else None),
            "end_time":   normalize_time_value(r.end_time) or (parse_time_range(r.block_time)[1] if r.block_time and parse_time_range(r.block_time) else None),
            "all_day":    r.block_time is None,
            "reason":     r.reason,
        }
        for r in rows
    ]


@router.post("/room-unavailability/")
def add_room_unavailability(
    data: RoomUnavailCreate,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    p = require_active_period_for_mutation(db)
    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    normalized_block_time, start_time, end_time = _normalize_room_block_fields(data)

    existing = db.query(models.RoomUnavailability).filter(
        and_(
            models.RoomUnavailability.room_id        == data.room_id,
            models.RoomUnavailability.exam_period_id == p.id,
            models.RoomUnavailability.block_date     == data.block_date,
            models.RoomUnavailability.block_time     == normalized_block_time,
        )
    ).first()
    if existing:
        raise HTTPException(400, "มีการ block นี้อยู่แล้ว")

    row = models.RoomUnavailability(
        room_id        = data.room_id,
        exam_period_id = p.id,
        block_date     = data.block_date,
        block_time     = normalized_block_time,
        start_time     = start_time,
        end_time       = end_time,
        reason         = data.reason,
        created_by     = current_user.id,
    )
    db.add(row)
    db.commit()

    room = db.query(models.Room).filter(models.Room.id == data.room_id).first()
    log_action(db, current_user, "ADD_ROOM_UNAVAILABILITY", "room_unavailability",
               record_id=row.id,
               new_values={"room": room.room_name if room else data.room_id,
                           "date": data.block_date, "time": normalized_block_time},
               request=request)
    return {"id": row.id, "status": "added"}


@router.delete("/room-unavailability/{unavail_id}")
def delete_room_unavailability(
    unavail_id: int,
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    row = db.query(models.RoomUnavailability).filter(
        models.RoomUnavailability.id == unavail_id
    ).first()
    if not row:
        raise HTTPException(404, "ไม่พบ")
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.id == row.exam_period_id
    ).first()
    ensure_period_record_editable(period)
    db.delete(row)
    db.commit()
    log_action(db, current_user, "DELETE_ROOM_UNAVAILABILITY", "room_unavailability",
               record_id=unavail_id, request=request)
    return {"status": "deleted"}

# ════════════════════════════════════════════════════════════════
# EDIT LOCK — ป้องกัน admin สองคนแก้พร้อมกัน
# ════════════════════════════════════════════════════════════════

LOCK_TTL_SECONDS = WORKFLOW_LOCK_TTL_SECONDS


def _is_lock_expired(sess: models.OptimizeSession) -> bool:
    return workflow_lock_service.is_lock_expired(sess)


def _get_active_session(db: Session) -> Optional[models.OptimizeSession]:
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        return None
    return db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()


def _assert_editable(sess: models.OptimizeSession, current_user: models.User):
    """
    ตรวจสอบว่า session อยู่ใน state ที่แก้ได้
    และ user นี้ถือ lock อยู่ (หรือ lock หมดอายุแล้ว)
    """
    try:
        workflow_lock_service.assert_session_editable_for_lock(sess, current_user)
    except EMSPermissionError as exc:
        raise HTTPException(403, exc.message)
    except EMSDomainError as exc:
        raise HTTPException(423 if "กำลังถูกแก้ไข" in exc.message else 400, exc.message)


def _acquire_lock(db: Session, sess: models.OptimizeSession,
                  user: models.User) -> None:
    workflow_lock_service.acquire_lock(sess, user)
    db.commit()


@router.post("/session/lock")
def acquire_edit_lock(
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    require_active_period_for_mutation(db)
    """
    Admin ขอ lock ก่อนเริ่มแก้ตาราง
    - ถ้าไม่มีใครถือ lock → ได้ lock ทันที
    - ถ้ามีคนอื่น lock อยู่ และยังไม่หมดอายุ → 423 Locked
    - ถ้า lock หมดอายุ → ได้ lock ทันที
    """
    sess = _get_active_session(db)
    _assert_editable(sess, current_user)

    # ถ้าตัวเองถือ lock อยู่แล้ว → ต่ออายุ
    if sess.edit_lock_user_id == current_user.id or _is_lock_expired(sess):
        _acquire_lock(db, sess, current_user)
        audit_event(
            db,
            current_user,
            "WORKFLOW_LOCK_ACQUIRED",
            table_name="optimize_sessions",
            record_id=sess.id,
            metadata={"exam_period_id": sess.exam_period_id, "lock_ttl_seconds": LOCK_TTL_SECONDS},
            request=request,
        )
        return {
            "status":   "locked",
            "holder":   current_user.full_name,
            "user_id":  current_user.id,
            "expires_in": LOCK_TTL_SECONDS,
            "message":  "ได้รับสิทธิ์แก้ไขแล้ว — จะหมดอายุใน 5 นาที",
        }

    raise HTTPException(423, "ไม่ควรถึงจุดนี้")  # _assert_editable จะ raise ก่อน


@router.post("/session/unlock")
def release_edit_lock(
    request: Request,
    db:      Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    require_active_period_for_mutation(db)
    """Admin ปล่อย lock เมื่อแก้เสร็จ"""
    sess = _get_active_session(db)
    if sess:
        released = workflow_lock_service.release_lock(sess, current_user)
        if released:
            db.commit()
            audit_event(
                db,
                current_user,
                "WORKFLOW_LOCK_RELEASED",
                table_name="optimize_sessions",
                record_id=sess.id,
                metadata={"exam_period_id": sess.exam_period_id},
                request=request,
            )
    return {"status": "unlocked"}


@router.post("/session/heartbeat")
def heartbeat_lock(
    request: Request,
    db:  Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    require_active_period_for_mutation(db)
    """ต่ออายุ lock (frontend เรียกทุก 60 วิ ขณะกำลังแก้อยู่)"""
    sess = _get_active_session(db)
    if sess and workflow_lock_service.heartbeat_lock(sess, current_user):
        db.commit()
        audit_event(
            db,
            current_user,
            "WORKFLOW_LOCK_HEARTBEAT",
            table_name="optimize_sessions",
            record_id=sess.id,
            metadata={"exam_period_id": sess.exam_period_id, "lock_ttl_seconds": LOCK_TTL_SECONDS},
            request=request,
        )
        return {"status": "renewed", "expires_in": LOCK_TTL_SECONDS}
    return {"status": "not_holder"}


@router.get("/session/lock-status")
def get_lock_status(
    db:  Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ดูว่าใครถือ lock อยู่ตอนนี้"""
    sess = _get_active_session(db)
    if not sess or not sess.edit_lock_user_id or _is_lock_expired(sess):
        return {"locked": False, "holder": None, "is_mine": False}

    holder = sess.edit_lock_user
    remaining = workflow_lock_service.remaining_lock_seconds(sess)

    return {
        "locked":       True,
        "holder":       holder.full_name if holder else None,
        "holder_id":    sess.edit_lock_user_id,
        "is_mine":      sess.edit_lock_user_id == current_user.id,
        "remaining_sec": max(0, remaining),
        "session_status": sess.status,
    }


def _save_baseline_stats(db: Session, period: models.ExamPeriod):
    """
    บันทึก SupervisionBaseline จาก Supervision ปัจจุบัน
    เรียกตอน round 1 ครบ 4 ลายเซ็น
    """
    # ดึง sections ของ period นี้
    sections = db.query(models.Section).filter(
        and_(
            models.Section.semester      == period.semester,
            models.Section.academic_year == period.academic_year,
        )
    ).all()
    section_ids = [s.id for s in sections]
    if not section_ids:
        return

    # ดึง schedules
    schedules = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.section_id.in_(section_ids)
    ).all()
    schedule_ids = [s.id for s in schedules]

    # ดึง supervisions
    sups = db.query(models.Supervision).filter(
        models.Supervision.schedule_id.in_(schedule_ids)
    ).all()

    saved = 0
    for sup in sups:
        # เช็ค duplicate
        existing = db.query(models.SupervisionBaseline).filter(
            and_(
                models.SupervisionBaseline.user_id     == sup.user_id,
                models.SupervisionBaseline.schedule_id == sup.schedule_id,
            )
        ).first()
        if not existing:
            db.add(models.SupervisionBaseline(
                user_id      = sup.user_id,
                schedule_id  = sup.schedule_id,
                slot_order   = sup.slot_order,
                role_in_exam = sup.role_in_exam or "supervisor",
            ))
            saved += 1

    db.flush()
    print(f"  📊 Baseline stats saved: {saved} records")


# ── Suggestions / ข้อเสนอแนะ ─────────────────────────────────
class SuggestionCreate(BaseModel):
    message: str
    priority: str = "normal"   # "normal" | "urgent"


@router.post("/session/suggest")
def add_suggestion(
    data: SuggestionCreate,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    p = require_active_period_for_mutation(db)
    """
    ส่งข้อเสนอแนะระหว่าง approve — เฉพาะ esq_head, secretary, admin
    Admin จะเห็นข้อเสนอแนะทั้งหมดในหน้า confirm
    """
    if current_user.role not in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "เฉพาะผู้มีสิทธิ์อนุมัติเท่านั้น")

    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")

    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
    if not sess:
        raise HTTPException(400, "ยังไม่มี optimize session")

    # เก็บใน notes (JSON list)
    import json
    from datetime import datetime, timezone
    notes_raw = sess.notes or "[]"
    try:
        notes = json.loads(notes_raw)
    except Exception:
        notes = []

    notes.append({
        "by":       current_user.full_name,
        "role":     current_user.role.value,
        "message":  data.message,
        "priority": data.priority,
        "at":       datetime.now(timezone.utc).isoformat(),
    })
    sess.notes = json.dumps(notes, ensure_ascii=False)
    db.commit()

    log_action(db, current_user, "ADD_SUGGESTION", "optimize_sessions",
               record_id=sess.id,
               new_values={"message": data.message[:100], "priority": data.priority},
               request=request)

    return {"status": "added", "count": len(notes)}


@router.get("/session/suggestions")
def get_suggestions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ดูข้อเสนอแนะทั้งหมดของ active session"""
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        return {"suggestions": []}

    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
    if not sess or not sess.notes:
        return {"suggestions": []}

    import json
    try:
        notes = json.loads(sess.notes)
    except Exception:
        notes = []
    return {"suggestions": notes, "count": len(notes)}



@router.get("/staff-pool")
def get_staff_pool(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    แสดง staff pool ก่อน optimize:
    - supervisor pool: คนที่จะถูก assign คุมสอบ
    - room_keeper pool: ธีราภัณฑ์ + ชนะชล (เปิด/ปิดห้อง)
    - excluded: หัวหน้างาน, เลขา, esq_head ฯลฯ
    - reminder: ESQ staff ที่อยู่ใน pool (อารยา + สัพพัญญู)
    """
    from auth_utils import is_eligible_supervisor, is_room_keeper, is_esq_staff

    all_staff = db.query(models.User).filter(
        models.User.role == models.UserRole.staff,
        models.User.is_active == True,
    ).order_by(models.User.full_name).all()

    supervisors  = []
    room_keepers = []
    excluded     = []
    esq_remind   = []
    paper_distribution_pool = []
    paper_distribution_excluded = []

    for u in all_staff:
        if is_paper_distribution_candidate(u):
            paper_distribution_pool.append(u)
        else:
            paper_distribution_excluded.append(u)
        if is_room_keeper(u):
            room_keepers.append(u)
        elif not is_eligible_supervisor(u):
            excluded.append(u)
        else:
            supervisors.append(u)
            if is_esq_staff(u):
                esq_remind.append(u)

    def _u(u):
        return {
            "id":           u.id,
            "full_name":    u.full_name,
            "division":     u.division,
            "unit":         u.unit,
            "special_role": getattr(u, "special_role", None),
            "username":     u.username,
        }

    return {
        "supervisor_count":  len(supervisors),
        "room_keeper_count": len(room_keepers),
        "excluded_count":    len(excluded),
        "supervisors":       [_u(u) for u in supervisors],
        "room_keepers":      [_u(u) for u in room_keepers],
        "excluded":          [_u(u) for u in excluded],
        "paper_distribution_pool": [_u(u) for u in paper_distribution_pool],
        "paper_distribution_excluded": [_u(u) for u in paper_distribution_excluded],
        "esq_staff_reminder": {
            "count":   len(esq_remind),
            "message": f"อารยา + สัพพัญญู ({len(esq_remind)} คน) อยู่ใน optimizer pool — ตรวจสอบก่อน optimize",
            "staff":   [_u(u) for u in esq_remind],
        } if esq_remind else None,
    }
