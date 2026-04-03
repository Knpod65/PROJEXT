"""
Period Router — จัดการ Exam Period (รอบสอบ)

ระบบจะมี 1 "active period" เสมอ
  GET  /api/period/              — ดู period ทั้งหมด
  GET  /api/period/active        — period ปัจจุบัน
  POST /api/period/              — สร้าง period ใหม่
  POST /api/period/{id}/activate — เปิดใช้ period นี้
  POST /api/period/rollover      — เริ่มรอบใหม่ (archive + reset active data)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import get_db
import models
from auth_utils import require_admin, get_current_user, log_action
import os, shutil

router = APIRouter()


class PeriodCreate(BaseModel):
    academic_year: str          # "2568"
    semester:      str          # "1" | "2" | "summer"
    exam_type:     str          # "midterm" | "final"
    label:         Optional[str] = None   # "ปลายภาค 2/2568"


class RolloverRequest(BaseModel):
    new_academic_year: str
    new_semester:      str
    new_exam_type:     str
    archive_pdf:       bool = True    # ย้าย PDF เก่าไป archive folder
    pdf_retention_days: int = 180     # เก็บ PDF กี่วัน (0 = เก็บตลอด)


# ── GET /api/period/ ──────────────────────────────────────────
@router.get("/")
def list_periods(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    periods = db.query(models.ExamPeriod).order_by(
        models.ExamPeriod.academic_year.desc(),
        models.ExamPeriod.semester.desc(),
    ).all()

    return [_period_dict(p, db) for p in periods]


# ── GET /api/period/active ────────────────────────────────────
@router.get("/active")
def get_active_period(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        raise HTTPException(404, "ยังไม่มี active period — Admin ต้องสร้างก่อน")
    return _period_dict(p, db)


# ── POST /api/period/ ─────────────────────────────────────────
@router.post("/")
def create_period(
    data: PeriodCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    # ตรวจ duplicate
    existing = db.query(models.ExamPeriod).filter(
        and_(
            models.ExamPeriod.academic_year == data.academic_year,
            models.ExamPeriod.semester      == data.semester,
            models.ExamPeriod.exam_type     == data.exam_type,
        )
    ).first()
    if existing:
        raise HTTPException(400, f"Period นี้มีอยู่แล้ว (id={existing.id})")

    label = data.label or f"{'ปลายภาค' if data.exam_type=='final' else 'กลางภาค'} {data.semester}/{data.academic_year}"
    period = models.ExamPeriod(
        academic_year = data.academic_year,
        semester      = data.semester,
        exam_type     = data.exam_type,
        label         = label,
        is_active     = False,
        created_by    = current_user.id,
    )
    db.add(period)
    db.commit()
    db.refresh(period)

    log_action(db, current_user, "CREATE_PERIOD", "exam_periods",
               record_id=period.id, new_values=data.dict(), request=request)

    return _period_dict(period, db)


# ── POST /api/period/{id}/activate ───────────────────────────
@router.post("/{period_id}/activate")
def activate_period(
    period_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """เปลี่ยน active period — deactivate อันเก่า activate อันใหม่"""
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.id == period_id
    ).first()
    if not period:
        raise HTTPException(404, "ไม่พบ period")

    # Atomic activation: deactivate ทั้งหมด แล้ว activate ใน 1 transaction
    # ป้องกัน race condition: ใช้ UPDATE ไม่ใช่ read-modify-write
    from sqlalchemy import text as _text
    db.execute(_text(
        "UPDATE exam_periods SET is_active = (id = :pid)"
    ), {"pid": period.id})

    # อัปเดต system_settings ให้ตรงกัน
    _update_setting(db, "current_semester",      period.semester,      current_user.id)
    _update_setting(db, "current_academic_year", period.academic_year, current_user.id)

    db.commit()
    log_action(db, current_user, "ACTIVATE_PERIOD", "exam_periods",
               record_id=period.id, request=request)

    return {"status": "ok", "active_period": _period_dict(period, db)}


# ── POST /api/period/rollover ────────────────────────────────
@router.post("/rollover")
def rollover_period(
    data: RolloverRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    เริ่มรอบสอบใหม่:
    1. Archive PDF เก่า (ย้ายไป uploads/archive/YEAR_SEM/)
    2. ตั้งค่า ExamPeriod ใหม่เป็น active
    3. ไม่ลบข้อมูลใด — ข้อมูลเก่าอยู่ครบ แยกด้วย semester+year

    ข้อมูลที่ "reset" คือ:
    - system_settings: current_semester, current_academic_year
    - swap_enabled: true (เปิดใหม่)
    - deadline settings: ล้าง

    ข้อมูลที่ยังอยู่ครบ:
    - users, rooms, courses (ใช้ร่วมได้)
    - sections, exam_schedules, supervisions (กรอง semester+year เอง)
    - submissions, enrollment_records (กรอง semester+year เอง)
    - audit_logs (ประวัติทั้งหมด)
    """
    # 1. สร้าง/หา period ใหม่
    label = f"{'ปลายภาค' if data.new_exam_type=='final' else 'กลางภาค'} {data.new_semester}/{data.new_academic_year}"
    new_period = db.query(models.ExamPeriod).filter(
        and_(
            models.ExamPeriod.academic_year == data.new_academic_year,
            models.ExamPeriod.semester      == data.new_semester,
            models.ExamPeriod.exam_type     == data.new_exam_type,
        )
    ).first()
    if not new_period:
        new_period = models.ExamPeriod(
            academic_year = data.new_academic_year,
            semester      = data.new_semester,
            exam_type     = data.new_exam_type,
            label         = label,
            is_active     = False,
            created_by    = current_user.id,
        )
        db.add(new_period)
        db.flush()

    # 2. Archive PDF เก่า
    archived_files = 0
    deleted_files  = 0
    if data.archive_pdf:
        old_period = db.query(models.ExamPeriod).filter(
            models.ExamPeriod.is_active == True
        ).first()

        if old_period:
            archive_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "uploads", "archive",
                f"{old_period.academic_year}_{old_period.semester}_{old_period.exam_type}"
            )
            os.makedirs(archive_dir, exist_ok=True)

            # หา submissions ที่มี PDF
            subs = db.query(models.ExamSubmission).join(models.Section).filter(
                and_(
                    models.Section.semester      == old_period.semester,
                    models.Section.academic_year == old_period.academic_year,
                )
            ).all()

            cutoff = None
            if data.pdf_retention_days > 0:
                cutoff = datetime.now(timezone.utc) - timedelta(days=data.pdf_retention_days)

            for sub in subs:
                for path_attr in ["pdf_stripped_path", "pdf_original_path"]:
                    fpath = getattr(sub, path_attr, None)
                    if not fpath or not os.path.exists(fpath):
                        continue
                    fname = os.path.basename(fpath)
                    dest  = os.path.join(archive_dir, fname)
                    if cutoff and os.path.getmtime(fpath) < cutoff.timestamp():
                        # เกินอายุ — ลบทิ้ง
                        os.remove(fpath)
                        setattr(sub, path_attr, None)
                        deleted_files += 1
                    else:
                        # ย้ายไป archive
                        shutil.move(fpath, dest)
                        setattr(sub, path_attr, dest)
                        archived_files += 1

            db.flush()

    # 3. Atomic activation — ป้องกัน race condition
    from sqlalchemy import text as _text
    db.execute(_text(
        "UPDATE exam_periods SET is_active = (id = :pid)"
    ), {"pid": new_period.id})

    # 4. อัปเดต settings
    _update_setting(db, "current_semester",          data.new_semester,      current_user.id)
    _update_setting(db, "current_academic_year",     data.new_academic_year, current_user.id)
    _update_setting(db, "swap_enabled",              "true",                 current_user.id)
    _update_setting(db, "exam_submission_deadline",  None,                   current_user.id)
    _update_setting(db, "swap_request_deadline",     None,                   current_user.id)

    db.commit()

    log_action(db, current_user, "ROLLOVER", "exam_periods",
               record_id=new_period.id,
               new_values={
                   "new_period": label,
                   "archived_files": archived_files,
                   "deleted_files":  deleted_files,
               },
               request=request)

    return {
        "status":          "ok",
        "new_period":      _period_dict(new_period, db),
        "archived_files":  archived_files,
        "deleted_files":   deleted_files,
        "note":            "ข้อมูลเก่ายังอยู่ครบใน DB — แยกด้วย semester+year อัตโนมัติ",
    }


