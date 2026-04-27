"""
Public Router — ไม่ต้อง login
นักศึกษาค้นหาตารางสอบด้วยรหัสนักศึกษา
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from database import get_db
import models
from auth_utils import get_current_user

router = APIRouter()


def _get_active_period(db: Session):
    return db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()


def _load_enrollment_records(
    db: Session,
    student_id: str,
    active_period: models.ExamPeriod | None,
):
    query = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.student_id == student_id
    )

    if active_period:
        query = query.join(
            models.Section,
            models.EnrollmentRecord.section_id == models.Section.id,
        ).filter(
            models.Section.semester == active_period.semester,
            models.Section.academic_year == active_period.academic_year,
        )

    return query.options(
        joinedload(models.EnrollmentRecord.section)
            .joinedload(models.Section.course),
        joinedload(models.EnrollmentRecord.section)
            .joinedload(models.Section.teacher),
        joinedload(models.EnrollmentRecord.section)
            .selectinload(models.Section.schedules)
            .joinedload(models.ExamSchedule.room),
    ).order_by(
        models.EnrollmentRecord.import_session_id.desc(),
        models.EnrollmentRecord.id.desc(),
    ).all()


def _load_legacy_enrollments(
    db: Session,
    student_id: str,
    active_period: models.ExamPeriod | None,
):
    query = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id
    )

    if active_period:
        query = query.join(
            models.Section,
            models.Enrollment.section_id == models.Section.id,
        ).filter(
            models.Section.semester == active_period.semester,
            models.Section.academic_year == active_period.academic_year,
        )

    return query.options(
        joinedload(models.Enrollment.section)
            .joinedload(models.Section.course),
        joinedload(models.Enrollment.section)
            .joinedload(models.Section.teacher),
        joinedload(models.Enrollment.section)
            .selectinload(models.Section.schedules)
            .joinedload(models.ExamSchedule.room),
        joinedload(models.Enrollment.student),
    ).order_by(models.Enrollment.id.desc()).all()


def _serialize_schedule_status(schedule: models.ExamSchedule | None) -> str:
    if not schedule or not schedule.status:
        return "not_scheduled"
    return getattr(schedule.status, "value", str(schedule.status))


def _is_schedule_for_active_period(
    schedule: models.ExamSchedule,
    active_period: models.ExamPeriod | None,
) -> bool:
    if not active_period:
        return True

    schedule_exam_type = getattr(schedule.exam_type, "value", schedule.exam_type)
    return schedule_exam_type == active_period.exam_type


def _serialize_exam_rows(records, active_period: models.ExamPeriod | None):
    results = []
    seen_sections: set[int] = set()

    for record in records:
        sec = record.section
        if not sec or sec.id in seen_sections:
            continue

        seen_sections.add(sec.id)
        course = sec.course
        teacher = sec.teacher
        schedules = [
            schedule
            for schedule in (sec.schedules or [])
            if _is_schedule_for_active_period(schedule, active_period)
        ]
        schedules.sort(key=lambda item: (item.exam_date is None, item.exam_date or "9999-12-31", item.exam_time or ""))

        if not schedules:
            schedules = [None]

        for schedule in schedules:
            results.append({
                "course_id": course.course_id if course else "-",
                "course_name": (course.course_name_th or course.course_name_en) if course else "-",
                "section_no": sec.section_no,
                "teacher": teacher.full_name if teacher and teacher.full_name else "-",
                "exam_date": str(schedule.exam_date) if schedule and schedule.exam_date else None,
                "exam_time": schedule.exam_time if schedule else None,
                "room": schedule.room.room_name if schedule and schedule.room else None,
                "seat_group": sec.co_group_id,
                "status": _serialize_schedule_status(schedule),
                "has_schedule": schedule is not None,
            })

    results.sort(
        key=lambda item: (
            item["exam_date"] is None,
            item["exam_date"] or "9999-12-31",
            item["exam_time"] or "",
            item["course_id"],
            item["section_no"],
        )
    )
    return results


@router.get("/schedule/student/{student_id}")
def student_schedule(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    นักศึกษาค้นหาตารางสอบ (ต้อง login)

    Access Control (Strict Ownership):
    - Admin/Esq/Secretary: ดูตารางสอบของนักศึกษาคนใดก็ได้
    - Staff: ช่วยนักศึกษา (ดูตารางสอบได้)
    - Student: เฉพาะตารางสอบของตัวเอง (username == student_id)
    - Others: ปฏิเสธ

    Note: Temporary mapping uses username as student_id (common university pattern).
    TODO: Add student_id field to User model for permanent solution.
    """
    from auth_utils import get_effective_role

    normalized_student_id = student_id.strip()
    effective_role = get_effective_role(current_user)

    # ─── Access Control ───────────────────────────────────────
    # Allowed roles that can view any student schedule
    privileged_roles = (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
        models.UserRole.staff,  # Staff can help students
    )

    if effective_role not in privileged_roles:
        if effective_role == models.UserRole.student:
            # Student: Enforce strict ownership using username as temporary mapping
            # Most universities use student ID as username (e.g., "6200001234")
            if current_user.username != normalized_student_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"นักศึกษาสามารถดูตารางสอบของตัวเองเท่านั้น"
                )
        else:
            # Deny other roles (teacher, print_shop, etc.)
            raise HTTPException(
                status_code=403,
                detail="ไม่มีสิทธิ์เข้าถึงข้อมูลนี้"
            )

    # ─── Load schedule data (same as before) ───────────────────
    active_period = _get_active_period(db)
    enrollment_records = _load_enrollment_records(db, normalized_student_id, active_period)
    schedule_period = active_period if enrollment_records else None

    if not enrollment_records and active_period:
        enrollment_records = _load_enrollment_records(db, normalized_student_id, None)

    legacy_student = db.query(models.Student).filter(
        models.Student.student_id == normalized_student_id
    ).first()
    legacy_enrollments = []

    if not enrollment_records:
        legacy_enrollments = _load_legacy_enrollments(db, normalized_student_id, active_period)
        if legacy_enrollments:
            schedule_period = active_period
        if not legacy_enrollments and active_period:
            legacy_enrollments = _load_legacy_enrollments(db, normalized_student_id, None)
            schedule_period = None

    if not legacy_student and not enrollment_records and not legacy_enrollments:
        raise HTTPException(status_code=404, detail="Student ID was not found in the current exam records.")

    profile_source = enrollment_records[0] if enrollment_records else None
    legacy_profile = legacy_enrollments[0].student if legacy_enrollments else None
    exam_rows = _serialize_exam_rows(enrollment_records or legacy_enrollments, schedule_period)

    return {
        "student_id": normalized_student_id,
        "full_name": (
            legacy_student.full_name if legacy_student and legacy_student.full_name
            else legacy_profile.full_name if legacy_profile and legacy_profile.full_name
            else profile_source.student_name if profile_source and profile_source.student_name
            else normalized_student_id
        ),
        "major": (
            legacy_student.major if legacy_student and legacy_student.major
            else profile_source.major if profile_source and profile_source.major
            else None
        ),
        "faculty": (
            legacy_student.faculty if legacy_student and legacy_student.faculty
            else profile_source.faculty_name if profile_source and profile_source.faculty_name
            else None
        ),
        "term_label": (
            active_period.label if active_period and active_period.label
            else f"{active_period.exam_type} {active_period.semester}/{active_period.academic_year}" if active_period
            else None
        ),
        "total_courses": len({(row["course_id"], row["section_no"]) for row in exam_rows}),
        "exams": exam_rows,
    }


