"""
Public Router — ไม่ต้อง login
นักศึกษาค้นหาตารางสอบด้วยรหัสนักศึกษา
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models

router = APIRouter()


@router.get("/schedule/{student_id}")
def student_schedule(student_id: str, db: Session = Depends(get_db)):
    """
    นักศึกษาพิมพ์รหัสนักศึกษา → ได้ตารางสอบทุกวิชาที่ลงทะเบียน
    ไม่ต้อง login
    """
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id.strip()
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="ไม่พบรหัสนักศึกษานี้ในระบบ")

    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id
    ).options(
        joinedload(models.Enrollment.section)
            .joinedload(models.Section.course),
        joinedload(models.Enrollment.section)
            .joinedload(models.Section.teacher),
        joinedload(models.Enrollment.section)
            .joinedload(models.Section.schedules)
            .joinedload(models.ExamSchedule.room),
    ).all()

    results = []
    for enroll in enrollments:
        sec = enroll.section
        if not sec:
            continue
        course  = sec.course
        teacher = sec.teacher
        sch     = sec.schedules[0] if sec.schedules else None

        results.append({
            "course_id":      course.course_id if course else "—",
            "course_name":    course.course_name_th if course else "—",
            "section_no":     sec.section_no,
            "num_students":   sec.num_students,
            "teacher":        teacher.full_name if teacher else "—",
            "exam_date":      sch.exam_date if sch else None,
            "exam_time":      sch.exam_time if sch else None,
            "room":           sch.room.room_name if sch and sch.room else "—",
            "status":         sch.status if sch else "ยังไม่กำหนด",
            "has_schedule":   sch is not None,
        })

    # เรียงตามวันสอบ
    results.sort(key=lambda x: (x["exam_date"] or "9999", x["exam_time"] or ""))

    return {
        "student_id": student.student_id,
        "full_name":  student.full_name,
        "major":      student.major,
        "faculty":    student.faculty,
        "total_courses": len(results),
        "exams": results,
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

