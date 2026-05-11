from __future__ import annotations

import hashlib
import os
import secrets
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from config.policy import EMS_LOCAL_TIMEZONE, PICKUP_QR_OPEN_MINUTES_BEFORE, QR_PICKUP_PREFIX, QR_REGULATION_PREFIX
from time_ranges import parse_time_range


def now_local() -> datetime:
    return datetime.now(EMS_LOCAL_TIMEZONE)


def hash_pickup_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def wrap_pickup_token(token: str, qr_type: models.PickupQrType = models.PickupQrType.invigilator_pickup) -> str:
    prefix = QR_PICKUP_PREFIX if qr_type == models.PickupQrType.invigilator_pickup else QR_REGULATION_PREFIX
    return f"{prefix}{token}"


def extract_pickup_token(raw_value: str | None) -> str | None:
    text = (raw_value or "").strip()
    if not text:
        return None

    for prefix in (QR_PICKUP_PREFIX, QR_REGULATION_PREFIX):
        if text.startswith(prefix):
            return text[len(prefix):].strip() or None

    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        query = parse_qs(parsed.query)
        for key in ("token", "pickup_token", "qr"):
            values = query.get(key)
            if values and values[0].strip():
                return values[0].strip()
        if parsed.fragment.strip():
            return parsed.fragment.strip()

    return text


def _coerce_exam_date(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def get_schedule_start_datetime(schedule: models.ExamSchedule) -> datetime | None:
    exam_date = _coerce_exam_date(schedule.exam_date)
    if not exam_date:
        return None
    start_time = schedule.exam_time_start or parse_time_range(schedule.exam_time)[0]
    if not start_time:
        return None
    try:
        start = time.fromisoformat(start_time)
    except ValueError:
        return None
    return datetime.combine(exam_date, start).replace(tzinfo=LOCAL_TIMEZONE)


def get_pickup_scan_window(schedule: models.ExamSchedule) -> tuple[datetime | None, datetime | None]:
    exam_start = get_schedule_start_datetime(schedule)
    if not exam_start:
        return None, None
    open_at = exam_start - timedelta(minutes=PICKUP_QR_OPEN_MINUTES_BEFORE)
    return open_at, exam_start


def get_schedule_period(db: Session, schedule: models.ExamSchedule) -> models.ExamPeriod | None:
    section = schedule.section
    if not section:
        return None
    exam_type = schedule.exam_type.value if isinstance(schedule.exam_type, models.ExamType) else str(schedule.exam_type)
    return db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == str(section.academic_year),
        models.ExamPeriod.semester == str(section.semester),
        models.ExamPeriod.exam_type == exam_type,
    ).first()


def get_confirmed_workflow_session(
    db: Session,
    schedule: models.ExamSchedule,
) -> tuple[models.ExamPeriod | None, models.OptimizeSession | None]:
    period = get_schedule_period(db, schedule)
    if not period:
        return None, None
    session = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == period.id
    ).first()
    if not session:
        return period, None
    if session.sig4_at or session.status in {"confirmed", "swap_open", "swap_confirming", "locked"}:
        return period, session
    return period, None


def ensure_schedule_ready_for_pickup(
    db: Session,
    schedule: models.ExamSchedule,
) -> tuple[models.ExamPeriod, models.OptimizeSession]:
    if not schedule.room_id or not schedule.room:
        raise HTTPException(400, "ยังไม่ได้ยืนยันห้องสอบจากการจัดตารางสอบ")
    period, session = get_confirmed_workflow_session(db, schedule)
    if not period or not session:
        raise HTTPException(400, "ยังไม่สามารถสร้าง QR หรือเอกสาร final ได้จนกว่าจะยืนยันผลการจัดตารางสอบ")
    return period, session


def get_confirmed_section_owner(db: Session, schedule: models.ExamSchedule) -> models.User | None:
    section = schedule.section
    if not section:
        return None
    exam_type = schedule.exam_type.value if isinstance(schedule.exam_type, models.ExamType) else str(schedule.exam_type)
    owner = db.query(models.SectionExamManager).filter(
        models.SectionExamManager.section_id == section.id,
        models.SectionExamManager.exam_type == exam_type,
        models.SectionExamManager.confirmed == True,
    ).first()
    if owner and owner.manager:
        return owner.manager
    return section.teacher