# ── GET /api/schedule/stats (public) ─────────────────────────
@router.get("/schedule/stats")
def schedule_stats(db: Session = Depends(get_db)):
    """สถิติสาธารณะสำหรับ landing page"""
    from sqlalchemy import func, distinct
    from models import ExamSchedule, Section, ExamPeriod

    p = db.query(ExamPeriod).filter(ExamPeriod.is_active == True).first()
    if not p:
        return {"total_schedules": 0, "total_students": 0,
                "total_rooms": 0, "exam_days": 0}

    scheds = db.query(ExamSchedule).join(Section).filter(
        Section.semester      == p.semester,
        Section.academic_year == p.academic_year,
    )
    total_scheds   = scheds.count()
    total_students = db.query(func.sum(Section.num_students)).join(ExamSchedule).filter(
        Section.semester      == p.semester,
        Section.academic_year == p.academic_year,
    ).scalar() or 0
    total_rooms = db.query(func.count(distinct(ExamSchedule.room_id))).join(Section).filter(
        Section.semester      == p.semester,
        Section.academic_year == p.academic_year,
        ExamSchedule.room_id.isnot(None),
    ).scalar() or 0
    exam_days = db.query(func.count(distinct(ExamSchedule.exam_date))).join(Section).filter(
        Section.semester      == p.semester,
        Section.academic_year == p.academic_year,
        ExamSchedule.exam_date.isnot(None),
    ).scalar() or 0

    return {
        "total_schedules": total_scheds,
        "total_students":  int(total_students),
        "total_rooms":     total_rooms,
        "exam_days":       exam_days,
    }


