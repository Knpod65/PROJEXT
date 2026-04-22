"""
Swap Router — Invigilator swap request workflow
Request → Target accepts/rejects → Auto-update supervision records
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from pydantic import BaseModel
from database import get_db
import models
from auth_utils import get_current_user, require_admin, log_action
from routers.settings import get_setting, is_past_deadline
from datetime import datetime, timezone
from term_lifecycle import require_period_editable_for_values

router = APIRouter()


class SwapRequestCreate(BaseModel):
    my_supervision_id:     int
    target_supervision_id: int
    message: Optional[str] = None


class SwapResponse(BaseModel):
    accept: bool
    reason: Optional[str] = None


def _can_swap(db) -> bool:
    enabled = get_setting(db, "swap_enabled")
    if enabled and enabled.lower() == "false":
        return False
    if is_past_deadline(db, "swap_request_deadline"):
        return False
    return True


@router.get("/")
def list_swaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ดู swap requests ที่เกี่ยวข้องกับตัวเอง"""
    q = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester),
        joinedload(models.SwapRequest.target),
        joinedload(models.SwapRequest.requester_sup)
            .joinedload(models.Supervision.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.SwapRequest.target_sup)
            .joinedload(models.Supervision.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
    ).filter(
        (models.SwapRequest.requester_id == current_user.id) |
        (models.SwapRequest.target_id == current_user.id)
    ).order_by(models.SwapRequest.created_at.desc())

    result = []
    for s in q.all():
        r_sch = s.requester_sup.schedule if s.requester_sup else None
        t_sch = s.target_sup.schedule if s.target_sup else None
        result.append({
            "id": s.id,
            "status": s.status,
            "is_requester": s.requester_id == current_user.id,
            "requester": s.requester.full_name if s.requester else None,
            "target": s.target.full_name if s.target else None,
            "message": s.message,
            "reject_reason": s.reject_reason,
            "created_at": s.created_at.isoformat(),
            "responded_at": s.responded_at.isoformat() if s.responded_at else None,
            "my_shift": {
                "date": r_sch.exam_date if r_sch else None,
                "time": r_sch.exam_time if r_sch else None,
                "course": (r_sch.section.course.course_name_th
                           if r_sch and r_sch.section and r_sch.section.course
                           else None),
            } if s.requester_id == current_user.id else {
                "date": t_sch.exam_date if t_sch else None,
                "time": t_sch.exam_time if t_sch else None,
                "course": (t_sch.section.course.course_name_th
                           if t_sch and t_sch.section and t_sch.section.course
                           else None),
            },
            "their_shift": {
                "date": t_sch.exam_date if t_sch else None,
                "time": t_sch.exam_time if t_sch else None,
                "course": (t_sch.section.course.course_name_th
                           if t_sch and t_sch.section and t_sch.section.course
                           else None),
            } if s.requester_id == current_user.id else {
                "date": r_sch.exam_date if r_sch else None,
                "time": r_sch.exam_time if r_sch else None,
                "course": (r_sch.section.course.course_name_th
                           if r_sch and r_sch.section and r_sch.section.course
                           else None),
            },
        })
    return result


