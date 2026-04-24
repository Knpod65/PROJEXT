"""
Checkin Router — Staff check-in system with multi-party confirmation
"""
import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
import models
from auth_utils import get_current_user, log_action, require_staff_or_admin
from exam_pickup import (
    build_pickup_assignments,
    describe_pickup_status,
    ensure_schedule_ready_for_pickup,
    extract_pickup_token,
    get_active_pickup_qr,
    get_pickup_scan_window,
    get_schedule_start_datetime,
    get_successful_pickup_checkin,
    get_user_pickup_assignment,
    hash_pickup_token,
    now_local,
)

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


class PickupQrScanRequest(BaseModel):
    qr_value: str
    allow_late_override: bool = False
    device_metadata: Optional[dict[str, object]] = None


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


def _schedule_pickup_summary(schedule: models.ExamSchedule) -> dict[str, object]:
    section = schedule.section
    course = section.course if section else None
    teacher = section.teacher if section else None
    return {
        "schedule_id": schedule.id,
        "course_code": course.course_id if course else None,
        "course_name": (course.course_name_th or course.course_name_en) if course else None,
        "section_no": section.section_no if section else None,
        "room_name": schedule.room.room_name if schedule.room else None,
        "exam_date": schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
        "exam_time": schedule.exam_time,
        "teacher_name": teacher.full_name if teacher else None,
    }