# ── GET /api/period/{id}/stats ───────────────────────────────
@router.get("/{period_id}/stats")
def period_stats(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """สรุปสถิติของ period นั้น"""
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.id == period_id
    ).first()
    if not p:
        raise HTTPException(404, "ไม่พบ period")

    sections = db.query(models.Section).filter(
        and_(
            models.Section.semester      == p.semester,
            models.Section.academic_year == p.academic_year,
        )
    ).all()

    section_ids = [s.id for s in sections]

    schedules = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.section_id.in_(section_ids),
        models.ExamSchedule.exam_type == p.exam_type,
    ).all() if section_ids else []

    submissions = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.section_id.in_(section_ids)
    ).all() if section_ids else []

    enrollments = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.section_id.in_(section_ids)
    ).count() if section_ids else 0

    sub_by_status = {}
    for s in submissions:
        k = s.status.value if s.status else "draft"
        sub_by_status[k] = sub_by_status.get(k, 0) + 1

    return {
        "period":          _period_dict(p, db),
        "sections":        len(sections),
        "scheduled":       len(schedules),
        "total_students":  sum(s.num_students or 0 for s in sections),
        "enrollment_records": enrollments,
        "submissions":     len(submissions),
        "submissions_by_status": sub_by_status,
        "total_sheets":    sum(s.total_sheets or 0 for s in schedules),
    }


# ── helpers ───────────────────────────────────────────────────
def _period_dict(p: "models.ExamPeriod", db: Session) -> dict:
    return {
        "id":           p.id,
        "academic_year": p.academic_year,
        "semester":     p.semester,
        "exam_type":    p.exam_type,
        "label":        p.label,
        "is_active":    p.is_active,
        "created_at":   p.created_at.isoformat() if p.created_at else None,
    }


def _update_setting(db: Session, key: str, value, user_id: int):
    row = db.query(models.SystemSetting).filter(
        models.SystemSetting.key == key
    ).first()
    if row:
        row.value      = value
        row.updated_by = user_id
    else:
        db.add(models.SystemSetting(key=key, value=value, updated_by=user_id))
