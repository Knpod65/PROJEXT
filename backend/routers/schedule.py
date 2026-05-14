"""
M2 — Schedule Router + CP-SAT Optimizer (OR-Tools)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
import models, schemas
from academic_groups import build_course_group_clause
from auth_utils import (
    get_current_user, require_staff_or_admin, require_admin,
    get_effective_role, log_action, get_dept_filter, is_view_all_role
)
from collections import defaultdict
from exam_ownership import get_active_exam_period, get_teacher_owned_section_ids
from staff_workloads import (
    assign_paper_distribution_for_period,
    is_staff_unavailable as _interval_staff_unavailable,
)
from term_lifecycle import require_period_editable_for_values
from time_ranges import normalize_time_range, parse_time_range, ranges_overlap
from repositories.schedule_repository import load_unavailability_maps as _load_unavailability_maps_repo
from services.optimization_candidate_trace_adapter import (
    REASON_CODE_FAIRNESS_PENALTY,
    REASON_CODE_FALLBACK_USED,
    trace_room_candidate,
    trace_split_candidate,
    trace_staff_candidate,
    trace_timeslot_candidate,
)
from services.optimization_constraint_trace_adapter import (
    trace_capacity_constraint,
    trace_document_readiness_constraint,
    trace_fairness_constraint,
    trace_hard_constraint,
    trace_qr_readiness_constraint,
    trace_room_conflict_constraint,
    trace_soft_constraint,
    trace_staffing_constraint,
    trace_student_conflict_constraint,
)
from services.optimization_pipeline_observer_service import observe_optimization_result
from services.optimization_selection_trace_adapter import (
    trace_final_schedule_selection,
    trace_room_selection,
    trace_split_selection,
    trace_staff_selection,
)
from services.schedule_query_service import (
    build_schedule_query as _build_schedule_query_service,
    group_schedules_by_date as _group_schedules_by_date,
    is_room_unavailable as _is_room_unavailable_service,
    schedule_time_bounds as _schedule_time_bounds_service,
    serialize_schedule as _serialize_schedule,
)
from services.optimization_trace_context import (
    OptimizationTraceContext,
    TRACE_SOURCE_FALLBACK,
    TRACE_SOURCE_POST_HOC,
    TRACE_SOURCE_SOLVER,
)
from services.optimization_recheck_service import build_recheck_report

router = APIRouter()


def _schedule_time_bounds(exam_time: Optional[str], start: Optional[str] = None, end: Optional[str] = None):
    return _schedule_time_bounds_service(exam_time, start, end)


def _normalize_schedule_time_fields(exam_time: Optional[str]):
    start, end = parse_time_range(exam_time)
    return {
        "exam_time_start": start,
        "exam_time_end": end,
    }


def _build_schedule_query(
    db: Session,
    current_user: models.User,
    exam_date: Optional[str] = None,
    room_id: Optional[int] = None,
    status: Optional[str] = None,
):
    return _build_schedule_query_service(db, current_user, exam_date, room_id, status)


def _load_unavailability_maps(db: Session, data: schemas.OptimizerRequest):
    return _load_unavailability_maps_repo(db, data)


def _is_staff_unavailable(unavail_map, user_id: int, block_date, block_time: Optional[str]) -> bool:
    return _interval_staff_unavailable(unavail_map, user_id, block_date, block_time)


def _is_room_unavailable(
    room_unavail_map,
    room_id: int,
    block_date,
    block_time: Optional[str],
    block_start: Optional[str] = None,
    block_end: Optional[str] = None,
) -> bool:
    return _is_room_unavailable_service(room_unavail_map, room_id, block_date, block_time, block_start, block_end)

def _get_schedule(section, exam_type=None):
    """Helper: ดึง ExamSchedule จาก section.schedules (list)
    ถ้า exam_type=None ดึงอันแรก, มิฉะนั้น filter ตาม exam_type"""
    if not section.schedules:
        return None
    if exam_type is None:
        return section.schedules[0] if section.schedules else None
    for s in section.schedules:
        if s.exam_type == exam_type or s.exam_type.value == exam_type:
            return s
    return None


def _optimizer_exam_type_value(data) -> str:
    return data.exam_type.value if hasattr(data.exam_type, "value") else str(data.exam_type)


def _optimizer_trace_session_id(data) -> str:
    return f"{data.academic_year}:{data.semester}:{_optimizer_exam_type_value(data)}"


def _slot_trace_label(exam_date: str | None, exam_time: str | None) -> str:
    if exam_date and exam_time:
        return f"{exam_date} {exam_time}"
    return exam_date or exam_time or "UNSPECIFIED_SLOT"


def _link_trace_recheck_issues(
    trace_context: OptimizationTraceContext,
    issues: list[dict],
) -> None:
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        code = str(issue.get("code") or "UNKNOWN_CONSTRAINT")
        severity = str(issue.get("severity") or "INFO").upper()
        entity_type = str(issue.get("category") or "schedule_entry").lower()
        entity_id = issue.get("course_id") or issue.get("actor_id") or issue.get("room_id") or code
        metadata = {
            "category": issue.get("category"),
            "blocking": issue.get("blocking"),
            "can_override": issue.get("can_override"),
            "suggested_fix": issue.get("suggested_fix"),
            "exam_date": issue.get("exam_date"),
            "exam_time": issue.get("exam_time"),
            "room_id": issue.get("room_id"),
            "actor_id": issue.get("actor_id"),
            "message": issue.get("message"),
        }

        if code == "ROOM_CAPACITY_EXCEEDED":
            trace_capacity_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code in {"MISSING_INVIGILATOR", "MISSING_DISTRIBUTION_STAFF", "INSTRUCTOR_CONFLICT"}:
            trace_staffing_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code == "ROOM_CONFLICT":
            trace_room_conflict_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code == "STUDENT_CONFLICT":
            trace_student_conflict_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code in {"WORKLOAD_IMBALANCE", "CONSECUTIVE_INVIGILATION_OVERLOAD", "SAME_DAY_OVERLOAD"}:
            trace_fairness_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                severity=severity,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code == "COPY_COUNT_MISMATCH":
            trace_document_readiness_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                severity=severity,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif code == "MISSING_QR_READINESS":
            trace_qr_readiness_constraint(
                trace_context,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                severity=severity,
                message=issue.get("message"),
                metadata=metadata,
            )
        elif severity == "HARD_FAIL":
            trace_hard_constraint(
                trace_context,
                constraint_code=code,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                message=issue.get("message"),
                metadata=metadata,
            )
        else:
            trace_soft_constraint(
                trace_context,
                constraint_code=code,
                passed=False,
                entity_type=entity_type,
                entity_id=entity_id,
                reason_code=code,
                source=TRACE_SOURCE_POST_HOC,
                severity=severity,
                message=issue.get("message"),
                metadata=metadata,
            )


def _build_optimizer_trace_fields(
    *,
    period: object | None,
    schedules: list,
    trace_context: OptimizationTraceContext,
) -> dict:
    recheck = build_recheck_report(
        period=period,
        schedules=schedules,
        submissions_by_section={},
        enrollments_by_section={},
    )
    _link_trace_recheck_issues(trace_context, recheck.get("issues", []))
    observer_payload = observe_optimization_result(
        period=period,
        schedules=schedules,
        submissions_by_section={},
        enrollments_by_section={},
        trace_context=trace_context,
    )
    return {
        "native_trace_summary": observer_payload.get("native_trace_summary", {}),
        "native_trace_events": observer_payload.get("native_trace_events", []),
        "traceability_completeness_score": observer_payload.get("traceability_completeness_score", 0.0),
        "trace_source_breakdown": observer_payload.get("trace_source_breakdown", {}),
    }


def _load_optimizer_trace_schedules(
    db: Session,
    *,
    period: object | None,
    data,
) -> list:
    if not period:
        return []
    return (
        db.query(models.ExamSchedule)
        .join(models.Section)
        .filter(
            models.Section.academic_year == data.academic_year,
            models.Section.semester == data.semester,
            models.ExamSchedule.exam_type == _optimizer_exam_type_value(data),
        )
        .options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.section).joinedload(models.Section.teaching_room),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        )
        .all()
    )


# ── CRUD ──────────────────────────────────────────────────────
@router.get("/", response_model=List[schemas.ScheduleWithSection])
def list_schedules(
    date:         Optional[str] = Query(None),  # frontend compatibility
    exam_date:    Optional[str] = None,   # filter by date (YYYY-MM-DD)
    room_id:      Optional[int] = None,   # filter by room
    status:       Optional[str] = None,   # draft|published|locked
    page:         int = 1,
    limit:        int = 200,              # max 500
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if limit > 500:
        limit = 500
    if page < 1:
        page = 1
    offset = (page - 1) * limit
    target_date = exam_date or date
    q = _build_schedule_query(
        db=db,
        current_user=current_user,
        exam_date=target_date,
        room_id=room_id,
        status=status,
    )

    # Teacher เห็นเฉพาะตารางของตัวเอง
    return q.order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time
    ).offset(offset).limit(limit).all()


@router.get("/grouped")
def schedule_grouped(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ตารางสอบจัดกลุ่มตามวันที่ สำหรับหน้า Schedule"""
    schedules = _build_schedule_query(
        db=db,
        current_user=current_user,
    ).order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time
    ).all()
    return _group_schedules_by_date(schedules)


