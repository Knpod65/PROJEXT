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
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import models
from auth_utils import (
    require_admin, get_current_user, log_action, hash_password, get_effective_role,
    SIGN_ORDER_USERNAMES, is_signer
)
from term_lifecycle import ensure_period_record_editable, require_active_period_for_mutation
from time_ranges import normalize_time_range, normalize_time_value, parse_time_range

router = APIRouter()

# ── ลำดับลายเซ็น 4 คน (username) ──────────────────────────────
# Round 1 & 2 ใช้ลำดับเดียวกัน
SIGN_ORDER = SIGN_ORDER_USERNAMES  # defined in auth_utils

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
        try:
            role_enum = models.UserRole(role)
            q = q.filter(models.User.role == role_enum)
        except ValueError:
            raise HTTPException(400, f"role ไม่ถูกต้อง: {role}")
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

    try:
        role_enum = models.UserRole(data.role)
    except ValueError:
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
        try:
            user.role = models.UserRole(data.role)
        except ValueError:
            raise HTTPException(400, f"role ไม่ถูกต้อง: {data.role}")
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
    return {
        "id":          u.id,
        "username":    u.username,
        "email":       u.email,
        "role":        u.role.value if u.role else None,
        "full_name":   u.full_name,
        "title":       u.title,
        "division":    u.division,
        "unit":        u.unit,
        "dept_code":   u.dept_code,
        "mobile":      u.mobile,
        "ext":         u.ext,
        "employee_id": u.employee_id,
        "is_active":   u.is_active,
    }


# ════════════════════════════════════════════════════════════════
# STAFF UNAVAILABILITY
# ════════════════════════════════════════════════════════════════

class UnavailCreate(BaseModel):
    user_id:    int
    block_date: str              # "2026-03-23"
    block_time: Optional[str] = None   # None = ทั้งวัน
    reason:     Optional[str] = None


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
            "block_date": r.block_date,
            "block_time": r.block_time,
            "all_day":    r.block_time is None,
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

    # เช็ค duplicate
    existing = db.query(models.StaffUnavailability).filter(
        and_(
            models.StaffUnavailability.user_id        == data.user_id,
            models.StaffUnavailability.exam_period_id == p.id,
            models.StaffUnavailability.block_date     == data.block_date,
            models.StaffUnavailability.block_time     == data.block_time,
        )
    ).first()
    if existing:
        raise HTTPException(400, "มีการ block นี้อยู่แล้ว")

    row = models.StaffUnavailability(
        user_id        = data.user_id,
        exam_period_id = p.id,
        block_date     = data.block_date,
        block_time     = data.block_time,
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
                           "date": data.block_date, "time": data.block_time},
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
# OPTIMIZE SESSION — 4-signature workflow
# ════════════════════════════════════════════════════════════════

def _get_or_create_session(db: Session, period_id: int) -> models.OptimizeSession:
    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == period_id
    ).first()
    if not sess:
        sess = models.OptimizeSession(exam_period_id=period_id, status="draft")
        db.add(sess)
        db.flush()
    return sess


def _session_dict(sess: models.OptimizeSession) -> dict:
    sigs_r1 = [
        {"order": i+1, "username": SIGN_ORDER[i],
         "user_id": getattr(sess, f"sig{i+1}_user_id"),
         "signed_at": getattr(sess, f"sig{i+1}_at").isoformat()
                      if getattr(sess, f"sig{i+1}_at") else None}
        for i in range(4)
    ]
    sigs_r2 = [
        {"order": i+1, "username": SIGN_ORDER[i],
         "user_id": getattr(sess, f"sig{i+1}r2_user_id"),
         "signed_at": getattr(sess, f"sig{i+1}r2_at").isoformat()
                      if getattr(sess, f"sig{i+1}r2_at") else None}
        for i in range(4)
    ]
    r1_done = sum(1 for s in sigs_r1 if s["signed_at"])
    r2_done = sum(1 for s in sigs_r2 if s["signed_at"])
    return {
        "id":              sess.id,
        "exam_period_id":  sess.exam_period_id,
        "status":          sess.status,
        "baseline_saved":  sess.baseline_saved,
        "round1": {"signatures": sigs_r1, "done": r1_done, "total": 4, "complete": r1_done == 4},
        "round2": {"signatures": sigs_r2, "done": r2_done, "total": 4, "complete": r2_done == 4},
        "next_signer_r1":  SIGN_ORDER[r1_done] if r1_done < 4 else None,
        "next_signer_r2":  SIGN_ORDER[r2_done] if r2_done < 4 else None,
    }


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
    return _session_dict(sess)


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

    sess = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
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
    return _session_dict(sess)


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
        sess = _get_or_create_session(db, p.id)
        # re-lock after create
        sess = db.query(models.OptimizeSession).filter(
            models.OptimizeSession.exam_period_id == p.id
        ).with_for_update().first()

    # ตรวจสอบสถานะ
    if round == 1 and sess.status not in ("draft", "confirming"):
        raise HTTPException(400, f"ไม่อยู่ใน state ที่ sign round 1 ได้ (status={sess.status})")
    if round == 2 and sess.status not in ("swap_open", "swap_confirming"):
        raise HTTPException(400, f"ยังไม่ได้เปิด swap หรือ status ไม่ถูก (status={sess.status})")

    # หาตำแหน่งที่ว่าง
    prefix = "" if round == 1 else "r2"
    slot   = None
    for i in range(1, 5):
        uid_key = f"sig{i}{prefix}_user_id"
        if getattr(sess, uid_key) is None:
            slot = i
            break

    if slot is None:
        raise HTTPException(400, "ลายเซ็นครบแล้ว")

    # ตรวจว่าเป็นคนที่ถูกต้องตามลำดับ
    expected_username = SIGN_ORDER[slot - 1]
    if current_user.username != expected_username:
        raise HTTPException(403,
            f"ลำดับที่ {slot} ต้องเป็น {expected_username} เท่านั้น "
            f"(คุณคือ {current_user.username})")

    # บันทึก
    setattr(sess, f"sig{slot}{prefix}_user_id", current_user.id)
    setattr(sess, f"sig{slot}{prefix}_at",      datetime.now(timezone.utc))
    sess.status = "confirming" if round == 1 else "swap_confirming"

    # ครบ 4 คน
    if slot == 4:
        if round == 1:
            sess.status = "confirmed"
            # บันทึก baseline stats
            _save_baseline_stats(db, p)
            sess.baseline_saved = True
        else:
            sess.status = "locked"

    db.commit()

    log_action(db, current_user, f"SIGN_R{round}_SLOT{slot}", "optimize_sessions",
               record_id=sess.id, request=request)

    return _session_dict(sess)


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
    if not sess or sess.status != "confirmed":
        raise HTTPException(400, "ต้อง confirm round 1 ครบก่อน (4 ลายเซ็น)")

    sess.status = "swap_open"
    db.commit()

    log_action(db, current_user, "OPEN_SWAP", "optimize_sessions",
               record_id=sess.id, request=request)
    return _session_dict(sess)