@router.post("/")
def create_swap_request(
    data: SwapRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not _can_swap(db):
        raise HTTPException(400, "ระบบปิดรับคำขอสลับแล้ว หรือเลย deadline")

    # Verify ownership of requester supervision
    my_sup = db.query(models.Supervision).filter(
        models.Supervision.id == data.my_supervision_id,
        models.Supervision.user_id == current_user.id,
    ).first()
    if not my_sup:
        raise HTTPException(404, "ไม่พบตารางคุมสอบของคุณ")

    if my_sup.schedule and my_sup.schedule.section:
        require_period_editable_for_values(
            db,
            my_sup.schedule.section.academic_year,
            my_sup.schedule.section.semester,
            my_sup.schedule.exam_type.value if hasattr(my_sup.schedule.exam_type, "value") else my_sup.schedule.exam_type,
        )

    target_sup = db.query(models.Supervision).options(
        joinedload(models.Supervision.user)
    ).filter(models.Supervision.id == data.target_supervision_id).first()
    if not target_sup:
        raise HTTPException(404, "ไม่พบตารางคุมสอบเป้าหมาย")

    # ห้ามขอซ้ำ
    existing = db.query(models.SwapRequest).filter(
        models.SwapRequest.requester_sup_id == data.my_supervision_id,
        models.SwapRequest.status == models.SwapStatus.pending,
    ).first()
    if existing:
        raise HTTPException(400, "มีคำขอสลับรออยู่แล้ว")

    swap = models.SwapRequest(
        requester_id     = current_user.id,
        target_id        = target_sup.user_id,
        requester_sup_id = data.my_supervision_id,
        target_sup_id    = data.target_supervision_id,
        message          = data.message,
        status           = models.SwapStatus.pending,
    )
    db.add(swap)

    # Mark supervision ว่ามี swap pending
    my_sup.swap_requested = True
    target_sup.swap_requested = True

    db.commit()
    log_action(db, current_user, "SWAP_REQUEST", "swap_requests",
               swap.id, request=request)
    return {"success": True, "swap_id": swap.id}


@router.post("/{swap_id}/respond")
def respond_to_swap(
    swap_id: int,
    data: SwapResponse,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not _can_swap(db):
        raise HTTPException(400, "ระบบปิดรับคำขอสลับแล้ว")

    swap = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester_sup),
        joinedload(models.SwapRequest.target_sup),
    ).filter(models.SwapRequest.id == swap_id).first()

    if not swap:
        raise HTTPException(404, "ไม่พบคำขอ")
    if swap.target_id != current_user.id:
        raise HTTPException(403, "คุณไม่ใช่ผู้รับคำขอนี้")
    if swap.status != models.SwapStatus.pending:
        raise HTTPException(400, "คำขอนี้ตอบไปแล้ว")

    if swap.requester_sup and swap.requester_sup.schedule and swap.requester_sup.schedule.section:
        require_period_editable_for_values(
            db,
            swap.requester_sup.schedule.section.academic_year,
            swap.requester_sup.schedule.section.semester,
            swap.requester_sup.schedule.exam_type.value if hasattr(swap.requester_sup.schedule.exam_type, "value") else swap.requester_sup.schedule.exam_type,
        )

    if data.accept:
        swap.status = models.SwapStatus.accepted
        swap.responded_at = datetime.now(timezone.utc)

        # ── Auto-update supervision records ──
        req_sup = swap.requester_sup
        tgt_sup = swap.target_sup

        # Swap user_id
        req_user_id, tgt_user_id = req_sup.user_id, tgt_sup.user_id
        req_sup.user_id  = tgt_user_id
        tgt_sup.user_id  = req_user_id

        # Mark as swapped (สำหรับ visualization — faded in UI)
        req_sup.is_swapped = True
        tgt_sup.is_swapped = True

        # Clear pending flags
        req_sup.swap_requested = False
        tgt_sup.swap_requested = False

        action = "SWAP_ACCEPTED"
    else:
        swap.status       = models.SwapStatus.rejected
        swap.reject_reason= data.reason
        swap.responded_at = datetime.now(timezone.utc)

        # Clear pending flags
        if swap.requester_sup:
            swap.requester_sup.swap_requested = False
        if swap.target_sup:
            swap.target_sup.swap_requested = False

        action = "SWAP_REJECTED"

    db.commit()
    log_action(db, current_user, action, "swap_requests",
               swap_id, request=request)
    return {"success": True, "status": swap.status}


@router.delete("/{swap_id}")
def cancel_swap(
    swap_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    swap = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester_sup),
        joinedload(models.SwapRequest.target_sup),
    ).filter(models.SwapRequest.id == swap_id).first()
    if not swap:
        raise HTTPException(404, "ไม่พบคำขอ")
    if swap.requester_id != current_user.id:
        raise HTTPException(403, "ยกเลิกได้เฉพาะคำขอของตัวเอง")
    if swap.status != models.SwapStatus.pending:
        raise HTTPException(400, "ยกเลิกได้เฉพาะคำขอที่ยังรออยู่")

    if swap.requester_sup and swap.requester_sup.schedule and swap.requester_sup.schedule.section:
        require_period_editable_for_values(
            db,
            swap.requester_sup.schedule.section.academic_year,
            swap.requester_sup.schedule.section.semester,
            swap.requester_sup.schedule.exam_type.value if hasattr(swap.requester_sup.schedule.exam_type, "value") else swap.requester_sup.schedule.exam_type,
        )

    swap.status = models.SwapStatus.cancelled
    if swap.requester_sup:
        swap.requester_sup.swap_requested = False
    if swap.target_sup:
        swap.target_sup.swap_requested = False

    db.commit()
    log_action(db, current_user, "SWAP_CANCELLED", "swap_requests",
               swap_id, request=request)
    return {"success": True}


@router.get("/admin/all")
def admin_list_all_swaps(
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    swaps = db.query(models.SwapRequest).options(
        joinedload(models.SwapRequest.requester),
        joinedload(models.SwapRequest.target),
    ).order_by(models.SwapRequest.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "status": s.status,
            "requester": s.requester.full_name if s.requester else None,
            "target": s.target.full_name if s.target else None,
            "created_at": s.created_at.isoformat(),
            "responded_at": s.responded_at.isoformat() if s.responded_at else None,
        }
        for s in swaps
    ]