def _sch_to_dict(s: models.ExamSchedule) -> dict:
    return _serialize_schedule(s)


@router.post("/", response_model=schemas.ScheduleOut)
def create_schedule(
    data: schemas.ScheduleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    # Check section ไม่มี schedule แล้ว
    exists = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.section_id == data.section_id
    ).first()
    if exists:
        raise HTTPException(400, "Section นี้มีตารางสอบแล้ว")

    section = db.query(models.Section).filter(
        models.Section.id == data.section_id
    ).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")

    require_period_editable_for_values(
        db,
        section.academic_year,
        section.semester,
        data.exam_type.value if hasattr(data.exam_type, "value") else data.exam_type,
    )
    total_sheets = section.num_students * data.num_pages
    sch = models.ExamSchedule(
        **data.model_dump(),
        **_normalize_schedule_time_fields(data.exam_time),
        total_sheets=total_sheets,
    )
    db.add(sch)
    db.commit()
    trace_schedules = _load_optimizer_trace_schedules(
        db,
        period=period,
        data=data,
    )
    trace_fields = _build_optimizer_trace_fields(
        period=period,
        schedules=trace_schedules,
        trace_context=trace_context,
    )
    db.refresh(sch)
    log_action(db, current_user, "CREATE_SCHEDULE", "exam_schedules", sch.id,
               new_values=data.model_dump(), request=request)
    return db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions),
    ).filter(models.ExamSchedule.id == sch.id).first()


@router.put("/{sid}", response_model=schemas.ScheduleOut)
def update_schedule(
    sid: int,
    data: schemas.ScheduleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    if is_view_all_role(current_user):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
    if not sch:
        raise HTTPException(404, "ไม่พบตารางสอบ")

    section = sch.section or db.query(models.Section).filter(
        models.Section.id == sch.section_id
    ).first()
    if section:
        require_period_editable_for_values(
            db,
            section.academic_year,
            section.semester,
            sch.exam_type.value if hasattr(sch.exam_type, "value") else sch.exam_type,
        )

    for k, v in data.model_dump(exclude_none=True).items():
        setattr(sch, k, v)
    if data.exam_time is not None:
        time_fields = _normalize_schedule_time_fields(data.exam_time)
        sch.exam_time_start = time_fields["exam_time_start"]
        sch.exam_time_end = time_fields["exam_time_end"]

    # คำนวณ total_sheets ใหม่
    if data.num_pages is not None:
        section = db.query(models.Section).filter(
            models.Section.id == sch.section_id
        ).first()
        if section:
            sch.total_sheets = section.num_students * sch.num_pages

    db.commit()
    db.refresh(sch)
    log_action(db, current_user, "UPDATE_SCHEDULE", "exam_schedules", sid, request=request)
    return db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions),
    ).filter(models.ExamSchedule.id == sid).first()