def build_pickup_assignments(
    db: Session,
    schedule: models.ExamSchedule,
) -> list[dict[str, object]]:
    assignments: list[dict[str, object]] = []
    seen: set[int] = set()

    for supervision in sorted(schedule.supervisions or [], key=lambda item: item.slot_order or 0):
        if not supervision.user_id or supervision.user_id in seen or not supervision.user:
            continue
        seen.add(supervision.user_id)
        assignments.append(
            {
                "user_id": supervision.user_id,
                "full_name": supervision.user.full_name or supervision.user.username,
                "role": supervision.role_in_exam or "invigilator",
            }
        )

    owner = get_confirmed_section_owner(db, schedule)
    if owner and owner.id not in seen:
        assignments.append(
            {
                "user_id": owner.id,
                "full_name": owner.full_name or owner.username,
                "role": "instructor",
            }
        )

    return assignments


def get_user_pickup_assignment(
    db: Session,
    schedule: models.ExamSchedule,
    user: models.User,
) -> dict[str, object] | None:
    for assignment in build_pickup_assignments(db, schedule):
        if assignment["user_id"] == user.id:
            return assignment
    return None


def get_latest_pickup_qr(
    db: Session,
    schedule_id: int,
    qr_type: models.PickupQrType = models.PickupQrType.invigilator_pickup,
) -> models.ExamPickupQrToken | None:
    return db.query(models.ExamPickupQrToken).filter(
        models.ExamPickupQrToken.schedule_id == schedule_id,
        models.ExamPickupQrToken.qr_type == qr_type,
    ).order_by(
        models.ExamPickupQrToken.version.desc(),
        models.ExamPickupQrToken.id.desc(),
    ).first()


def get_active_pickup_qr(
    db: Session,
    schedule_id: int,
    qr_type: models.PickupQrType = models.PickupQrType.invigilator_pickup,
) -> models.ExamPickupQrToken | None:
    return db.query(models.ExamPickupQrToken).filter(
        models.ExamPickupQrToken.schedule_id == schedule_id,
        models.ExamPickupQrToken.qr_type == qr_type,
        models.ExamPickupQrToken.is_active == True,
        models.ExamPickupQrToken.revoked_at.is_(None),
    ).order_by(models.ExamPickupQrToken.version.desc()).first()


def _build_pickup_snapshot(db: Session, schedule: models.ExamSchedule) -> dict[str, object]:
    course = schedule.section.course if schedule.section and schedule.section.course else None
    owner = get_confirmed_section_owner(db, schedule)
    return {
        "schedule_id": schedule.id,
        "course_code": course.course_id if course else None,
        "course_name_th": course.course_name_th if course else None,
        "section_no": schedule.section.section_no if schedule.section else None,
        "room_name": schedule.room.room_name if schedule.room else None,
        "exam_date": schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
        "exam_time": schedule.exam_time,
        "exam_time_start": schedule.exam_time_start,
        "exam_time_end": schedule.exam_time_end,
        "instructor": owner.full_name if owner else None,
        "assignments": build_pickup_assignments(db, schedule),
    }


def create_pickup_qr(
    db: Session,
    schedule: models.ExamSchedule,
    *,
    actor_id: int,
    activate: bool = False,
    qr_type: models.PickupQrType = models.PickupQrType.invigilator_pickup,
) -> models.ExamPickupQrToken:
    latest = get_latest_pickup_qr(db, schedule.id, qr_type=qr_type)
    next_version = (latest.version if latest else 0) + 1
    token = secrets.token_urlsafe(24)
    valid_from, valid_until = get_pickup_scan_window(schedule)
    row = models.ExamPickupQrToken(
        schedule_id=schedule.id,
        room_id=schedule.room_id,
        token=token,
        token_hash=hash_pickup_token(token),
        qr_type=qr_type,
        version=next_version,
        course_code=schedule.section.course.course_id if schedule.section and schedule.section.course else None,
        section_no=schedule.section.section_no if schedule.section else None,
        exam_date=schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
        start_time=schedule.exam_time_start or parse_time_range(schedule.exam_time)[0],
        end_time=schedule.exam_time_end or parse_time_range(schedule.exam_time)[1],
        is_active=False,
        generated_by=actor_id,
        valid_from=valid_from,
        valid_until=valid_until,
        payload_snapshot=_build_pickup_snapshot(db, schedule),
    )
    db.add(row)
    db.flush()
    if activate:
        activate_pickup_qr(db, row, actor_id=actor_id)
    return row