# ── GET /api/schedule/upcoming (public) ──────────────────────
@router.get("/schedule/upcoming")
def upcoming_schedules(
    limit: int = 12,
    db: Session = Depends(get_db),
):
    """ตารางสอบที่กำลังจะมาถึง (public)"""
    import datetime
    from models import ExamSchedule, Section, Course, Room
    from sqlalchemy.orm import joinedload

    today = datetime.date.today()
    scheds = db.query(ExamSchedule).options(
        joinedload(ExamSchedule.section).joinedload(Section.course),
        joinedload(ExamSchedule.room),
    ).filter(
        ExamSchedule.exam_date >= today,
    ).order_by(ExamSchedule.exam_date, ExamSchedule.exam_time).limit(limit).all()

    return [
        {
            "id":          s.id,
            "exam_date":   str(s.exam_date) if s.exam_date else None,
            "exam_time":   s.exam_time,
            "course_id":   s.section.course.course_id    if s.section and s.section.course else None,
            "course_name": s.section.course.course_name_th if s.section and s.section.course else None,
            "section_no":  s.section.section_no if s.section else None,
            "room_name":   s.room.room_name     if s.room   else None,
            "num_students":s.section.num_students if s.section else 0,
        }
        for s in scheds
    ]


@router.get("/schedule/{student_id}", include_in_schema=False)
def student_schedule_legacy(student_id: str, db: Session = Depends(get_db)):
    # Backward-compatible path for older clients.
    return student_schedule(student_id, db)