@router.get("/session/signers")
def get_signers_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ข้อมูล 4 คนที่ต้องกดลายเซ็น"""
    signers = []
    for i, uname in enumerate(SIGN_ORDER):
        u = db.query(models.User).filter(models.User.username == uname).first()
        signers.append({
            "order":     i + 1,
            "username":  uname,
            "full_name": u.full_name if u else uname,
            "is_me":     current_user.username == uname,
        })
    return signers





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
        normalized_block = normalize_time_range(block_time)
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
            "block_time": normalize_time_range(r.start_time, r.end_time) or normalize_time_range(r.block_time) or r.block_time,
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

LOCK_TTL_SECONDS = 300   # 5 นาที — expire อัตโนมัติ


def _is_lock_expired(sess: models.OptimizeSession) -> bool:
    if not sess.edit_lock_at:
        return True
    elapsed = (datetime.now(timezone.utc) - sess.edit_lock_at).total_seconds()
    return elapsed > LOCK_TTL_SECONDS


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
    if sess is None:
        raise HTTPException(400, "ยังไม่มี optimize session")
    if sess.status not in ("draft",):
        raise HTTPException(400,
            f"ไม่สามารถแก้ไขได้ — session status='{sess.status}' "
            "(ต้องอยู่ใน draft เท่านั้น)")
    # ตรวจสิทธิ์ลงนาม
    if not is_signer(current_user):
        raise HTTPException(403, "เฉพาะผู้มีสิทธิ์ลงนามเท่านั้น (admin / esq_head / secretary)")

    # ตรวจ lock
    if sess.edit_lock_user_id and sess.edit_lock_user_id != current_user.id:
        if not _is_lock_expired(sess):
            holder = sess.edit_lock_user
            name   = holder.full_name if holder else f"user#{sess.edit_lock_user_id}"
            remaining = int(LOCK_TTL_SECONDS -
                (datetime.now(timezone.utc) - sess.edit_lock_at).total_seconds())
            raise HTTPException(423,
                f"กำลังถูกแก้ไขโดย {name} "
                f"(หมดอายุใน {remaining} วินาที)")


def _acquire_lock(db: Session, sess: models.OptimizeSession,
                  user: models.User) -> None:
    sess.edit_lock_user_id = user.id
    sess.edit_lock_at      = datetime.now(timezone.utc)
    db.commit()


def _release_lock(db: Session, sess: models.OptimizeSession,
                  user: models.User) -> None:
    if sess.edit_lock_user_id == user.id:
        sess.edit_lock_user_id = None
        sess.edit_lock_at      = None
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
        _release_lock(db, sess, current_user)
    return {"status": "unlocked"}


@router.post("/session/heartbeat")
def heartbeat_lock(
    db:  Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    require_active_period_for_mutation(db)
    """ต่ออายุ lock (frontend เรียกทุก 60 วิ ขณะกำลังแก้อยู่)"""
    sess = _get_active_session(db)
    if sess and sess.edit_lock_user_id == current_user.id:
        sess.edit_lock_at = datetime.now(timezone.utc)
        db.commit()
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
    remaining = int(LOCK_TTL_SECONDS -
        (datetime.now(timezone.utc) - sess.edit_lock_at).total_seconds())

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

    for u in all_staff:
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
        "esq_staff_reminder": {
            "count":   len(esq_remind),
            "message": f"อารยา + สัพพัญญู ({len(esq_remind)} คน) อยู่ใน optimizer pool — ตรวจสอบก่อน optimize",
            "staff":   [_u(u) for u in esq_remind],
        } if esq_remind else None,
    }