def activate_pickup_qr(
    db: Session,
    qr_token: models.ExamPickupQrToken,
    *,
    actor_id: int,
) -> models.ExamPickupQrToken:
    now = datetime.now(timezone.utc)
    others = db.query(models.ExamPickupQrToken).filter(
        models.ExamPickupQrToken.schedule_id == qr_token.schedule_id,
        models.ExamPickupQrToken.qr_type == qr_token.qr_type,
        models.ExamPickupQrToken.id != qr_token.id,
        models.ExamPickupQrToken.is_active == True,
    ).all()
    for item in others:
        item.is_active = False
        item.revoked_at = now

    qr_token.is_active = True
    qr_token.confirmed_by = actor_id
    qr_token.confirmed_at = now
    qr_token.revoked_at = None
    if not qr_token.valid_from or not qr_token.valid_until:
        qr_token.valid_from, qr_token.valid_until = get_pickup_scan_window(qr_token.schedule)
    return qr_token


def ensure_active_pickup_qr(
    db: Session,
    schedule: models.ExamSchedule,
    *,
    actor_id: int,
) -> models.ExamPickupQrToken:
    current = get_active_pickup_qr(db, schedule.id)
    if current:
        return current
    row = create_pickup_qr(db, schedule, actor_id=actor_id, activate=True)
    return row


def get_successful_pickup_checkin(
    db: Session,
    schedule_id: int,
    user_id: int,
) -> models.ExamPickupCheckin | None:
    return db.query(models.ExamPickupCheckin).filter(
        models.ExamPickupCheckin.schedule_id == schedule_id,
        models.ExamPickupCheckin.user_id == user_id,
        models.ExamPickupCheckin.status.in_(
            [models.PickupCheckinStatus.success, models.PickupCheckinStatus.late_override]
        ),
    ).order_by(models.ExamPickupCheckin.scanned_at.desc()).first()


def serialize_pickup_qr(qr_token: models.ExamPickupQrToken | None) -> dict[str, object] | None:
    if not qr_token:
        return None
    return {
        "id": qr_token.id,
        "schedule_id": qr_token.schedule_id,
        "version": qr_token.version,
        "qr_type": qr_token.qr_type.value if isinstance(qr_token.qr_type, models.PickupQrType) else str(qr_token.qr_type),
        "is_active": qr_token.is_active,
        "confirmed_at": qr_token.confirmed_at.isoformat() if qr_token.confirmed_at else None,
        "generated_at": qr_token.generated_at.isoformat() if qr_token.generated_at else None,
        "valid_from": qr_token.valid_from.isoformat() if qr_token.valid_from else None,
        "valid_until": qr_token.valid_until.isoformat() if qr_token.valid_until else None,
        "course_code": qr_token.course_code,
        "section_no": qr_token.section_no,
        "exam_date": qr_token.exam_date,
        "start_time": qr_token.start_time,
        "end_time": qr_token.end_time,
        "qr_value": wrap_pickup_token(qr_token.token, qr_token.qr_type),
    }


def describe_pickup_status(
    schedule: models.ExamSchedule,
    scanned_at: datetime | None,
) -> str:
    if not scanned_at:
        exam_start = get_schedule_start_datetime(schedule)
        if exam_start and now_local() >= exam_start:
            return "missed"
        return "not_checked_in"

    exam_start = get_schedule_start_datetime(schedule)
    if exam_start and scanned_at > exam_start:
        return "late"
    return "checked_in"
