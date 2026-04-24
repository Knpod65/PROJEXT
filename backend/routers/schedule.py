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
    build_staff_unavailability_map,
    is_staff_unavailable as _interval_staff_unavailable,
)
from term_lifecycle import require_period_editable_for_values
from time_ranges import normalize_time_range, parse_time_range, ranges_overlap

router = APIRouter()


def _schedule_time_bounds(exam_time: Optional[str], start: Optional[str] = None, end: Optional[str] = None):
    if start and end:
        return start, end
    return parse_time_range(exam_time)


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
    effective = get_effective_role(current_user)
    dept_filter = get_dept_filter(current_user)

    q = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teaching_room),
    )

    if exam_date:
        q = q.filter(models.ExamSchedule.exam_date == exam_date)
    if room_id is not None:
        q = q.filter(models.ExamSchedule.room_id == room_id)
    if status:
        try:
            q = q.filter(models.ExamSchedule.status == models.ScheduleStatus(status))
        except ValueError:
            raise HTTPException(400, f"status ไม่ถูกต้อง: {status}")

    if effective == models.UserRole.teacher:
        active_period = get_active_exam_period(db)
        q = q.join(models.Section)
        if active_period:
            owned_section_ids, _ = get_teacher_owned_section_ids(
                db,
                current_user.id,
                active_period.semester,
                active_period.academic_year,
            )
            if owned_section_ids is None:
                q = q.filter(models.Section.teacher_id == current_user.id)
            elif not owned_section_ids:
                q = q.filter(models.Section.id.in_([-1]))
            else:
                q = q.filter(models.Section.id.in_(owned_section_ids))
        else:
            q = q.filter(models.Section.teacher_id == current_user.id)
    elif dept_filter:
        group_clause = build_course_group_clause(models.Course.course_id, dept_filter)
        if group_clause is not None:
            q = q.join(models.Section).join(
                models.Course,
                models.Section.course_id == models.Course.id,
            ).filter(group_clause)
        else:
            q = q.filter(models.ExamSchedule.id.in_([-1]))

    return q


def _load_unavailability_maps(db: Session, data: schemas.OptimizerRequest):
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == data.academic_year,
        models.ExamPeriod.semester == data.semester,
        models.ExamPeriod.exam_type == data.exam_type.value,
    ).first()

    if not period:
        return {}, {}

    staff_map = build_staff_unavailability_map(db, period.id)
    room_map = defaultdict(list)

    for row in db.query(models.RoomUnavailability).filter(
        models.RoomUnavailability.exam_period_id == period.id
    ).all():
        start_time = getattr(row, "start_time", None)
        end_time = getattr(row, "end_time", None)
        if not (start_time and end_time):
            start_time, end_time = parse_time_range(row.block_time)
        room_map[row.room_id].append(
            {
                "date": str(row.block_date),
                "block_time": row.block_time or None,
                "start_time": start_time,
                "end_time": end_time,
                "all_day": row.block_time is None and not start_time and not end_time,
            }
        )

    return staff_map, room_map


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
    if not room_unavail_map:
        return False
    blocked = room_unavail_map.get(room_id, [])
    key_date = str(block_date)
    slot_start, slot_end = _schedule_time_bounds(block_time, block_start, block_end)
    for row in blocked:
        if row["date"] != key_date:
            continue
        if row["all_day"]:
            return True
        if row["block_time"] == block_time and row["block_time"] is not None:
            return True
        if ranges_overlap(slot_start, slot_end, row["start_time"], row["end_time"]):
            return True
    return False

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
    grouped = defaultdict(list)
    for s in schedules:
        grouped[s.exam_date].append(s)
    # เรียงวันที่
    result = []
    for date in sorted(grouped.keys()):
        result.append({
            "date": date,
            "items": [_sch_to_dict(s) for s in sorted(
                grouped[date], key=lambda x: x.exam_time
            )]
        })
    return result


def _sch_to_dict(s: models.ExamSchedule) -> dict:
    sec = s.section
    course = sec.course if sec else None
    teacher = sec.teacher if sec else None
    room = s.room
    sups = s.supervisions or []
    return {
        "id": s.id,
        "exam_date": s.exam_date,
        "exam_time": s.exam_time,
        "status": s.status,
        "num_pages": s.num_pages,
        "total_sheets": s.total_sheets,
        "paper_distributor": s.paper_distributor,
        "notes": s.notes,
        "room": {"id": room.id, "room_name": room.room_name, "capacity": room.capacity} if room else None,
        "section": {
            "id": sec.id,
            "section_no": sec.section_no,
            "num_students": sec.num_students,
            "is_co_exam": sec.is_co_exam,
            "teaching_room": (
                {
                    "id": sec.teaching_room.id,
                    "room_name": sec.teaching_room.room_name,
                    "capacity": sec.teaching_room.capacity,
                    "building": sec.teaching_room.building,
                }
                if sec and sec.teaching_room
                else None
            ),
        } if sec else None,
        "course": {
            "course_id": course.course_id,
            "course_name_th": course.course_name_th,
        } if course else None,
        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
        } if teacher else None,
        "supervisions": [
            {
                "slot_order": sup.slot_order,
                "user": {"id": sup.user.id, "full_name": sup.user.full_name} if sup.user else None,
                "confirmed": sup.confirmed,
            }
            for sup in sups
        ],
    }


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
        return _greedy_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map, room_unavail_map)

    return _cpsat_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map, room_unavail_map)


def _greedy_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map=None, room_unavail_map=None):
    """Greedy fallback เมื่อ OR-Tools ไม่ได้ติดตั้ง"""
    assigned = 0
    violations = []
    details = []

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
    )


def _cpsat_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map=None, room_unavail_map=None):
    """CP-SAT (OR-Tools) optimizer — ค้นหา assignment ที่ optimize fairness"""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    n_sections = len(sections)
    n_rooms = len(rooms)
    n_slots = len(time_slots)
    n_teachers = len(teachers)

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
        # Fallback to greedy
        return _greedy_optimizer(sections, rooms, teachers, time_slots, data, db, current_user, request, unavail_map, room_unavail_map)

    # Extract solution
    assigned = 0
    details = []
    teacher_count = defaultdict(int)
    slot_teacher_used = defaultdict(set)

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
    )