@router.delete("/{sid}")
def delete_schedule(
    sid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
    if not sch:
        raise HTTPException(404, "ไม่พบตารางสอบ")
    section = sch.section or db.query(models.Section).filter(
        models.Section.id == sch.section_id
    ).first()
    if section:
        require_period_editable_for_values(
            db,
            section.academic_year,
            section.semester,
            sch.exam_type.value if hasattr(sch.exam_type, "value") else sch.exam_type,
        )
    db.delete(sch)
    db.commit()
    log_action(db, current_user, "DELETE_SCHEDULE", "exam_schedules", sid, request=request)
    return {"success": True}


# ── Supervision ───────────────────────────────────────────────
@router.post("/{sid}/supervision")
def assign_supervision(
    sid: int,
    user_id: int,
    slot_order: int = 1,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
    if not sch:
        raise HTTPException(404, "ไม่พบตารางสอบ")

    section = sch.section or db.query(models.Section).filter(
        models.Section.id == sch.section_id
    ).first()
    if section:
        require_period_editable_for_values(
            db,
            section.academic_year,
            section.semester,
            sch.exam_type.value if hasattr(sch.exam_type, "value") else sch.exam_type,
        )

    existing = db.query(models.Supervision).filter(
        models.Supervision.schedule_id == sid,
        models.Supervision.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(400, "อาจารย์ท่านนี้อยู่ในตารางนี้แล้ว")

    sup = models.Supervision(
        schedule_id=sid,
        user_id=user_id,
        slot_order=slot_order,
        compensation=300.0 if slot_order == 1 else 200.0,
    )
    db.add(sup)
    db.commit()
    log_action(db, current_user, "ASSIGN_SUPERVISION", "supervisions", sup.id, request=request)
    return {"success": True, "supervision_id": sup.id}


@router.delete("/{sid}/supervision/{sup_id}")
def remove_supervision(
    sid: int,
    sup_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    sup = db.query(models.Supervision).filter(
        models.Supervision.id == sup_id,
        models.Supervision.schedule_id == sid
    ).first()
    if not sup:
        raise HTTPException(404, "ไม่พบข้อมูลกรรมการ")
    schedule = sup.schedule or db.query(models.ExamSchedule).filter(
        models.ExamSchedule.id == sid
    ).first()
    section = schedule.section if schedule else None
    if section:
        require_period_editable_for_values(
            db,
            section.academic_year,
            section.semester,
            schedule.exam_type.value if hasattr(schedule.exam_type, "value") else schedule.exam_type,
        )
    db.delete(sup)
    db.commit()
    log_action(db, current_user, "DELETE_SUPERVISION", "supervisions", sup_id, request=request)
    return {"success": True}


# ── Copy Count Summary ────────────────────────────────────────
@router.get("/copy-count")
def copy_count_summary(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin)
):
    schedules = db.query(models.ExamSchedule).join(models.Section).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
    ).filter(
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).all()

    section_ids = [schedule.section_id for schedule in schedules]
    submission_map = {}
    if section_ids:
        submissions = db.query(models.ExamSubmission).options(
            joinedload(models.ExamSubmission.material_request),
        ).filter(models.ExamSubmission.section_id.in_(section_ids)).all()
        submission_map = {submission.section_id: submission for submission in submissions}

    rows = []
    total = 0
    for s in schedules:
        sec = s.section
        course = sec.course if sec else None
        submission = submission_map.get(sec.id if sec else -1)
        material_request = submission.material_request if submission else None
        rows.append({
            "course_id": course.course_id if course else "",
            "course_name_th": course.course_name_th if course else "",
            "section_no": sec.section_no if sec else "",
            "num_students": sec.num_students if sec else 0,
            "num_pages": s.num_pages,
            "total_sheets": s.total_sheets,
            "exam_date": s.exam_date,
            "exam_time": s.exam_time,
            "room": s.room.room_name if s.room else "",
            "print_duplex": bool(submission.print_duplex) if submission else False,
            "print_staple": submission.print_staple if submission and submission.print_staple else "none",
            "print_staple_page": submission.print_staple_page if submission else None,
            "print_note": submission.print_note if submission else None,
            "a4_pages_count": submission.a4_pages_count if submission else 0,
            "answer_formats": submission.answer_formats if submission else [],
            "answer_paper_sheets": material_request.answer_paper_sheets if material_request else 0,
            "answer_paper_staple": material_request.answer_paper_staple if material_request else False,
            "answer_booklet_count": material_request.answer_booklet_count if material_request else 0,
            "omr_sheet_count": material_request.omr_sheet_count if material_request else 0,
            "scratch_paper_sheets": material_request.scratch_paper_sheets if material_request else 0,
            "special_note": material_request.special_note if material_request else None,
        })
        total += s.total_sheets

    fraud_forms = 150  # แบบฟอร์มทุจริต
    grand_total = total + fraud_forms
    return {
        "rows": rows,
        "subtotal_exam": total,
        "fraud_forms": fraud_forms,
        "grand_total": grand_total,
        "cost": grand_total * 0.50,
        "sections_count": len(rows),
    }


# ── CP-SAT Optimizer ──────────────────────────────────────────
@router.post("/optimize", response_model=schemas.OptimizerResult)
def run_optimizer(
    data: schemas.OptimizerRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    """
    CP-SAT Optimizer สำหรับจัดตารางสอบอัตโนมัติ
    Input:  semester + academic_year + exam_type
    Output: assign ห้อง + กรรมการ + วันเวลา
    """
    try:
        from ortools.sat.python import cp_model
        has_ortools = True
    except ImportError:
        has_ortools = False

    require_period_editable_for_values(
        db,
        data.academic_year,
        data.semester,
        data.exam_type.value if hasattr(data.exam_type, "value") else data.exam_type,
    )

    sections = db.query(models.Section).filter(
        models.Section.semester == data.semester,
        models.Section.academic_year == data.academic_year,
    ).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
    ).all()

    rooms = db.query(models.Room).filter(models.Room.is_active == True).all()
    teachers = db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True
    ).all()

    unavail_map, room_unavail_map = _load_unavailability_maps(db, data)

    if not sections:
        raise HTTPException(400, "ไม่พบ sections ในเทอมที่ระบุ")
    if not rooms:
        raise HTTPException(400, "ไม่พบห้องสอบ")

    # Time slots ที่ใช้ได้ (จาก exam_dates จริงในระบบ หรือ default)
    time_slots = [
        ("2569-03-19", "15.30-18.30"),
        ("2569-03-20", "15.30-18.30"),
        ("2569-03-23", "09.00-12.00"),
        ("2569-03-23", "12.00-15.00"),
        ("2569-03-23", "15.30-18.30"),
        ("2569-03-24", "08.00-11.00"),
        ("2569-03-24", "12.00-15.00"),
        ("2569-03-24", "15.30-18.30"),
        ("2569-03-25", "09.00-12.00"),
        ("2569-03-25", "12.00-15.00"),
        ("2569-03-26", "09.00-12.00"),
        ("2569-03-26", "12.00-15.00"),
        ("2569-03-26", "15.30-18.30"),
        ("2569-03-27", "09.00-12.00"),
        ("2569-03-27", "12.00-15.00"),
        ("2569-03-27", "15.30-18.30"),
        ("2569-03-28", "09.00-12.00"),
        ("2569-03-28", "12.00-15.00"),
        ("2569-03-28", "15.30-18.30"),
    ]

    if not has_ortools:
        return _greedy_optimizer(
            sections,
            rooms,
            teachers,
            time_slots,
            data,
            db,
            current_user,
            request,
            unavail_map,
            room_unavail_map,
            trace_fallback_reason="ORTOOLS_UNAVAILABLE",
        )

    return _cpsat_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map, room_unavail_map)


