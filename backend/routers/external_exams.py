"""
External Exams Router — สอบภาษาอังกฤษกลาง มช. / สอบพิเศษ

POST /api/external/                        สร้าง external exam
GET  /api/external/                        รายการทั้งหมดใน active period
GET  /api/external/{id}                    รายละเอียด + กรรมการ
PUT  /api/external/{id}                    แก้ไข
DELETE /api/external/{id}                  ลบ

POST /api/external/{id}/assign             Auto-assign กรรมการด้วย fairness
POST /api/external/{id}/assign-manual      กำหนดกรรมการเอง
DELETE /api/external/{id}/supervision/{uid} ถอด

GET  /api/external/stats/leaderboard       สถิติสะสมทุก period
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, case
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
import models
from auth_utils import require_admin, require_staff_or_admin, get_current_user, log_action
from collections import defaultdict
import statistics
from time_ranges import normalize_time_range

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────
class ExternalExamCreate(BaseModel):
    title:               str
    organizer:           Optional[str] = None
    exam_date:           str                    # "2026-03-15"
    exam_time:           str                    # "09.00-12.00"
    room_name:           Optional[str] = None
    num_students:        int = 0
    invigilators_needed: int = 1
    notes:               Optional[str] = None


class ExternalExamUpdate(BaseModel):
    title:               Optional[str] = None
    organizer:           Optional[str] = None
    exam_date:           Optional[str] = None
    exam_time:           Optional[str] = None
    room_name:           Optional[str] = None
    num_students:        Optional[int] = None
    invigilators_needed: Optional[int] = None
    notes:               Optional[str] = None
    status:              Optional[str] = None


class ManualAssignRequest(BaseModel):
    user_ids:      List[int]
    compensation:  float = 300.0


# ── helpers ───────────────────────────────────────────────────
def _get_active_period(db: Session) -> models.ExamPeriod:
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        raise HTTPException(400, "ยังไม่มี active period — Admin ต้องสร้างก่อน")
    return p


def _load_exam(db: Session, exam_id: int) -> models.ExternalExam:
    exam = db.query(models.ExternalExam).options(
        joinedload(models.ExternalExam.supervisions)
            .joinedload(models.ExternalSupervision.user),
        joinedload(models.ExternalExam.period),
    ).filter(models.ExternalExam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "ไม่พบ external exam")
    return exam


def _exam_dict(exam: models.ExternalExam) -> dict:
    return {
        "id":                  exam.id,
        "title":               exam.title,
        "organizer":           exam.organizer,
        "exam_date":           exam.exam_date,
        "exam_time":           exam.exam_time,
        "room_name":           exam.room_name,
        "num_students":        exam.num_students,
        "invigilators_needed": exam.invigilators_needed,
        "notes":               exam.notes,
        "status":              exam.status,
        "period":              {
            "id":           exam.period.id,
            "label":        exam.period.label,
            "academic_year":exam.period.academic_year,
            "semester":     exam.period.semester,
        } if exam.period else None,
        "supervisions": [
            {
                "id":          s.id,
                "user_id":     s.user_id,
                "full_name":   s.user.full_name if s.user else None,
                "user_name":   s.user.full_name if s.user else None,
                "slot_order":  s.slot_order,
                "compensation":s.compensation,
                "confirmed":   s.confirmed,
                "assigned_by": s.assigned_by,
            }
            for s in sorted(exam.supervisions, key=lambda x: x.slot_order)
        ],
        "assigned_count": len(exam.supervisions),
        "ready": len(exam.supervisions) >= exam.invigilators_needed,
    }


def _get_accumulated_load(db: Session) -> dict:
    """
    นับจำนวนครั้งคุมสอบสะสมทุก period ทุก type:
      supervision_baselines (ภายในคณะ) +
      external_supervisions (สอบพิเศษ)

    return: {user_id: total_count}
    """
    load = defaultdict(int)

    # ภายในคณะ (baseline = ไม่นับ swap เข้า/ออก)
    baselines = db.query(
        models.SupervisionBaseline.user_id,
        func.count(models.SupervisionBaseline.id).label("cnt")
    ).group_by(models.SupervisionBaseline.user_id).all()
    for user_id, cnt in baselines:
        load[user_id] += cnt

    # External exams
    ext_sups = db.query(
        models.ExternalSupervision.user_id,
        func.count(models.ExternalSupervision.id).label("cnt")
    ).group_by(models.ExternalSupervision.user_id).all()
    for user_id, cnt in ext_sups:
        load[user_id] += cnt

    return dict(load)


# กลุ่มที่ไม่เข้าร่วม external exam
EXCLUDED_ROLES      = {models.UserRole.esq_head, models.UserRole.dept_supervisor,
                       models.UserRole.teacher, models.UserRole.admin}
EXCLUDED_DIVISIONS  = {"Faculty_Secretary"}   # เลขาคณะ
EXCLUDED_UNIT_ROLES = {"Head_of_Unit"}        # หัวหน้าหน่วย (เก็บใน users.unit field)

# หัวหน้าหน่วยใน DB เก็บเป็น role=staff แต่ unit=Human_Resources/Finance/... พร้อม
# surname มี "(หัวหน้างาน)" หรือ query จาก full_name
def _is_excluded(user: models.User) -> bool:
    """
    True = ไม่มีสิทธิ์คุมสอบ external

    กลุ่มที่กรองออก:
      1. esq_head (นภาภรณ์) — ดูภาพรวม ไม่คุมสอบ
      2. dept_supervisor, teacher, admin — ไม่ใช่ staff ทั่วไป
      3. Faculty_Secretary (เลขาคณะ ปวีณา)
      4. Head_of_Unit ทุกฝ่าย — unit field ลงท้ายด้วย "_HEAD"
         (สิรินภัทร, ไกรพล, รภัทรา)
      5. full_name มี "(หัวหน้างาน)" — กรณีพิเศษ ESQ head
    """
    if user.role in EXCLUDED_ROLES:
        return True
    if user.division in EXCLUDED_DIVISIONS:
        return True
    if user.full_name and "(หัวหน้างาน)" in user.full_name:
        return True
    # Head_of_Unit ทุกฝ่าย — unit ลงท้ายด้วย _HEAD (seed.py)
    if user.unit and user.unit.endswith("_HEAD"):
        return True
    return False


def _get_eligible_staff(db: Session, exam: models.ExternalExam) -> List[models.User]:
    preview = _build_assignment_preview(db, exam)
    eligible_ids = {row["user_id"] for row in preview["eligible_candidates"]}
    return [
        user
        for user in db.query(models.User).filter(
            models.User.role == models.UserRole.staff,
            models.User.is_active == True,
        ).all()
        if user.id in eligible_ids
    ]


def _build_assignment_preview(db: Session, exam: models.ExternalExam) -> dict:
    normalized_exam_time = normalize_time_range(exam.exam_time) or exam.exam_time
    already_assigned = {s.user_id for s in exam.supervisions}
    acc_load = _get_accumulated_load(db)

    internal_conflicts = {
        row[0]
        for row in db.query(models.Supervision.user_id).join(
            models.ExamSchedule,
            models.Supervision.schedule_id == models.ExamSchedule.id,
        ).filter(
            models.ExamSchedule.exam_date == exam.exam_date,
            models.ExamSchedule.exam_time == exam.exam_time,
        ).all()
    }
    external_conflicts = {
        row[0]
        for row in db.query(models.ExternalSupervision.user_id).join(
            models.ExternalExam,
            models.ExternalSupervision.external_exam_id == models.ExternalExam.id,
        ).filter(
            models.ExternalExam.exam_date == exam.exam_date,
            models.ExternalExam.exam_time == exam.exam_time,
            models.ExternalExam.id != exam.id,
        ).all()
    }

    unavailable_by_user: dict[int, str] = {}
    for user_id, block_time in db.query(
        models.StaffUnavailability.user_id,
        models.StaffUnavailability.block_time,
    ).filter(
        models.StaffUnavailability.exam_period_id == exam.exam_period_id,
        models.StaffUnavailability.block_date == exam.exam_date,
    ).all():
        if block_time is None:
            unavailable_by_user[user_id] = "Unavailable all day"
            continue
        if normalize_time_range(block_time) == normalized_exam_time:
            unavailable_by_user[user_id] = f"Unavailable at {normalized_exam_time}"

    all_staff = [
        user
        for user in db.query(models.User).filter(
            models.User.role == models.UserRole.staff,
            models.User.is_active == True,
        ).order_by(models.User.full_name).all()
    ]

    eligible_candidates = []
    conflicted_staff = []
    excluded_staff = []
    assigned_staff = []

    for user in all_staff:
        payload = {
            "user_id": user.id,
            "full_name": user.full_name,
            "division": user.division,
            "unit": user.unit,
            "total_load": acc_load.get(user.id, 0),
        }
        if _is_excluded(user):
            excluded_staff.append({**payload, "reason": "Excluded by role/division rule"})
            continue
        if user.id in already_assigned:
            assigned_staff.append(payload)
            continue
        if user.id in unavailable_by_user:
            conflicted_staff.append({**payload, "reason": unavailable_by_user[user.id], "conflict_type": "staff_unavailability"})
            continue
        if user.id in internal_conflicts:
            conflicted_staff.append({**payload, "reason": "Already assigned to an internal exam at this time", "conflict_type": "internal_exam"})
            continue
        if user.id in external_conflicts:
            conflicted_staff.append({**payload, "reason": "Already assigned to another external exam at this time", "conflict_type": "external_exam"})
            continue
        eligible_candidates.append(payload)

    eligible_candidates.sort(key=lambda row: (row["total_load"], row["user_id"]))

    needed_count = max(exam.invigilators_needed - len(exam.supervisions), 0)
    recommended_assignment = eligible_candidates[:needed_count]
    candidate_pool = [row["total_load"] for row in eligible_candidates + conflicted_staff + assigned_staff]
    projected_pool = candidate_pool.copy()
    for row in recommended_assignment:
        projected_pool.append(row["total_load"] + 1)

    current_score = round(statistics.stdev(candidate_pool), 2) if len(candidate_pool) > 1 else 0.0
    projected_score = round(statistics.stdev(projected_pool), 2) if len(projected_pool) > 1 else current_score

    warnings = []
    shortage_count = max(needed_count - len(eligible_candidates), 0)
    if needed_count == 0:
        warnings.append("This external exam already has enough assigned staff.")
    if shortage_count > 0:
        warnings.append(
            f"Only {len(eligible_candidates)} eligible staff are available, but {needed_count} are required."
        )

    return {
        "exam": _exam_dict(exam),
        "allocation_mode": "staff_only",
        "required_count": exam.invigilators_needed,
        "assigned_count": len(exam.supervisions),
        "needed_count": needed_count,
        "shortage_count": shortage_count,
        "eligible_candidates": eligible_candidates,
        "recommended_assignment": recommended_assignment,
        "conflicted_staff": conflicted_staff,
        "excluded_staff": excluded_staff,
        "assigned_staff": assigned_staff,
        "fairness": {
            "current_score": current_score,
            "projected_score": projected_score,
        },
        "warnings": warnings,
        "note": "External exam optimization assigns staff only. It does not assign rooms.",
    }


# ══════════════════════════════════════════════════════════════
# CRUD
# ══════════════════════════════════════════════════════════════

@router.get("/")
def list_external_exams(
    period_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    if period_id:
        q = db.query(models.ExternalExam).filter(
            models.ExternalExam.exam_period_id == period_id
        )
    else:
        period = _get_active_period(db)
        q = db.query(models.ExternalExam).filter(
            models.ExternalExam.exam_period_id == period.id
        )

    exams = q.options(
        joinedload(models.ExternalExam.supervisions)
            .joinedload(models.ExternalSupervision.user),
        joinedload(models.ExternalExam.period),
    ).order_by(models.ExternalExam.exam_date, models.ExternalExam.exam_time).all()

    return [_exam_dict(e) for e in exams]


@router.post("/")
def create_external_exam(
    data: ExternalExamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    period = _get_active_period(db)
    exam = models.ExternalExam(
        exam_period_id       = period.id,
        title                = data.title,
        organizer            = data.organizer,
        exam_date            = data.exam_date,
        exam_time            = data.exam_time,
        room_name            = data.room_name,
        num_students         = data.num_students,
        invigilators_needed  = data.invigilators_needed,
        notes                = data.notes,
        status               = "draft",
        created_by           = current_user.id,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    log_action(db, current_user, "CREATE_EXTERNAL_EXAM", "external_exams",
               record_id=exam.id, new_values=data.dict(), request=request)

    return _exam_dict(_load_exam(db, exam.id))


@router.get("/{exam_id}")
def get_external_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    return _exam_dict(_load_exam(db, exam_id))


@router.post("/{exam_id}/assign-preview")
def preview_auto_assign(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    exam = _load_exam(db, exam_id)
    return _build_assignment_preview(db, exam)


@router.put("/{exam_id}")
def update_external_exam(
    exam_id: int,
    data: ExternalExamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    exam = _load_exam(db, exam_id)
    for k, v in data.dict(exclude_none=True).items():
        setattr(exam, k, v)
    db.commit()
    log_action(db, current_user, "UPDATE_EXTERNAL_EXAM", "external_exams",
               record_id=exam_id, new_values=data.dict(exclude_none=True), request=request)
    return _exam_dict(_load_exam(db, exam_id))


@router.delete("/{exam_id}")
def delete_external_exam(
    exam_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    exam = db.query(models.ExternalExam).filter(
        models.ExternalExam.id == exam_id
    ).first()
    if not exam:
        raise HTTPException(404, "ไม่พบ external exam")
    db.delete(exam)
    db.commit()
    log_action(db, current_user, "DELETE_EXTERNAL_EXAM", "external_exams",
               record_id=exam_id, request=request)
    return {"status": "deleted"}


# ══════════════════════════════════════════════════════════════
# AUTO-ASSIGN — Fairness optimizer
# ══════════════════════════════════════════════════════════════

@router.post("/{exam_id}/assign")
def auto_assign(
    exam_id: int,
    compensation: float = 300.0,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    Auto-assign กรรมการคุมสอบโดยใช้ fairness จาก accumulated load
    Algorithm:
      1. ดึง load สะสมทุก period (baseline + external)
      2. เรียงลำดับ staff จากน้อยสุด → มากสุด
      3. กรอง conflict วัน+เวลาเดียวกัน
      4. เลือก N คน (invigilators_needed)
    """
    exam = _load_exam(db, exam_id)

    preview = _build_assignment_preview(db, exam)
    need = preview["needed_count"]
    if need <= 0:
        raise HTTPException(400, preview["warnings"][0] if preview["warnings"] else "This external exam already has enough assigned staff.")
    if preview["shortage_count"] > 0:
        raise HTTPException(400, preview["warnings"][0] if preview["warnings"] else "Not enough eligible staff are available.")

    next_slot = len(exam.supervisions) + 1
    assigned  = []
    for candidate in preview["recommended_assignment"]:
        db.add(models.ExternalSupervision(
            external_exam_id = exam.id,
            user_id          = candidate["user_id"],
            slot_order       = next_slot,
            compensation     = compensation,
            confirmed        = False,
            assigned_by      = "auto",
        ))
        assigned.append({
            "user_id":     candidate["user_id"],
            "full_name":   candidate["full_name"],
            "load_before": candidate["total_load"],
        })
        next_slot += 1

    db.commit()

    log_action(db, current_user, "AUTO_ASSIGN_EXTERNAL", "external_exams",
               record_id=exam_id,
               new_values={"assigned": [a["full_name"] for a in assigned],
                           "fairness_score": preview["fairness"]["projected_score"]},
               request=request)

    return {
        "status":         "ok",
        "assigned":       assigned,
        "fairness_score": preview["fairness"]["projected_score"],
        "preview":        _build_assignment_preview(db, _load_exam(db, exam_id)),
        "exam":           _exam_dict(_load_exam(db, exam_id)),
    }