# ── GET /api/public/timeline ──────────────────────────────────
@router.get("/timeline")
def get_timeline(db: Session = Depends(get_db)):
    """
    Timeline สำหรับ landing page — ไม่ต้อง login
    แสดงขั้นตอน semester + สถานะปัจจุบัน + pending counts
    """
    from sqlalchemy import func
    import datetime

    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()

    if not p:
        return {"period": None, "steps": [], "current_step": -1}

    # นับ stats สำหรับแต่ละ step
    total_sections = db.query(models.Section).filter(
        models.Section.semester      == p.semester,
        models.Section.academic_year == p.academic_year,
    ).count()

    assigned_managers = db.query(models.SectionExamManager).join(
        models.Section,
        models.SectionExamManager.section_id == models.Section.id
    ).filter(
        models.Section.semester      == p.semester,
        models.Section.academic_year == p.academic_year,
        models.SectionExamManager.confirmed == True,
    ).count()

    submitted = db.query(models.ExamSubmission).join(
        models.Section,
        models.ExamSubmission.section_id == models.Section.id
    ).filter(
        models.Section.semester      == p.semester,
        models.Section.academic_year == p.academic_year,
        models.ExamSubmission.exam_format_confirmed == True,
    ).count()

    optimized = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()

    approved_subs = db.query(models.ExamSubmission).join(
        models.Section,
        models.ExamSubmission.section_id == models.Section.id
    ).filter(
        models.Section.semester      == p.semester,
        models.Section.academic_year == p.academic_year,
        models.ExamSubmission.status.in_(["approved","released"]),
    ).count()

    workflow_session = db.query(models.OptimizeSession).filter(
        models.OptimizeSession.exam_period_id == p.id
    ).first()
    sig1_done = bool(workflow_session and workflow_session.sig1_at)
    confirmed = bool(workflow_session and workflow_session.sig4_at)
    locked    = bool(workflow_session and workflow_session.status == "locked")

    # หาวันสอบแรก-สุดท้าย
    date_range = db.query(
        func.min(models.ExamSchedule.exam_date),
        func.max(models.ExamSchedule.exam_date),
    ).join(models.Section).filter(
        models.Section.semester      == p.semester,
        models.Section.academic_year == p.academic_year,
    ).first()

    today = datetime.date.today()

    # determine current step
    exam_started = date_range[0] and date_range[0] <= today
    exam_ended   = date_range[1] and date_range[1] < today

    if exam_ended:
        current_step = 6
    elif exam_started:
        current_step = 5
    elif locked:
        current_step = 4
    elif confirmed:
        current_step = 4
    elif sig1_done:
        current_step = 3
    elif optimized:
        current_step = 2
    elif submitted > 0:
        current_step = 1
    else:
        current_step = 0

    steps = [
        {
            "id": 0, "icon": "📥", "label": "นำเข้าข้อมูล",
            "desc": "Import รายวิชา + นักศึกษา",
            "detail": f"วิชาทั้งหมด {total_sections} รายวิชา",
            "role": "admin",
            "done": total_sections > 0,
        },
        {
            "id": 1, "icon": "📋", "label": "กำหนดผู้รับผิดชอบ",
            "desc": "อาจารย์กรอกรูปแบบสอบ",
            "detail": f"{submitted}/{total_sections} วิชากรอกแล้ว",
            "role": "teacher",
            "done": submitted >= total_sections and total_sections > 0,
            "progress": round(submitted/total_sections*100) if total_sections else 0,
        },
        {
            "id": 2, "icon": "🎯", "label": "จัดตารางสอบ",
            "desc": "Optimize ห้อง + กรรมการ",
            "detail": "Admin จัดตารางสอบ",
            "role": "admin",
            "done": bool(optimized),
        },
        {
            "id": 3, "icon": "✍️", "label": "ลงนามอนุมัติ",
            "desc": "4 ลายเซ็น R1 + อัปโหลดข้อสอบ",
            "detail": f"ข้อสอบ {approved_subs}/{total_sections} วิชาอนุมัติแล้ว",
            "role": "admin",
            "done": confirmed,
            "progress": round(approved_subs/total_sections*100) if total_sections else 0,
        },
        {
            "id": 4, "icon": "🖨️", "label": "พิมพ์ข้อสอบ",
            "desc": "ส่งร้านถ่าย",
            "detail": "ร้านถ่ายรับไฟล์แล้ว",
            "role": "admin",
            "done": locked,
        },
        {
            "id": 5, "icon": "📝", "label": "วันสอบ",
            "desc": "คุมสอบ + Check-in",
            "detail": f"{str(date_range[0]) if date_range[0] else '?'} — {str(date_range[1]) if date_range[1] else '?'}",
            "role": "all",
            "done": exam_ended,
            "active": exam_started and not exam_ended,
        },
        {
            "id": 6, "icon": "✅", "label": "เสร็จสิ้น",
            "desc": "สรุปผล",
            "detail": f"ภาค {p.semester}/{p.academic_year}",
            "role": "admin",
            "done": exam_ended,
        },
    ]

    return {
        "period": {
            "semester":      p.semester,
            "academic_year": p.academic_year,
            "label":         p.label or f"ภาค {p.semester}/{p.academic_year}",
            "exam_start":    str(date_range[0]) if date_range[0] else None,
            "exam_end":      str(date_range[1]) if date_range[1] else None,
        },
        "current_step":  current_step,
        "steps":         steps,
        "stats": {
            "total_sections":    total_sections,
            "assigned_managers": assigned_managers,
            "submitted":         submitted,
            "approved":          approved_subs,
            "optimized":         bool(optimized),
            "confirmed":         confirmed,
            "locked":            locked,
        },
    }