def _greedy_optimizer(
    sections,
    rooms,
    teachers,
    time_slots,
    data,
    db,
    current_user,
    request,
    unavail_map=None,
    room_unavail_map=None,
    trace_context: OptimizationTraceContext | None = None,
    trace_fallback_reason: str | None = None,
):
    """Greedy fallback เมื่อ OR-Tools ไม่ได้ติดตั้ง"""
    assigned = 0
    violations = []
    details = []
    created_schedules = []
    trace_context = trace_context or OptimizationTraceContext(
        session_id=_optimizer_trace_session_id(data)
    )
    if trace_fallback_reason:
        trace_context.add_event(
            event_type="FALLBACK_USED",
            stage="SELECTION",
            entity_type="optimization_run",
            entity_id=_optimizer_trace_session_id(data),
            reason_code=REASON_CODE_FALLBACK_USED,
            source=TRACE_SOURCE_FALLBACK,
            message="Greedy optimizer was used at the optimizer boundary.",
            metadata={
                "algorithm": "greedy",
                "fallback_reason": trace_fallback_reason,
            },
        )

    # Track: slot → rooms ที่ใช้แล้ว
    slot_room_used = defaultdict(set)
    # Track: slot → teachers ที่คุมสอบแล้ว
    slot_teacher_used = defaultdict(set)
    # Track: teacher → จำนวนครั้งที่คุมสอบ (fairness)
    teacher_count = defaultdict(int)

    teacher_list = list(teachers)

    # โหลด room_keepers (ธีราภัณฑ์ + ชนะชล) สำหรับ assign ดูแลห้อง
    from auth_utils import is_room_keeper as _is_rk
    _room_keepers = [u for u in (db.query(models.User)
        .filter(models.User.role == models.UserRole.staff, models.User.is_active == True)
        .all()) if _is_rk(u)]

    # สร้าง co_exam group map: section_id → group
    co_groups = {}
    if hasattr(models, 'CoExamMember'):
        try:
            members = db.query(models.CoExamMember).options(
                __import__('sqlalchemy.orm', fromlist=['joinedload']).joinedload(models.CoExamMember.group)
            ).join(models.Section).filter(
                models.Section.semester      == data.semester,
                models.Section.academic_year == data.academic_year,
            ).all()
            for m in members:
                co_groups[m.section_id] = m.group
        except Exception:
            pass  # table ยังไม่มี — ข้าม

    # sections ที่เป็น co_exam หัวหน้ากลุ่ม (section แรกของกลุ่ม)
    processed_co_groups = set()

    for section in sections:
        # Skip ถ้ามีตารางสอบแล้ว
        if _get_schedule(section):
            continue

        # Co-exam: ถ้า section นี้อยู่ในกลุ่ม และกลุ่มนี้ถูก process แล้ว → skip
        co_group = co_groups.get(section.id)
        if co_group and co_group.id in processed_co_groups:
            continue

        assigned_slot = None
        assigned_room = None

        for slot in time_slots:
            date, time = slot
            # หาห้องที่จุได้พอ
            for room in sorted(rooms, key=lambda r: r.capacity):
                if room.id in slot_room_used[slot]:
                    continue
                if _is_room_unavailable(room_unavail_map, room.id, date, time):
                    continue
                if room.capacity >= section.num_students:
                    assigned_slot = slot
                    assigned_room = room
                    break
            if assigned_slot:
                break

        if not assigned_slot:
            violations.append(f"ไม่สามารถจัดห้องให้ {section.course.course_id} Sec{section.section_no} ได้")
            continue

        # เลือก supervisor (fairness: เลือกคนที่คุมสอบน้อยสุด)
        avail_date = assigned_slot[0]
        avail_time = assigned_slot[1]
        available_teachers = [
            t for t in teacher_list
            if t.id not in slot_teacher_used[assigned_slot]
            and t.id != (section.teacher_id or -1)
            and not _is_staff_unavailable(unavail_map, t.id, avail_date, avail_time)
        ]
        available_teachers.sort(key=lambda t: teacher_count[t.id])

        sup1 = available_teachers[0] if len(available_teachers) > 0 else None
        sup2 = available_teachers[1] if len(available_teachers) > 1 else None
        sup1_load_before = teacher_count[sup1.id] if sup1 else None
        sup2_load_before = teacher_count[sup2.id] if sup2 else None

        # สร้าง ExamSchedule
        sch = models.ExamSchedule(
            section_id=section.id,
            room_id=assigned_room.id,
            exam_date=assigned_slot[0],
            exam_time=assigned_slot[1],
            exam_time_start=parse_time_range(assigned_slot[1])[0],
            exam_time_end=parse_time_range(assigned_slot[1])[1],
            exam_type=data.exam_type,
            status=models.ScheduleStatus.draft,
            num_pages=1,
            total_sheets=section.num_students * 1,
        )
        db.add(sch)
        db.flush()
        created_schedules.append(sch)

        # Assign supervisions
        if sup1:
            db.add(models.Supervision(
                schedule_id=sch.id, user_id=sup1.id,
                slot_order=1, compensation=300.0
            ))
            slot_teacher_used[assigned_slot].add(sup1.id)
            teacher_count[sup1.id] += 1

        if sup2:
            db.add(models.Supervision(
                schedule_id=sch.id, user_id=sup2.id,
                slot_order=2, compensation=200.0
            ))
            slot_teacher_used[assigned_slot].add(sup2.id)
            teacher_count[sup2.id] += 1

        slot_room_used[assigned_slot].add(assigned_room.id)
        assigned += 1

        details.append({
            "section_id": section.id,
            "course_id": section.course.course_id,
            "section_no": section.section_no,
            "date": assigned_slot[0],
            "time": assigned_slot[1],
            "room": assigned_room.room_name,
            "supervisors": [
                sup1.full_name if sup1 else None,
                sup2.full_name if sup2 else None,
            ]
        })

        # Room keeper assignment — หมุนเวียนรายวัน (ใช้ day-of-year parity)
        slot_label = _slot_trace_label(assigned_slot[0], assigned_slot[1])
        selected_staff_ids = [staff.id for staff in (sup1, sup2) if staff is not None]

        trace_timeslot_candidate(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id=slot_label,
            source=TRACE_SOURCE_FALLBACK,
            time_slot=slot_label,
            message="Greedy optimizer selected a timeslot candidate.",
        )
        trace_room_candidate(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id=assigned_room.id,
            source=TRACE_SOURCE_FALLBACK,
            message="Greedy optimizer selected a room candidate.",
            capacity=getattr(assigned_room, "capacity", None),
            assigned_count=getattr(section, "num_students", 0),
            building=getattr(assigned_room, "building", None),
            room_type=getattr(assigned_room, "room_type", None),
        )
        trace_room_selection(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id=assigned_room.id,
            selected_candidate={
                "room_id": assigned_room.id,
                "room_name": assigned_room.room_name,
                "capacity": getattr(assigned_room, "capacity", None),
                "building": getattr(assigned_room, "building", None),
                "exam_date": assigned_slot[0],
                "exam_time": assigned_slot[1],
            },
            accepted_reason="GREEDY_CAPACITY_MATCH",
            tradeoffs_accepted=["FALLBACK_USED"],
            contributing_constraints=["ROOM_CAPACITY", "ROOM_AVAILABILITY"],
            quality_impact={"assigned_students": getattr(section, "num_students", 0)},
            governance_relevance="RECHECK_PENDING",
            confidence_level="MEDIUM",
            source=TRACE_SOURCE_FALLBACK,
        )
        trace_capacity_constraint(
            trace_context,
            passed=(getattr(assigned_room, "capacity", 0) or 0) >= (getattr(section, "num_students", 0) or 0),
            entity_type="section",
            entity_id=section.id,
            reason_code="ROOM_CAPACITY_CONFIRMED",
            metadata={
                "room_id": assigned_room.id,
                "student_count": getattr(section, "num_students", 0),
                "capacity": getattr(assigned_room, "capacity", None),
            },
        )
        trace_split_candidate(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id="single-room-allocation",
            source=TRACE_SOURCE_FALLBACK,
            message="Greedy optimizer used a single-room split candidate.",
            assigned_count=1,
        )
        trace_split_selection(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id="single-room-allocation",
            selected_candidate={"split_count": 1, "split_reason": "SINGLE_ROOM_ALLOCATION"},
            accepted_reason="NO_SPLIT_REQUIRED",
            contributing_constraints=["ROOM_CAPACITY"],
            governance_relevance="LOW",
            confidence_level="MEDIUM",
            source=TRACE_SOURCE_FALLBACK,
        )
        for staff_obj, staff_load_before, slot_order in (
            (sup1, sup1_load_before, 1),
            (sup2, sup2_load_before, 2),
        ):
            if staff_obj is None:
                continue
            trace_staff_candidate(
                trace_context,
                entity_type="section",
                entity_id=section.id,
                candidate_id=staff_obj.id,
                source=TRACE_SOURCE_FALLBACK,
                message="Greedy optimizer selected a staff candidate.",
                staff_current_load=staff_load_before,
                staff_role="INVIGILATOR",
                time_slot=slot_label,
            )
            trace_staff_selection(
                trace_context,
                entity_type="section",
                entity_id=section.id,
                candidate_id=staff_obj.id,
                selected_candidate={
                    "staff_id": staff_obj.id,
                    "slot_order": slot_order,
                    "time_slot": slot_label,
                },
                accepted_reason="LOWEST_CURRENT_LOAD",
                tradeoffs_accepted=[REASON_CODE_FAIRNESS_PENALTY],
                contributing_constraints=["STAFFING_AVAILABILITY", "WORKLOAD_BALANCE"],
                quality_impact={"staff_current_load": staff_load_before},
                governance_relevance="RECHECK_PENDING",
                confidence_level="MEDIUM",
                source=TRACE_SOURCE_FALLBACK,
            )
        trace_staffing_constraint(
            trace_context,
            passed=bool(selected_staff_ids),
            entity_type="section",
            entity_id=section.id,
            reason_code="STAFFING_CONFIRMED" if selected_staff_ids else "MISSING_INVIGILATOR",
            source=TRACE_SOURCE_FALLBACK,
            metadata={
                "selected_staff_ids": selected_staff_ids,
                "available_staff_count": len(available_teachers),
                "time_slot": slot_label,
            },
        )
        if selected_staff_ids:
            trace_context.add_tradeoff_chosen(
                entity_type="section",
                entity_id=section.id,
                candidate_type="STAFF",
                candidate_id=selected_staff_ids[0],
                reason_code=REASON_CODE_FAIRNESS_PENALTY,
                source=TRACE_SOURCE_FALLBACK,
                message="Greedy staff selection prioritized lower current workloads.",
                metadata={
                    "selected_staff_ids": selected_staff_ids,
                    "selected_staff_loads": [load for load in (sup1_load_before, sup2_load_before) if load is not None],
                    "available_staff_count": len(available_teachers),
                },
            )
        trace_final_schedule_selection(
            trace_context,
            entity_type="section",
            entity_id=section.id,
            candidate_id=sch.id,
            selected_candidate={
                "schedule_id": sch.id,
                "room_id": assigned_room.id,
                "staff_ids": selected_staff_ids,
                "exam_date": assigned_slot[0],
                "exam_time": assigned_slot[1],
                "split_count": 1,
            },
            accepted_reason="GREEDY_FINALIZED",
            tradeoffs_accepted=["FALLBACK_USED"],
            contributing_constraints=["ROOM_CAPACITY", "STAFFING_AVAILABILITY"],
            quality_impact={"assigned_students": getattr(section, "num_students", 0)},
            governance_relevance="RECHECK_PENDING",
            confidence_level="MEDIUM",
            source=TRACE_SOURCE_FALLBACK,
        )

        if _room_keepers:
            try:
                import datetime as _dt
                exam_d = _to_date(assigned_slot[0])
                if exam_d:
                    day_num = exam_d.timetuple().tm_yday
                    # วันคี่ = keeper[0], วันคู่ = keeper[1]
                    keeper = _room_keepers[day_num % len(_room_keepers)]
                    # ตรวจว่า keeper ไม่ได้ assign ห้องนี้แล้ว
                    already = db.query(models.Supervision).filter(
                        models.Supervision.schedule_id == new_sch.id,
                        models.Supervision.user_id     == keeper.id,
                    ).first() if hasattr(new_sch, 'id') else None
                    if not already:
                        db.add(models.Supervision(
                            schedule_id  = new_sch.id,
                            user_id      = keeper.id,
                            slot_order   = 99,        # slot พิเศษ — ไม่นับใน fairness
                            role_in_exam = "room_keeper",
                        ))
            except Exception:
                pass   # ถ้า assign ไม่ได้ → ข้าม

        # Co-exam: mark กลุ่ม + assign วัน/เวลาเดียวกันให้ทุก section ในกลุ่ม
        if co_group:
            processed_co_groups.add(co_group.id)
            for other_m in (co_group.members if hasattr(co_group, 'members') else []):
                other_sec = other_m.section if other_m else None
                if not other_sec or other_sec.id == section.id:
                    continue
                if _get_schedule(other_sec):
                    continue
                # ใช้ห้องเดียวกัน slot เดียวกัน
                other_sch = models.ExamSchedule(
                    section_id   = other_sec.id,
                    room_id      = assigned_room.id,
                    exam_date    = assigned_slot[0],
                    exam_time    = assigned_slot[1],
                    exam_time_start = parse_time_range(assigned_slot[1])[0],
                    exam_time_end = parse_time_range(assigned_slot[1])[1],
                    exam_type    = data.exam_type,
                    status       = models.ScheduleStatus.draft,
                    num_pages    = 1,
                    total_sheets = other_sec.num_students or 0,
                )
                db.add(other_sch)
                assigned += 1
                slot_room_used[assigned_slot].add(assigned_room.id)
                details.append({
                    "section_id": other_sec.id,
                    "course_id":  other_sec.course.course_id if other_sec.course else "?",
                    "section_no": other_sec.section_no,
                    "date":       assigned_slot[0],
                    "time":       assigned_slot[1],
                    "room":       assigned_room.room_name,
                    "co_exam":    True,
                    "co_group":   co_group.label,
                    "supervisors": [
                        sup1.full_name if sup1 else None,
                        sup2.full_name if sup2 else None,
                    ]
                })

    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == data.academic_year,
        models.ExamPeriod.semester == data.semester,
        models.ExamPeriod.exam_type == data.exam_type.value,
    ).first()
    distribution_result = (
        assign_paper_distribution_for_period(db, period, current_user.id)
        if period
        else {"assigned_count": 0, "slot_count": 0, "unfilled_count": 0, "warnings": []}
    )

    db.commit()

    # Fairness score (std deviation ต่ำ = ดี)
    import statistics
    counts = list(teacher_count.values())
    fairness = round(statistics.stdev(counts), 2) if len(counts) > 1 else 0.0

    # เพิ่ม esq_head ใน fairness display (load=0 แต่ปรากฏในรายงาน)
    from auth_utils import show_in_fairness_stat as _show_stat
    esq_in_stat = [
        {"id": u.id, "full_name": u.full_name, "load": 0,
         "note": "ยกเว้น — ไม่นับ load"}
        for u in (db.query(models.User).filter(
            models.User.is_active == True
        ).all()) if _show_stat(u)
    ]

    log_action(db, current_user, "RUN_OPTIMIZER",
               new_values={"assigned": assigned, "algorithm": "greedy"},
               request=request)

    # ── นภาภรณ์ (esq_head) — แสดงใน fairness stat แต่ load=0 ──
    esq_head_user = db.query(models.User).filter(
        models.User.role == models.UserRole.esq_head,
        models.User.is_active == True,
    ).first()
    esq_staff_excluded = []
    if esq_head_user:
        esq_staff_excluded = [{
            "id":        esq_head_user.id,
            "full_name": esq_head_user.full_name,
            "unit":      "ESQ Head",
            "reason":    "ผู้ช่วยหัวหน้าสำนักงาน — ไม่ถูกรวมในการคุมสอบ",
        }]
    # room_keepers ที่ถูก assign แล้ว (สลับวัน)
    from auth_utils import is_room_keeper as _is_rk2
    room_keepers_assigned = [
        {"id": u.id, "full_name": u.full_name}
        for u in (db.query(models.User).filter(
            models.User.role == models.UserRole.staff,
            models.User.is_active == True
        ).all()) if _is_rk2(u)
    ]

    reminder_msg = None
    if esq_staff_excluded:
        names = ", ".join(e["full_name"] for e in esq_staff_excluded)
        reminder_msg = f"ℹ {names} — ไม่ถูกรวมในการคุมสอบ (ปรากฏในสถิติ load=0)"

    return schemas.OptimizerResult(
        success=True,
        sections_assigned=assigned,
        sections_total=len(sections),
        fairness_score=fairness,
        violations=violations,
        details=details,
        paper_distribution_assigned=distribution_result["assigned_count"],
        paper_distribution_slots=distribution_result["slot_count"],
        paper_distribution_unfilled=distribution_result["unfilled_count"],
        paper_distribution_warnings=distribution_result["warnings"],
        esq_staff_excluded=esq_staff_excluded,
        esq_in_stat=esq_in_stat if "esq_in_stat" in dir() else [],
        room_keepers_assigned=room_keepers_assigned,
        reminder=reminder_msg,
        native_trace_summary=trace_fields["native_trace_summary"],
        native_trace_events=trace_fields["native_trace_events"],
        traceability_completeness_score=trace_fields["traceability_completeness_score"],
        trace_source_breakdown=trace_fields["trace_source_breakdown"],
    )


