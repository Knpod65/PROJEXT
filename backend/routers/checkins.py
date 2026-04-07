"""
Checkin Router — Staff check-in system with multi-party confirmation
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
import models
from auth_utils import get_current_user, log_action
from datetime import datetime, timezone

router = APIRouter()


class CheckinCreate(BaseModel):
    schedule_id:      int
    checkin_type:     models.CheckinType
    students_present: Optional[int] = None
    late_count:       Optional[int] = 0
    absent_student_ids: Optional[List[str]] = None
    notes:            Optional[str] = None


class ConfirmCheckin(BaseModel):
    checkin_id: int


@router.get("/schedule/{schedule_id}")
def get_checkins_for_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    events = db.query(models.CheckinEvent).options(
        joinedload(models.CheckinEvent.user),
    ).filter(
        models.CheckinEvent.schedule_id == schedule_id
    ).all()

    return [
        {
            "id": e.id,
            "user": e.user.full_name if e.user else None,
            "checkin_type": e.checkin_type,
            "checked_in_at": e.checked_in_at.isoformat() if e.checked_in_at else None,
            "students_present": e.students_present,
            "late_count": e.late_count,
            "absent_count": len(e.absent_student_ids or []),
            "notes": e.notes,
            "confirmed": e.confirmed,
            "confirmed_by_all": e.confirmed_by_all,
            "confirmations": e.confirmations or {},
        }
        for e in events
    ]


@router.post("/")
def create_checkin(
    data: CheckinCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # ตรวจว่า user นี้ assigned กับ schedule นี้
    is_supervisor = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == data.schedule_id,
        models.Supervision.user_id == current_user.id,
    ).first()

    is_teacher = db.query(models.ExamSchedule).join(models.Section).filter(
        models.ExamSchedule.id == data.schedule_id,
        models.Section.teacher_id == current_user.id,
    ).first()

    if not is_supervisor and not is_teacher:
        raise HTTPException(403, "คุณไม่ได้รับ assign ให้ดูแลการสอบนี้")

    # ป้องกัน check-in ซ้ำ
    existing = db.query(models.CheckinEvent).filter(
        models.CheckinEvent.schedule_id == data.schedule_id,
        models.CheckinEvent.user_id == current_user.id,
        models.CheckinEvent.checkin_type == data.checkin_type,
    ).first()
    if existing:
        raise HTTPException(400, "คุณ check-in ประเภทนี้ไปแล้ว")

    event = models.CheckinEvent(
        schedule_id        = data.schedule_id,
        user_id            = current_user.id,
        checkin_type       = data.checkin_type,
        students_present   = data.students_present,
        late_count         = data.late_count or 0,
        absent_student_ids = data.absent_student_ids or [],
        notes              = data.notes,
        confirmations      = {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    log_action(db, current_user, f"CHECKIN_{data.checkin_type.upper()}",
               "checkin_events", event.id, request=request)
    return {"success": True, "checkin_id": event.id}


@router.post("/confirm")
def confirm_checkin_data(
    data: ConfirmCheckin,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Multi-party confirmation — ทุกคนที่ดูแลต้อง confirm"""
    event = db.query(models.CheckinEvent).filter(
        models.CheckinEvent.id == data.checkin_id
    ).first()
    if not event:
        raise HTTPException(404, "ไม่พบ check-in event")

    # SECURITY: verify caller is actually assigned to this schedule
    is_supervisor = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == event.schedule_id,
        models.Supervision.user_id == current_user.id,
    ).first()
    is_teacher = db.query(models.ExamSchedule).join(models.Section).filter(
        models.ExamSchedule.id == event.schedule_id,
        models.Section.teacher_id == current_user.id,
    ).first()
    if not is_supervisor and not is_teacher:
        raise HTTPException(403, "คุณไม่ได้รับมอบหมายให้ดูแลการสอบนี้")

    # บันทึก confirmation ของ user นี้
    confirmations = event.confirmations or {}
    confirmations[str(current_user.id)] = datetime.now(timezone.utc).isoformat()
    event.confirmations = confirmations
    event.confirmed = True

    # ตรวจว่าทุกคนที่เกี่ยวข้องกด confirm หมดแล้วหรือยัง
    supervisors = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == event.schedule_id
    ).all()
    supervisor_ids = {str(s.user_id) for s in supervisors}

    schedule = db.query(models.ExamSchedule).join(models.Section).filter(
        models.ExamSchedule.id == event.schedule_id
    ).first()
    if schedule and schedule.section and schedule.section.teacher_id:
        supervisor_ids.add(str(schedule.section.teacher_id))

    if supervisor_ids.issubset(set(confirmations.keys())):
        event.confirmed_by_all = True

    db.commit()
    log_action(db, current_user, "CHECKIN_CONFIRM", "checkin_events",
               event.id, request=request)
    return {
        "success": True,
        "confirmed_by_all": event.confirmed_by_all,
        "confirmed_count": len(confirmations),
        "total_required": len(supervisor_ids),
    }