@router.post("/{exam_id}/assign-manual")
def manual_assign(
    exam_id: int,
    data: ManualAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    """กำหนดกรรมการเองโดยระบุ user_ids"""
    exam = _load_exam(db, exam_id)
    already = {s.user_id for s in exam.supervisions}
    preview = _build_assignment_preview(db, exam)
    eligible_ids = {row["user_id"] for row in preview["eligible_candidates"]}

    added = []
    next_slot = len(exam.supervisions) + 1
    for uid in data.user_ids:
        if uid in already:
            continue
        if uid not in eligible_ids:
            raise HTTPException(400, f"user_id {uid} is not eligible for this slot")
        user = db.query(models.User).filter(models.User.id == uid).first()
        if not user:
            continue
        db.add(models.ExternalSupervision(
            external_exam_id = exam.id,
            user_id          = uid,
            slot_order       = next_slot,
            compensation     = data.compensation,
            confirmed        = False,
            assigned_by      = "manual",
        ))
        added.append(user.full_name)
        next_slot += 1

    db.commit()
    log_action(db, current_user, "MANUAL_ASSIGN_EXTERNAL", "external_exams",
               record_id=exam_id, new_values={"added": added}, request=request)

    return {"status": "ok", "added": added, "exam": _exam_dict(_load_exam(db, exam_id))}


@router.delete("/{exam_id}/supervision/{user_id}")
def remove_supervision(
    exam_id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    sup = db.query(models.ExternalSupervision).filter(
        and_(
            models.ExternalSupervision.external_exam_id == exam_id,
            models.ExternalSupervision.user_id          == user_id,
        )
    ).first()
    if not sup:
        raise HTTPException(404, "ไม่พบกรรมการ")
    db.delete(sup)
    db.commit()
    return {"status": "removed", "exam": _exam_dict(_load_exam(db, exam_id))}


# ══════════════════════════════════════════════════════════════
# STATS — Leaderboard สะสมทุก period
# ══════════════════════════════════════════════════════════════

@router.get("/stats/leaderboard")
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    สถิติสะสมทุก period ต่อคน:
      internal_count  = ครั้งจาก supervision_baselines
      external_count  = ครั้งจาก external_supervisions
      total_count     = รวม
    เรียงจากน้อยสุด (คนที่ยังได้คุมน้อย = ควรได้รับเลือกครั้งต่อไป)
    """
    # internal
    internal = db.query(
        models.SupervisionBaseline.user_id,
        func.count(models.SupervisionBaseline.id).label("internal_count"),
    ).group_by(models.SupervisionBaseline.user_id).all()
    internal_map = {r[0]: r[1] for r in internal}

    # external
    external = db.query(
        models.ExternalSupervision.user_id,
        func.count(models.ExternalSupervision.id).label("external_count"),
    ).group_by(models.ExternalSupervision.user_id).all()
    external_map = {r[0]: r[1] for r in external}

    # all staff
    all_staff = db.query(models.User).filter(
        models.User.role      == models.UserRole.staff,
        models.User.is_active == True,
    ).order_by(models.User.full_name).all()
    # กรองกลุ่มที่ไม่เข้าร่วม
    staff = [u for u in all_staff if not _is_excluded(u)]

    rows = []
    for u in staff:
        ic = internal_map.get(u.id, 0)
        ec = external_map.get(u.id, 0)
        rows.append({
            "user_id":        u.id,
            "full_name":      u.full_name,
            "division":       u.division,
            "internal_count": ic,
            "external_count": ec,
            "total_count":    ic + ec,
        })

    # เรียง total_count น้อย→มาก (fairness order)
    rows.sort(key=lambda r: (r["total_count"], r["user_id"]))

    total_counts = [r["total_count"] for r in rows]
    fairness_score = round(statistics.stdev(total_counts), 2) if len(total_counts) > 1 else 0.0

    return {
        "leaderboard":   rows,
        "fairness_score": fairness_score,
        "total_staff":   len(rows),
        "note": "เรียงจากน้อยสุด — คนบนสุดควรได้รับมอบหมายครั้งถัดไป",
    }


@router.get("/stats/conflict-check/{exam_id}")
def conflict_check(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    """ดูว่า staff คนไหนว่าง/ติดในวันเวลานั้น"""
    exam     = _load_exam(db, exam_id)
    eligible = _get_eligible_staff(db, exam)
    acc_load = _get_accumulated_load(db)

    # คนที่ติด
    all_staff = db.query(models.User).filter(
        models.User.role      == models.UserRole.staff,
        models.User.is_active == True,
    ).all()
    # กรองกลุ่มที่ไม่เข้าร่วม
    all_staff = [u for u in all_staff if not _is_excluded(u)]

    eligible_ids = {u.id for u in eligible}
    assigned_ids = {s.user_id for s in exam.supervisions}

    result = []
    for u in sorted(all_staff, key=lambda x: acc_load.get(x.id, 0)):
        if u.id in assigned_ids:
            status = "assigned"
        elif u.id in eligible_ids:
            status = "available"
        else:
            status = "conflict"
        result.append({
            "user_id":    u.id,
            "full_name":  u.full_name,
            "total_load": acc_load.get(u.id, 0),
            "status":     status,
        })

    return {
        "exam_date":  exam.exam_date,
        "exam_time":  exam.exam_time,
        "available":  sum(1 for r in result if r["status"] == "available"),
        "conflict":   sum(1 for r in result if r["status"] == "conflict"),
        "assigned":   sum(1 for r in result if r["status"] == "assigned"),
        "staff":      result,
    }