def _cpsat_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map=None, room_unavail_map=None):
    """CP-SAT (OR-Tools) optimizer — ค้นหา assignment ที่ optimize fairness"""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    n_sections = len(sections)
    n_rooms = len(rooms)
    n_slots = len(time_slots)
    n_teachers = len(teachers)
    trace_context = OptimizationTraceContext(
        session_id=_optimizer_trace_session_id(data)
    )

    # Variables: x[s][r][t] = 1 ถ้า section s ใช้ room r ใน slot t
    x = {}
    for s in range(n_sections):
        for r in range(n_rooms):
            for t in range(n_slots):
                x[s, r, t] = model.NewBoolVar(f"x_s{s}_r{r}_t{t}")

    # Constraint 1: แต่ละ section ต้องได้ 1 slot (ถ้ายังไม่ถูก assign)
    unscheduled = [s for s in sections if not s.schedule]
    for s_idx, section in enumerate(sections):
        if not _get_schedule(section):
            model.Add(sum(x[s_idx, r, t]
                          for r in range(n_rooms)
                          for t in range(n_slots)) == 1)
        else:
            for r in range(n_rooms):
                for t in range(n_slots):
                    model.Add(x[s_idx, r, t] == 0)

    # Constraint 2: ห้องหนึ่งใน slot เดียวกัน มีได้แค่ 1 section
    for r in range(n_rooms):
        for t in range(n_slots):
            model.Add(sum(x[s, r, t] for s in range(n_sections)) <= 1)

    # Constraint 3: ห้องต้องจุได้พอ
    for s_idx, section in enumerate(sections):
        for r_idx, room in enumerate(rooms):
            if room.capacity < section.num_students:
                for t in range(n_slots):
                    model.Add(x[s_idx, r_idx, t] == 0)

    # Constraint 3b: room unavailability
    if room_unavail_map:
        for r_idx, room in enumerate(rooms):
            for t_idx, slot in enumerate(time_slots):
                date, time = slot
                if _is_room_unavailable(room_unavail_map, room.id, date, time):
                    for s in range(n_sections):
                        model.Add(x[s, r_idx, t_idx] == 0)

    # Constraint 3c: staff unavailability (ใน CP-SAT ทำผ่าน allowed_teachers)
    allowed_per_slot = {}
    for t_idx, slot in enumerate(time_slots):
        date, time = slot
        allowed_per_slot[t_idx] = [
            tc_idx for tc_idx, teacher in enumerate(teachers)
            if not _is_staff_unavailable(unavail_map, teacher.id, date, time)
        ]

    # Supervision variables: y[t][teacher] = จำนวนครั้งคุมสอบใน slot t
    t_count = {}
    for tc_idx in range(n_teachers):
        t_count[tc_idx] = model.NewIntVar(0, n_slots, f"tcount_{tc_idx}")
        # นับจาก sections ที่ teacher นั้น supervise
        model.Add(t_count[tc_idx] == sum(
            x[s, r, t]
            for s in range(n_sections)
            for r in range(n_rooms)
            for t in range(n_slots)
        ) // max(n_teachers, 1))  # approximation

    # Objective: minimize max - min teacher load (fairness)
    max_load = model.NewIntVar(0, n_sections, "max_load")
    min_load = model.NewIntVar(0, n_sections, "min_load")
    for tc in range(n_teachers):
        model.Add(t_count[tc] <= max_load)
        model.Add(t_count[tc] >= min_load)
    model.Minimize(max_load - min_load)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        trace_context.add_event(
            event_type="FALLBACK_USED",
            stage="SELECTION",
            entity_type="optimization_run",
            entity_id=_optimizer_trace_session_id(data),
            reason_code=REASON_CODE_FALLBACK_USED,
            source=TRACE_SOURCE_FALLBACK,
            message="CP-SAT did not produce a feasible result, so greedy fallback was used.",
            metadata={
                "algorithm": "CP-SAT",
                "fallback_algorithm": "greedy",
                "solver_status": int(status),
            },
        )
        return _greedy_optimizer(
            sections,
            rooms,
            teachers,
            time_slots,
            data,
            db,
            current_user,
            request,
            unavail_map,
            room_unavail_map,
            trace_context=trace_context,
        )

    # Extract solution
    assigned = 0
    details = []
    created_schedules = []
    teacher_count = defaultdict(int)
    slot_teacher_used = defaultdict(set)
    trace_context.add_penalty_applied(
        entity_type="optimization_run",
        entity_id=_optimizer_trace_session_id(data),
        candidate_type="STAFF",
        reason_code=REASON_CODE_FAIRNESS_PENALTY,
        source=TRACE_SOURCE_SOLVER,
        message="CP-SAT minimized max-minus-min staff load as the fairness objective.",
        metadata={
            "objective": "MINIMIZE_MAX_MINUS_MIN_LOAD",
            "solver_status": int(status),
        },
    )

    for s_idx, section in enumerate(sections):
        if _get_schedule(section):
            continue
        for r_idx, room in enumerate(rooms):
            for t_idx, slot in enumerate(time_slots):
                if solver.Value(x[s_idx, r_idx, t_idx]) == 1:
                    # เลือก supervisors
                    available = [
                        t for t in teachers
                        if t.id not in slot_teacher_used[t_idx]
                        and t.id != (section.teacher_id or -1)
                        and not _interval_staff_unavailable(
                            unavail_map,
                            t.id,
                            slot[0],
                            slot[1],
                            parse_time_range(slot[1])[0],
                            parse_time_range(slot[1])[1],
                        )
                    ]
                    available.sort(key=lambda t: teacher_count[t.id])
                    sup1 = available[0] if available else None
                    sup2 = available[1] if len(available) > 1 else None
                    sup1_load_before = teacher_count[sup1.id] if sup1 else None
                    sup2_load_before = teacher_count[sup2.id] if sup2 else None

                    sch = models.ExamSchedule(
                        section_id=section.id,
                        room_id=room.id,
                        exam_date=slot[0],
                        exam_time=slot[1],
                        exam_time_start=parse_time_range(slot[1])[0],
                        exam_time_end=parse_time_range(slot[1])[1],
                        exam_type=data.exam_type,
                        status=models.ScheduleStatus.draft,
                        num_pages=1,
                        total_sheets=section.num_students,
                    )
                    db.add(sch)
                    db.flush()
                    created_schedules.append(sch)

                    if sup1:
                        db.add(models.Supervision(
                            schedule_id=sch.id, user_id=sup1.id,
                            slot_order=1, compensation=300.0
                        ))
                        slot_teacher_used[t_idx].add(sup1.id)
                        teacher_count[sup1.id] += 1
                    if sup2:
                        db.add(models.Supervision(
                            schedule_id=sch.id, user_id=sup2.id,
                            slot_order=2, compensation=200.0
                        ))
                        slot_teacher_used[t_idx].add(sup2.id)
                        teacher_count[sup2.id] += 1

                    assigned += 1
                    details.append({
                        "section_id": section.id,
                        "course_id": section.course.course_id,
                        "section_no": section.section_no,
                        "date": slot[0],
                        "time": slot[1],
                        "room": room.room_name,
                    })
                    slot_label = _slot_trace_label(slot[0], slot[1])
                    selected_staff_ids = [staff.id for staff in (sup1, sup2) if staff is not None]
                    solver_status_label = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"

                    trace_timeslot_candidate(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id=slot_label,
                        source=TRACE_SOURCE_SOLVER,
                        time_slot=slot_label,
                        message="CP-SAT selected a timeslot candidate.",
                    )
                    trace_room_candidate(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id=room.id,
                        source=TRACE_SOURCE_SOLVER,
                        message="CP-SAT selected a room candidate.",
                        capacity=getattr(room, "capacity", None),
                        assigned_count=getattr(section, "num_students", 0),
                        building=getattr(room, "building", None),
                        room_type=getattr(room, "room_type", None),
                    )
                    trace_room_selection(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id=room.id,
                        selected_candidate={
                            "room_id": room.id,
                            "room_name": room.room_name,
                            "capacity": getattr(room, "capacity", None),
                            "building": getattr(room, "building", None),
                            "exam_date": slot[0],
                            "exam_time": slot[1],
                        },
                        accepted_reason="CP_SAT_FEASIBLE_ASSIGNMENT",
                        contributing_constraints=["ROOM_CAPACITY", "ROOM_AVAILABILITY", "PERIOD_WINDOW"],
                        quality_impact={"solver_status": solver_status_label},
                        governance_relevance="RECHECK_PENDING",
                        confidence_level="HIGH",
                        source=TRACE_SOURCE_SOLVER,
                    )
                    trace_capacity_constraint(
                        trace_context,
                        passed=(getattr(room, "capacity", 0) or 0) >= (getattr(section, "num_students", 0) or 0),
                        entity_type="section",
                        entity_id=section.id,
                        reason_code="ROOM_CAPACITY_CONFIRMED",
                        metadata={
                            "room_id": room.id,
                            "student_count": getattr(section, "num_students", 0),
                            "capacity": getattr(room, "capacity", None),
                        },
                    )
                    trace_split_candidate(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id="single-room-allocation",
                        source=TRACE_SOURCE_SOLVER,
                        message="CP-SAT used a single-room split candidate.",
                        assigned_count=1,
                    )
                    trace_split_selection(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id="single-room-allocation",
                        selected_candidate={"split_count": 1, "split_reason": "SINGLE_ROOM_ALLOCATION"},
                        accepted_reason="NO_SPLIT_REQUIRED",
                        contributing_constraints=["ROOM_CAPACITY"],
                        governance_relevance="LOW",
                        confidence_level="HIGH",
                        source=TRACE_SOURCE_SOLVER,
                    )
                    for staff_obj, staff_load_before, slot_order in (
                        (sup1, sup1_load_before, 1),
                        (sup2, sup2_load_before, 2),
                    ):
                        if staff_obj is None:
                            continue
                        trace_staff_candidate(
                            trace_context,
                            entity_type="section",
                            entity_id=section.id,
                            candidate_id=staff_obj.id,
                            source=TRACE_SOURCE_FALLBACK,
                            message="Boundary supervisor assignment selected a staff candidate after CP-SAT room selection.",
                            staff_current_load=staff_load_before,
                            staff_role="INVIGILATOR",
                            time_slot=slot_label,
                        )
                        trace_staff_selection(
                            trace_context,
                            entity_type="section",
                            entity_id=section.id,
                            candidate_id=staff_obj.id,
                            selected_candidate={
                                "staff_id": staff_obj.id,
                                "slot_order": slot_order,
                                "time_slot": slot_label,
                            },
                            accepted_reason="LOWEST_CURRENT_LOAD",
                            tradeoffs_accepted=[REASON_CODE_FAIRNESS_PENALTY],
                            contributing_constraints=["STAFFING_AVAILABILITY", "WORKLOAD_BALANCE"],
                            quality_impact={"staff_current_load": staff_load_before},
                            governance_relevance="RECHECK_PENDING",
                            confidence_level="MEDIUM",
                            source=TRACE_SOURCE_FALLBACK,
                        )
                    trace_staffing_constraint(
                        trace_context,
                        passed=bool(selected_staff_ids),
                        entity_type="section",
                        entity_id=section.id,
                        reason_code="STAFFING_CONFIRMED" if selected_staff_ids else "MISSING_INVIGILATOR",
                        source=TRACE_SOURCE_FALLBACK,
                        metadata={
                            "selected_staff_ids": selected_staff_ids,
                            "available_staff_count": len(available),
                            "time_slot": slot_label,
                        },
                    )
                    if selected_staff_ids:
                        trace_context.add_tradeoff_chosen(
                            entity_type="section",
                            entity_id=section.id,
                            candidate_type="STAFF",
                            candidate_id=selected_staff_ids[0],
                            reason_code=REASON_CODE_FAIRNESS_PENALTY,
                            source=TRACE_SOURCE_FALLBACK,
                            message="Boundary supervisor assignment favored lower current workloads after CP-SAT room selection.",
                            metadata={
                                "selected_staff_ids": selected_staff_ids,
                                "selected_staff_loads": [load for load in (sup1_load_before, sup2_load_before) if load is not None],
                                "available_staff_count": len(available),
                            },
                        )
                    trace_final_schedule_selection(
                        trace_context,
                        entity_type="section",
                        entity_id=section.id,
                        candidate_id=sch.id,
                        selected_candidate={
                            "schedule_id": sch.id,
                            "room_id": room.id,
                            "staff_ids": selected_staff_ids,
                            "exam_date": slot[0],
                            "exam_time": slot[1],
                            "split_count": 1,
                        },
                        accepted_reason="CP_SAT_FINALIZED",
                        contributing_constraints=["ROOM_CAPACITY", "STAFFING_AVAILABILITY"],
                        quality_impact={"solver_status": solver_status_label},
                        governance_relevance="RECHECK_PENDING",
                        confidence_level="HIGH",
                        source=TRACE_SOURCE_SOLVER,
                    )

    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == data.academic_year,
        models.ExamPeriod.semester == data.semester,
        models.ExamPeriod.exam_type == data.exam_type.value,
    ).first()
    distribution_result = (
        assign_paper_distribution_for_period(db, period, current_user.id)
        if period
        else {"assigned_count": 0, "slot_count": 0, "unfilled_count": 0, "warnings": []}
    )

    db.commit()
    trace_schedules = _load_optimizer_trace_schedules(
        db,
        period=period,
        data=data,
    )
    trace_fields = _build_optimizer_trace_fields(
        period=period,
        schedules=trace_schedules,
        trace_context=trace_context,
    )
    import statistics
    counts = list(teacher_count.values())
    fairness = round(statistics.stdev(counts), 2) if len(counts) > 1 else 0.0

    log_action(db, current_user, "RUN_OPTIMIZER",
               new_values={"assigned": assigned, "algorithm": "CP-SAT"},
               request=request)

    return schemas.OptimizerResult(
        success=True,
        sections_assigned=assigned,
        sections_total=len(sections),
        fairness_score=fairness,
        violations=[],
        details=details,
        paper_distribution_assigned=distribution_result["assigned_count"],
        paper_distribution_slots=distribution_result["slot_count"],
        paper_distribution_unfilled=distribution_result["unfilled_count"],
        paper_distribution_warnings=distribution_result["warnings"],
        native_trace_summary=trace_fields["native_trace_summary"],
        native_trace_events=trace_fields["native_trace_events"],
        traceability_completeness_score=trace_fields["traceability_completeness_score"],
        trace_source_breakdown=trace_fields["trace_source_breakdown"],
    )
