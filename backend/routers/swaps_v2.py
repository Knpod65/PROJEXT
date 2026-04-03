"""
Enhanced Swap Router v2
- find users who are free at the same exam time
- support both shift swap and direct handoff flows
- keep frontend payloads backward-compatible
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from auth_utils import get_current_user, log_action, require_admin
from database import get_db
import models
from routers.settings import get_setting, is_past_deadline

router = APIRouter()


class SwapRequestCreate(BaseModel):
    my_supervision_id: int
    target_user_id: int
    message: Optional[str] = None


class SwapResponse(BaseModel):
    accept: Optional[bool] = None
    response: Optional[str] = None
    reason: Optional[str] = None


class EmergencySubCreate(BaseModel):
    schedule_id: int
    substitute_user_id: int


def _can_swap(db: Session) -> bool:
    enabled = get_setting(db, "swap_enabled")
    if enabled and enabled.lower() == "false":
        return False
    return not is_past_deadline(db, "swap_request_deadline")


def _resolve_swap_accept(data: SwapResponse) -> bool:
    if data.accept is not None:
        return data.accept
    if data.response:
        return data.response.lower() in {"accept", "accepted", "approve", "approved", "yes", "true"}
    raise HTTPException(400, "กรุณาระบุว่าจะ accept หรือ reject")


def _is_direct_handoff(swap: models.SwapRequest) -> bool:
    return (
        swap.requester_sup_id == swap.target_sup_id
        or not swap.target_sup
        or (swap.requester_sup and swap.target_sup and swap.requester_sup.id == swap.target_sup.id)
    )


def _schedule_payload(schedule: Optional[models.ExamSchedule], supervision_id: Optional[int] = None) -> dict:
    if not schedule:
        payload = {
            "exam_date": None,
            "exam_time": None,
            "course_id": None,
            "room_name": None,
            "section_no": None,
        }
    else:
        payload = {
            "exam_date": schedule.exam_date,
            "exam_time": schedule.exam_time,
            "course_id": (
                schedule.section.course.course_id
                if schedule.section and schedule.section.course
                else None
            ),
            "room_name": schedule.room.room_name if schedule.room else None,
            "section_no": schedule.section.section_no if schedule.section else None,
        }
    if supervision_id is not None:
        payload["supervision_id"] = supervision_id
    return payload


def _shift_payload(supervision: Optional[models.Supervision], include_supervision_id: bool = False) -> dict:
    schedule = supervision.schedule if supervision else None
    payload = {
        "date": schedule.exam_date if schedule else None,
        "time": schedule.exam_time if schedule else None,
        "course": (
            schedule.section.course.course_id
            if schedule and schedule.section and schedule.section.course
            else None
        ),
        "room": schedule.room.room_name if schedule and schedule.room else None,
        "section_no": schedule.section.section_no if schedule and schedule.section else None,
    }
    if include_supervision_id:
        payload["supervision_id"] = supervision.id if supervision else None
    return payload


def _party_payload(user: Optional[models.User]) -> dict:
    if not user:
        return {"id": None, "full_name": None, "email": None}
    return {"id": user.id, "full_name": user.full_name, "email": user.email}


def _clear_swap_flags(swap: models.SwapRequest) -> None:
    if swap.requester_sup:
        swap.requester_sup.swap_requested = False
    if swap.target_sup and swap.target_sup.id != swap.requester_sup_id:
        swap.target_sup.swap_requested = False


def _ensure_baseline(supervision: Optional[models.Supervision]) -> None:
    if supervision and not supervision.baseline_user_id:
        supervision.baseline_user_id = supervision.user_id


def _notify_swap_request(
    db: Session,
    requester: models.User,
    target_user_id: int,
    schedule: Optional[models.ExamSchedule],
    swap_id: int,
) -> None:
    if not schedule:
        return
    try:
        from email_notifications import notify_swap_request as _notify_sr

        target = db.query(models.User).filter(models.User.id == target_user_id).first()
        if not target or not target.email:
            return
        _notify_sr(
            target_email=target.email,
            target_name=target.full_name or target.username,
            requester_name=requester.full_name or requester.username,
            course_id=(
                schedule.section.course.course_id
                if schedule.section and schedule.section.course
                else "?"
            ),
            exam_date=str(schedule.exam_date) if schedule.exam_date else "?",
            exam_time=schedule.exam_time or "?",
            room_name=schedule.room.room_name if schedule.room else "?",
            swap_id=swap_id,
        )
    except Exception:
        pass


def _notify_swap_response(
    db: Session,
    swap: models.SwapRequest,
    current_user: models.User,
    response_value: str,
) -> None:
    try:
        from email_notifications import notify_swap_responded as _notify_rsp

        requester = db.query(models.User).filter(models.User.id == swap.requester_id).first()
        schedule = swap.requester_sup.schedule if swap.requester_sup else None
        if not requester or not requester.email:
            return
        _notify_rsp(
            requester_email=requester.email,
            requester_name=requester.full_name or requester.username,
            target_name=current_user.full_name or current_user.username,
            response=response_value,
            exam_date=str(schedule.exam_date) if schedule and schedule.exam_date else "?",
            exam_time=schedule.exam_time if schedule else "?",
        )
    except Exception:
        pass


@router.get("/available-users/{supervision_id}")
def get_available_users(
    supervision_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sup = db.query(models.Supervision).options(
        joinedload(models.Supervision.schedule)
    ).filter(models.Supervision.id == supervision_id).first()
    if not sup or not sup.schedule:
        raise HTTPException(404, "ไม่พบข้อมูล")

    sch = sup.schedule
    busy_user_ids = db.query(models.Supervision.user_id).join(
        models.ExamSchedule
    ).filter(
        models.ExamSchedule.exam_date == sch.exam_date,
        models.ExamSchedule.exam_time == sch.exam_time,
    ).subquery()

    available = db.query(models.User).filter(
        models.User.is_active == True,
        models.User.role.in_([models.UserRole.teacher, models.UserRole.staff]),
        models.User.id != current_user.id,
        ~models.User.id.in_(busy_user_ids),
    ).order_by(models.User.full_name).all()

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email,
        }
        for user in available
    ]


@router.get("/my")
def my_swaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    swaps = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester),
        joinedload(models.SwapRequest.target),
        joinedload(models.SwapRequest.requester_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.SwapRequest.requester_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.room),
        joinedload(models.SwapRequest.target_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.SwapRequest.target_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.room),
    ).filter(
        (models.SwapRequest.requester_id == current_user.id)
        | (models.SwapRequest.target_id == current_user.id)
    ).order_by(models.SwapRequest.created_at.desc()).all()

    result = []
    for swap in swaps:
        requester_sup = swap.requester_sup
        target_sup = None if _is_direct_handoff(swap) else swap.target_sup
        is_requester = swap.requester_id == current_user.id

        my_sup = requester_sup if is_requester else target_sup
        their_sup = target_sup if is_requester else requester_sup

        result.append({
            "id": swap.id,
            "status": swap.status.value if hasattr(swap.status, "value") else str(swap.status),
            "is_requester": is_requester,
            "is_direct_handoff": _is_direct_handoff(swap),
            "requester_name": swap.requester.full_name if swap.requester else None,
            "target_name": swap.target.full_name if swap.target else None,
            "requester": _party_payload(swap.requester),
            "target": _party_payload(swap.target),
            "message": swap.message,
            "reject_reason": swap.reject_reason,
            "created_at": swap.created_at.isoformat() if swap.created_at else None,
            "responded_at": swap.responded_at.isoformat() if swap.responded_at else None,
            "my_shift": _shift_payload(my_sup, include_supervision_id=True),
            "their_shift": _shift_payload(their_sup),
            "requester_schedule": _schedule_payload(
                requester_sup.schedule if requester_sup else None,
                requester_sup.id if requester_sup else None,
            ),
            "target_schedule": _schedule_payload(
                target_sup.schedule if target_sup else None,
                target_sup.id if target_sup else None,
            ),
        })
    return result


@router.get("/waiting")
def my_waiting_list(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    pending = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester),
        joinedload(models.SwapRequest.target),
        joinedload(models.SwapRequest.requester_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.SwapRequest.requester_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.room),
        joinedload(models.SwapRequest.target_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.SwapRequest.target_sup)
        .joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.room),
    ).filter(
        models.SwapRequest.target_id == current_user.id,
        models.SwapRequest.status == models.SwapStatus.pending,
    ).order_by(models.SwapRequest.created_at.desc()).all()

    result = []
    for swap in pending:
        target_sup = None if _is_direct_handoff(swap) else swap.target_sup
        result.append({
            "id": swap.id,
            "requester_name": swap.requester.full_name if swap.requester else None,
            "target_name": swap.target.full_name if swap.target else None,
            "requester": _party_payload(swap.requester),
            "target": _party_payload(swap.target),
            "message": swap.message,
            "created_at": swap.created_at.isoformat() if swap.created_at else None,
            "is_direct_handoff": _is_direct_handoff(swap),
            "their_shift": _shift_payload(swap.requester_sup),
            "my_shift": _shift_payload(target_sup),
            "requester_schedule": _schedule_payload(
                swap.requester_sup.schedule if swap.requester_sup else None,
                swap.requester_sup.id if swap.requester_sup else None,
            ),
            "target_schedule": _schedule_payload(
                target_sup.schedule if target_sup else None,
                target_sup.id if target_sup else None,
            ),
        })
    return result


@router.post("/")
def create_swap(
    data: SwapRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not _can_swap(db):
        raise HTTPException(400, "ระบบปิดรับคำขอสลับหรือเลย deadline")

    my_sup = db.query(models.Supervision).options(
        joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.room),
    ).filter(
        models.Supervision.id == data.my_supervision_id,
        models.Supervision.user_id == current_user.id,
    ).first()
    if not my_sup or not my_sup.schedule:
        raise HTTPException(404, "ไม่พบตารางคุมสอบของคุณ")

    if data.target_user_id == current_user.id:
        raise HTTPException(400, "ไม่สามารถส่งคำขอให้ตัวเองได้")

    target_user = db.query(models.User).filter(
        models.User.id == data.target_user_id,
        models.User.is_active == True,
    ).first()
    if not target_user:
        raise HTTPException(404, "ไม่พบผู้รับคำขอ")

    exists = db.query(models.SwapRequest).filter(
        models.SwapRequest.requester_sup_id == data.my_supervision_id,
        models.SwapRequest.status == models.SwapStatus.pending,
    ).first()
    if exists:
        raise HTTPException(400, "มีคำขอสลับรออยู่แล้ว")

    target_sup = db.query(models.Supervision).options(
        joinedload(models.Supervision.schedule)
        .joinedload(models.ExamSchedule.section)
        .joinedload(models.Section.course),
        joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.room),
    ).filter(
        models.Supervision.user_id == data.target_user_id,
    ).join(models.ExamSchedule).filter(
        models.ExamSchedule.exam_date == my_sup.schedule.exam_date
    ).order_by(models.ExamSchedule.exam_time).first()

    swap = models.SwapRequest(
        requester_id=current_user.id,
        target_id=data.target_user_id,
        requester_sup_id=my_sup.id,
        target_sup_id=target_sup.id if target_sup else my_sup.id,
        message=data.message,
        status=models.SwapStatus.pending,
    )
    db.add(swap)
    my_sup.swap_requested = True
    if target_sup and target_sup.id != my_sup.id:
        target_sup.swap_requested = True
    db.commit()
    db.refresh(swap)

    log_action(db, current_user, "SWAP_REQUEST", "swap_requests", swap.id, request=request)
    _notify_swap_request(db, current_user, data.target_user_id, my_sup.schedule, swap.id)
    return {"success": True, "swap_id": swap.id}


@router.post("/{swap_id}/respond")
def respond_swap(
    swap_id: int,
    data: SwapResponse,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not _can_swap(db):
        raise HTTPException(400, "ระบบปิดรับคำขอสลับแล้ว")

    swap = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester_sup).joinedload(models.Supervision.schedule),
        joinedload(models.SwapRequest.target_sup).joinedload(models.Supervision.schedule),
    ).filter(models.SwapRequest.id == swap_id).first()
    if not swap:
        raise HTTPException(404, "ไม่พบคำขอ")
    if swap.target_id != current_user.id:
        raise HTTPException(403, "ไม่ใช่ผู้รับคำขอนี้")
    if swap.status != models.SwapStatus.pending:
        raise HTTPException(400, "คำขอนี้ตอบไปแล้ว")

    accepted = _resolve_swap_accept(data)
    swap.responded_at = datetime.now(timezone.utc)

    if accepted:
        requester_sup = swap.requester_sup
        target_sup = swap.target_sup
        if not requester_sup:
            raise HTTPException(400, "ไม่พบตารางต้นทางของคำขอนี้")

        _ensure_baseline(requester_sup)

        if _is_direct_handoff(swap):
            requester_sup.user_id = swap.target_id
            requester_sup.is_swapped = True
            requester_sup.swap_requested = False
        else:
            if not target_sup:
                raise HTTPException(400, "ไม่พบตารางปลายทางของคำขอนี้")
            _ensure_baseline(target_sup)
            requester_user_id = requester_sup.user_id
            target_user_id = target_sup.user_id
            requester_sup.user_id = target_user_id
            target_sup.user_id = requester_user_id
            requester_sup.is_swapped = True
            target_sup.is_swapped = True
            requester_sup.swap_requested = False
            target_sup.swap_requested = False

        swap.status = models.SwapStatus.accepted
        action = "SWAP_ACCEPTED"
    else:
        swap.status = models.SwapStatus.rejected
        swap.reject_reason = data.reason
        _clear_swap_flags(swap)
        action = "SWAP_REJECTED"

    db.commit()
    log_action(db, current_user, action, "swap_requests", swap_id, request=request)
    _notify_swap_response(
        db,
        swap,
        current_user,
        "accepted" if accepted else "rejected",
    )
    return {"success": True, "status": swap.status.value}


@router.delete("/{swap_id}")
def cancel_swap(
    swap_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    swap = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester_sup),
        joinedload(models.SwapRequest.target_sup),
    ).filter(models.SwapRequest.id == swap_id).first()
    if not swap:
        raise HTTPException(404, "ไม่พบคำขอ")
    if swap.status != models.SwapStatus.pending:
        raise HTTPException(400, "คำขอนี้ไม่สามารถยกเลิกได้แล้ว")
    if current_user.role != models.UserRole.admin and swap.requester_id != current_user.id:
        raise HTTPException(403, "ไม่มีสิทธิ์ยกเลิกคำขอนี้")

    swap.status = models.SwapStatus.cancelled
    swap.responded_at = datetime.now(timezone.utc)
    _clear_swap_flags(swap)
    db.commit()

    log_action(db, current_user, "SWAP_CANCELLED", "swap_requests", swap.id, request=request)
    return {"success": True, "status": swap.status.value}


@router.post("/emergency-sub")
def emergency_substitute(
    data: EmergencySubCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    schedule = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.id == data.schedule_id
    ).first()
    if not schedule:
        raise HTTPException(404, "ไม่พบตารางสอบ")

    if current_user.role != models.UserRole.admin:
        is_assigned = db.query(models.Supervision).filter(
            models.Supervision.schedule_id == data.schedule_id,
            models.Supervision.user_id == current_user.id,
        ).first()
        if not is_assigned:
            raise HTTPException(403, "คุณไม่ได้ถูก assign ในตารางสอบนี้")

    existing = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == data.schedule_id,
        models.Supervision.user_id == data.substitute_user_id,
    ).first()
    if existing:
        raise HTTPException(400, "คนนี้มีชื่อในตารางสอบนี้อยู่แล้ว")

    max_slot = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == data.schedule_id
    ).count()

    supervision = models.Supervision(
        schedule_id=data.schedule_id,
        user_id=data.substitute_user_id,
        slot_order=max_slot + 1,
        is_emergency_sub=True,
        confirmed=True,
    )
    db.add(supervision)
    db.commit()

    log_action(
        db,
        current_user,
        "EMERGENCY_SUB",
        "supervisions",
        supervision.id,
        new_values={"substitute": data.substitute_user_id, "schedule": data.schedule_id},
        request=request,
    )
    return {"success": True, "supervision_id": supervision.id}


@router.post("/admin/lock-baseline")
def lock_baseline(
    semester: str = "2",
    academic_year: str = "2568",
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    db.query(models.SupervisionBaseline).delete()

    supervisions = db.query(models.Supervision).join(
        models.ExamSchedule
    ).join(models.Section).filter(
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).all()

    count = 0
    for supervision in supervisions:
        baseline = models.SupervisionBaseline(
            user_id=supervision.user_id,
            schedule_id=supervision.schedule_id,
            slot_order=supervision.slot_order,
            role_in_exam=supervision.role_in_exam,
        )
        db.add(baseline)
        count += 1

    db.commit()
    log_action(
        db,
        current_user,
        "LOCK_BASELINE",
        new_values={"count": count, "semester": semester},
        request=request,
    )
    return {"success": True, "baseline_count": count}