def _record_pickup_attempt(
    db: Session,
    *,
    qr_token: models.ExamPickupQrToken | None,
    schedule: models.ExamSchedule | None,
    user: models.User,
    role: str | None,
    status: models.PickupCheckinStatus,
    message: str,
    duplicate_attempt: bool = False,
    device_metadata: Optional[dict[str, object]] = None,
    token_hash: str | None = None,
) -> models.ExamPickupCheckin:
    row = models.ExamPickupCheckin(
        qr_token_id=qr_token.id if qr_token else None,
        schedule_id=schedule.id if schedule else None,
        user_id=user.id,
        role=role,
        scanned_at=datetime.now(timezone.utc),
        status=status,
        message=message,
        duplicate_attempt=duplicate_attempt,
        token_version=qr_token.version if qr_token else None,
        token_hash=token_hash or (qr_token.token_hash if qr_token else None),
        device_metadata=device_metadata or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/pickup/scan")
def scan_pickup_qr(
    data: PickupQrScanRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    raw_token = extract_pickup_token(data.qr_value)
    hashed_token = hash_pickup_token(raw_token) if raw_token else hashlib.sha256((data.qr_value or "").encode("utf-8")).hexdigest()

    if not raw_token:
        log_action(
            db,
            current_user,
            "PICKUP_SCAN_INVALID",
            "exam_pickup_checkins",
            new_values={
                "status": models.PickupCheckinStatus.invalid_token.value,
                "message": "ไม่สามารถอ่าน QR X นี้ได้",
                "token_hash": hashed_token,
                "device_metadata": data.device_metadata or {},
            },
            request=request,
        )
        raise HTTPException(400, "ไม่สามารถอ่าน QR X นี้ได้")

    qr_token = db.query(models.ExamPickupQrToken).options(
        joinedload(models.ExamPickupQrToken.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamPickupQrToken.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.teacher),
        joinedload(models.ExamPickupQrToken.schedule)
            .joinedload(models.ExamSchedule.room),
        joinedload(models.ExamPickupQrToken.schedule)
            .joinedload(models.ExamSchedule.supervisions)
            .joinedload(models.Supervision.user),
    ).filter(
        models.ExamPickupQrToken.token_hash == hashed_token,
        models.ExamPickupQrToken.qr_type == models.PickupQrType.invigilator_pickup,
    ).order_by(models.ExamPickupQrToken.version.desc()).first()

    if not qr_token or not qr_token.schedule:
        log_action(
            db,
            current_user,
            "PICKUP_SCAN_INVALID",
            "exam_pickup_checkins",
            new_values={
                "status": models.PickupCheckinStatus.invalid_token.value,
                "message": "QR X นี้ไม่ถูกต้องหรือหมดอายุแล้ว",
                "token_hash": hashed_token,
                "device_metadata": data.device_metadata or {},
            },
            request=request,
        )
        raise HTTPException(400, "QR X นี้ไม่ถูกต้องหรือหมดอายุแล้ว")

    schedule = qr_token.schedule
    ensure_schedule_ready_for_pickup(db, schedule)

    if not qr_token.is_active or qr_token.revoked_at:
        attempt = _record_pickup_attempt(
            db,
            qr_token=qr_token,
            schedule=schedule,
            user=current_user,
            role=current_user.role.value if current_user.role else None,
            status=models.PickupCheckinStatus.inactive_token,
            message="QR X นี้ไม่ใช่เวอร์ชันที่ใช้งานอยู่ในขณะนี้",
            device_metadata=data.device_metadata,
        )
        log_action(db, current_user, "PICKUP_SCAN_INACTIVE", "exam_pickup_checkins", attempt.id, request=request)
        raise HTTPException(400, "QR X นี้ไม่ใช่เวอร์ชันที่ใช้งานอยู่ในขณะนี้")

    assignment = get_user_pickup_assignment(db, schedule, current_user)
    if not assignment:
        attempt = _record_pickup_attempt(
            db,
            qr_token=qr_token,
            schedule=schedule,
            user=current_user,
            role=current_user.role.value if current_user.role else None,
            status=models.PickupCheckinStatus.unassigned_user,
            message="คุณไม่ได้รับมอบหมายให้รับข้อสอบสำหรับวิชา/ห้อง/เวลานี้",
            device_metadata=data.device_metadata,
        )
        log_action(db, current_user, "PICKUP_SCAN_UNASSIGNED", "exam_pickup_checkins", attempt.id, request=request)
        raise HTTPException(403, "คุณไม่ได้รับมอบหมายให้รับข้อสอบสำหรับวิชา/ห้อง/เวลานี้")

    existing = get_successful_pickup_checkin(db, schedule.id, current_user.id)
    if existing:
        attempt = _record_pickup_attempt(
            db,
            qr_token=qr_token,
            schedule=schedule,
            user=current_user,
            role=str(assignment.get("role") or current_user.role.value),
            status=models.PickupCheckinStatus.duplicate,
            message="คุณได้เช็คอินรับข้อสอบสำหรับรายการนี้แล้ว",
            duplicate_attempt=True,
            device_metadata=data.device_metadata,
        )
        log_action(db, current_user, "PICKUP_SCAN_DUPLICATE", "exam_pickup_checkins", attempt.id, request=request)
        raise HTTPException(400, "คุณได้เช็คอินรับข้อสอบสำหรับรายการนี้แล้ว")

    current_time = now_local()
    fallback_valid_from, fallback_valid_until = get_pickup_scan_window(schedule)
    valid_from = qr_token.valid_from or fallback_valid_from
    valid_until = qr_token.valid_until or fallback_valid_until or get_schedule_start_datetime(schedule)
    is_late = bool(valid_until and current_time > valid_until)
    is_early = bool(valid_from and current_time < valid_from)

    if is_early or is_late:
        can_override_late = (
            is_late
            and data.allow_late_override
            and current_user.role == models.UserRole.admin
        )
        if not can_override_late:
            message = "ยังไม่อยู่ในช่วงเวลาที่สามารถยืนยันการรับข้อสอบได้" if is_early else "เลยเวลาเริ่มสอบแล้ว ต้องใช้งาน admin override หากจำเป็น"
            attempt = _record_pickup_attempt(
                db,
                qr_token=qr_token,
                schedule=schedule,
                user=current_user,
                role=str(assignment.get("role") or current_user.role.value),
                status=models.PickupCheckinStatus.outside_window,
                message=message,
                device_metadata=data.device_metadata,
            )
            log_action(db, current_user, "PICKUP_SCAN_OUTSIDE_WINDOW", "exam_pickup_checkins", attempt.id, request=request)
            raise HTTPException(400, message)
        status = models.PickupCheckinStatus.late_override
    else:
        status = models.PickupCheckinStatus.success

    course = schedule.section.course if schedule.section and schedule.section.course else None
    teacher_name = schedule.section.teacher.full_name if schedule.section and schedule.section.teacher else "-"
    success_message = (
        f"คุณได้รับข้อสอบกระบวนวิชา {course.course_id if course else '-'} "
        f"ตอน {schedule.section.section_no if schedule.section else '-'} "
        f"ห้อง {schedule.room.room_name if schedule.room else '-'} "
        f"อาจารย์ประจำวิชา {teacher_name} "
        f"เวลา {schedule.exam_time or '-'} เรียบร้อยแล้ว"
    )
    attempt = _record_pickup_attempt(
        db,
        qr_token=qr_token,
        schedule=schedule,
        user=current_user,
        role=str(assignment.get("role") or current_user.role.value),
        status=status,
        message=success_message,
        device_metadata=data.device_metadata,
    )
    log_action(db, current_user, "PICKUP_SCAN_SUCCESS", "exam_pickup_checkins", attempt.id, request=request)
    return {
        "success": True,
        "status": status.value if hasattr(status, "value") else str(status),
        "message": success_message,
        "schedule": _schedule_pickup_summary(schedule),
        "assignment": assignment,
        "checked_in_at": attempt.scanned_at.isoformat() if attempt.scanned_at else None,
        "qr_version": qr_token.version,
    }


@router.get("/pickup/monitor")
def get_pickup_monitor(
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    active_period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not active_period:
        return []

    workflow_session = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == active_period.id
    ).first()
    if not workflow_session or (not workflow_session.sig4_at and workflow_session.status not in {"confirmed", "swap_open", "swap_confirming", "locked"}):
        return []

    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        joinedload(models.ExamSchedule.pickup_checkins),
        joinedload(models.ExamSchedule.pickup_qr_tokens),
    ).join(models.Section).filter(
        models.Section.academic_year == active_period.academic_year,
        models.Section.semester == active_period.semester,
        models.ExamSchedule.exam_type == models.ExamType(active_period.exam_type),
    ).order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time,
        models.ExamSchedule.id,
    ).all()

    rows: list[dict[str, object]] = []
    for schedule in schedules:
        if date and str(schedule.exam_date) != date:
            continue
        if not schedule.room_id or not schedule.room:
            continue

        assignments = build_pickup_assignments(db, schedule)
        active_qr = get_active_pickup_qr(db, schedule.id)
        latest_qr = db.query(models.ExamPickupQrToken).filter(
            models.ExamPickupQrToken.schedule_id == schedule.id,
            models.ExamPickupQrToken.qr_type == models.PickupQrType.invigilator_pickup,
        ).order_by(models.ExamPickupQrToken.version.desc()).first()

        for assignment in assignments:
            success = None
            latest = None
            for item in sorted(schedule.pickup_checkins or [], key=lambda row: row.scanned_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
                if item.user_id != assignment["user_id"]:
                    continue
                if latest is None:
                    latest = item
                if item.status in (models.PickupCheckinStatus.success, models.PickupCheckinStatus.late_override):
                    success = item
                    break

            rows.append(
                {
                    "schedule_id": schedule.id,
                    "date": schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
                    "time": schedule.exam_time,
                    "course_code": schedule.section.course.course_id if schedule.section and schedule.section.course else None,
                    "course_name": (schedule.section.course.course_name_th or schedule.section.course.course_name_en) if schedule.section and schedule.section.course else None,
                    "section_no": schedule.section.section_no if schedule.section else None,
                    "room_name": schedule.room.room_name if schedule.room else None,
                    "assigned_person": assignment["full_name"],
                    "role": assignment["role"],
                    "checkin_status": describe_pickup_status(schedule, success.scanned_at if success else None),
                    "checkin_time": success.scanned_at.isoformat() if success and success.scanned_at else None,
                    "latest_message": latest.message if latest else None,
                    "active_qr_version": active_qr.version if active_qr else None,
                    "latest_qr_version": latest_qr.version if latest_qr else None,
                    "has_pending_regeneration": bool(latest_qr and not latest_qr.is_active),
                    "action_details": {
                        "checkin_id": success.id if success else None,
                        "duplicate_attempt": bool(latest.duplicate_attempt) if latest else False,
                    },
                }
            )

    return rows
