"""
PDF Export Router
สร้างตารางสอบ PDF ตามรูปแบบไฟล์จริง (ตารางสอบปลายภาค)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models
from auth_utils import get_current_user, require_admin, require_staff_or_admin, require_view_all, log_action, get_effective_role
from config.audit_actions import (
    EXPORT_PAPER_DISTRIBUTION_PDF,
    EXPORT_SCHEDULE_PDF,
    EXPORT_WORKLOAD_SUMMARY_PDF,
)
from config.periods import resolve_export_period
from staff_workloads import get_period_workload_snapshot
import io

router = APIRouter()

# Thai day/month names
THAI_DAYS = ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"]
THAI_MONTHS = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
               "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
DAY_NAMES_TH = {
    "Monday":"วันจันทร์ที่","Tuesday":"วันอังคารที่",
    "Wednesday":"วันพุธที่","Thursday":"วันพฤหัสบดีที่",
    "Friday":"วันศุกร์ที่","Saturday":"วันเสาร์ที่","Sunday":"วันอาทิตย์ที่"
}


def parse_date_th(date_str: str) -> tuple:
    """'2569-03-23' → ('วันอาทิตย์ที่', '23', 'มีนาคม', '2569')"""
    if not date_str:
        return ("","","","")
    try:
        from datetime import date
        parts = date_str.split("-")
        year_be = int(parts[0])
        month   = int(parts[1])
        day     = int(parts[2])
        year_ce = year_be - 543
        d = date(year_ce, month, day)
        day_name = DAY_NAMES_TH.get(d.strftime("%A"), "")
        return (day_name, str(day), THAI_MONTHS[month], str(year_be))
    except Exception:
        return ("", date_str, "", "")


def get_supervisions_str(supervisions, role="supervisor") -> str:
    names = []
    for s in sorted(supervisions, key=lambda x: x.slot_order):
        if s.user and s.user.full_name:
            names.append(s.user.full_name)
    return " – ".join(names) if names else "—"


def get_distributor_str(supervisions) -> str:
    for s in supervisions:
        if s.role_in_exam == "distributor" and s.user:
            return s.user.full_name
    # fallback: paper_distributor field on schedule
    return ""


@router.get("/schedule")
def export_schedule_pdf(
    semester: str = Query("2"),
    academic_year: str = Query("2568"),
    exam_type: str = Query("final"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_view_all),
    request: Request = None
):
    """Export ตารางสอบเป็น PDF ตามรูปแบบเอกสารจริง"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import os

        # ลอง register Thai font
        font_name = "Helvetica"  # fallback
        thai_font_paths = [
            "/usr/share/fonts/truetype/tlwg/THSarabunNew.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        ]
        for fp in thai_font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont("ThaiFont", fp))
                    font_name = "ThaiFont"
                    break
                except Exception:
                    pass

        # ดึงข้อมูล schedules
        schedules = db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.section)
                .joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section)
                .joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions)
                .joinedload(models.Supervision.user),
        ).join(models.Section).filter(
            models.Section.semester == semester,
            models.Section.academic_year == academic_year,
        ).order_by(
            models.ExamSchedule.exam_date,
            models.ExamSchedule.exam_time,
        ).all()

        if not schedules:
            raise HTTPException(404, "ไม่พบข้อมูลตารางสอบ")

        # จัดกลุ่มตามวันที่ + เวลา
        from collections import defaultdict
        by_date = defaultdict(lambda: defaultdict(list))
        for s in schedules:
            by_date[s.exam_date][s.exam_time].append(s)

        # สร้าง PDF
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4),
            rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", fontName=font_name, fontSize=14,
            alignment=TA_CENTER, spaceAfter=4
        )
        sub_style = ParagraphStyle(
            "Sub", fontName=font_name, fontSize=11,
            alignment=TA_CENTER, spaceAfter=2
        )
        cell_style = ParagraphStyle(
            "Cell", fontName=font_name, fontSize=8,
            leading=10, wordWrap="CJK"
        )
        day_style = ParagraphStyle(
            "Day", fontName=font_name, fontSize=10,
            spaceAfter=2, spaceBefore=8
        )

        elements = []

        # Header
        exam_type_th = "ปลายภาค" if exam_type == "final" else "กลางภาค"
        elements.append(Paragraph(
            f"ตารางสอบ{exam_type_th} ระดับปริญญาตรี-โท ประจำภาคการศึกษาที่ {semester} ปีการศึกษา {academic_year}",
            title_style
        ))
        elements.append(Paragraph("คณะรัฐศาสตร์และรัฐประศาสนศาสตร์", sub_style))
        elements.append(Spacer(1, 4*mm))

        # Table columns: วัน/เวลา | กระบวนวิชา | อาจารย์ | จำนวน | ห้อง | กรรมการคุมสอบ | กรรมการจ่าย
        col_widths = [3.5*cm, 3*cm, 4*cm, 1.8*cm, 3*cm, 5*cm, 3*cm]

        header_row = [
            Paragraph("<b>วัน/เวลาสอบ</b>", cell_style),
            Paragraph("<b>กระบวนวิชา</b>", cell_style),
            Paragraph("<b>อาจารย์ผู้สอน</b>", cell_style),
            Paragraph("<b>จำนวน นศ.</b>", cell_style),
            Paragraph("<b>ห้อง</b>", cell_style),
            Paragraph("<b>กรรมการคุมสอบ</b>", cell_style),
            Paragraph("<b>กรรมการจ่ายข้อสอบ</b>", cell_style),
        ]

        all_rows = [header_row]
        row_styles = []
        current_row = 1

        for date_key in sorted(by_date.keys()):
            day_name, day_num, month_name, year = parse_date_th(date_key)
            date_label = f"{day_name} {day_num} {month_name} {year}"
            date_header = [
                Paragraph(f"<b>{date_label}</b>", cell_style),
                "", "", "", "", "", ""
            ]
            all_rows.append(date_header)
            row_styles.append(("BACKGROUND", (0, current_row), (-1, current_row), colors.HexColor("#E8E8E8")))
            row_styles.append(("SPAN", (0, current_row), (-1, current_row)))
            current_row += 1

            for time_key in sorted(by_date[date_key].keys()):
                time_label = time_key + " น."
                time_scheds = by_date[date_key][time_key]
                first = True

                for sch in time_scheds:
                    sec  = sch.section
                    course = sec.course if sec else None
                    teacher = sec.teacher if sec else None
                    room = sch.room

                    course_id  = course.course_id if course else "—"
                    section_no = sec.section_no if sec else "—"
                    course_str = f"{course_id} Sec {section_no}"
                    teacher_str = teacher.full_name if teacher else (sch.paper_distributor or "—")
                    students_n = sec.num_students if sec else 0
                    room_str   = room.room_name if room else "—"
                    sups_str   = get_supervisions_str(sch.supervisions or [])
                    dist_str   = (sch.paper_distributor or
                                  get_distributor_str(sch.supervisions or []) or "—")

                    row = [
                        Paragraph(time_label if first else "", cell_style),
                        Paragraph(course_str, cell_style),
                        Paragraph(teacher_str, cell_style),
                        Paragraph(str(students_n), cell_style),
                        Paragraph(room_str, cell_style),
                        Paragraph(sups_str, cell_style),
                        Paragraph(dist_str, cell_style),
                    ]
                    all_rows.append(row)

                    if sch.is_swapped if hasattr(sch, 'is_swapped') else False:
                        row_styles.append(("TEXTCOLOR", (0, current_row), (-1, current_row),
                                           colors.HexColor("#AAAAAA")))

                    current_row += 1
                    first = False

        table = Table(all_rows, colWidths=col_widths, repeatRows=1)
        base_style = [
            ("FONTNAME",    (0,0), (-1,-1), font_name),
            ("FONTSIZE",    (0,0), (-1,-1), 8),
            ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ("VALIGN",      (0,0), (-1,-1), "TOP"),
            ("BACKGROUND",  (0,0), (-1,0),  colors.HexColor("#1a2d52")),
            ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
            ("FONTSIZE",    (0,0), (-1,0),  9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
            ("TOPPADDING",  (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0),(-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING",(0,0), (-1,-1), 4),
        ]
        table.setStyle(TableStyle(base_style + row_styles))
        elements.append(table)

        doc.build(elements)
        buf.seek(0)

        filename = f"exam_schedule_{semester}_{academic_year}_{exam_type}.pdf"

        # Log export action
        try:
            log_action(
                db=db,
                actor=current_user,
                action=EXPORT_SCHEDULE_PDF,
                table_name="exam_schedules",
                new_values={
                    "file_type": "pdf",
                    "export_scope": "schedule",
                    "row_count": len(schedules),
                    "semester": semester,
                    "academic_year": academic_year,
                    "exam_type": exam_type,
                },
                request=request,
                http_status=200
            )
        except Exception as e:
            # Don't block export if logging fails
            import sys
            print(f"Warning: Export logging failed: {e}", file=sys.stderr)

        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except ImportError:
        raise HTTPException(500, "กรุณาติดตั้ง reportlab: pip install reportlab")


@router.get("/workload-summary-pdf")
def export_workload_summary_pdf(
    semester: str = Query(None),
    academic_year: str = Query(None),
    exam_type: str = Query("final"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
    request: Request = None,
):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        raise HTTPException(500, "กรุณาติดตั้ง reportlab: pip install reportlab")

    period = resolve_export_period(db, semester, academic_year, exam_type)
    snapshot = get_period_workload_snapshot(db, period)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    rows = [["Staff", "Department", "Invigilation", "Paper Distribution", "External Exam", "Current Total", "Historical Total"]]
    for row in snapshot["summary"]:
        rows.append([
            row["staff_name"],
            row["department"],
            str(row["invigilation_count"]),
            str(row["paper_distribution_count"]),
            str(row["external_exam_count"]),
            str(row["total_workload"]),
            str(row["historical_total_workload"]),
        ])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2d52")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    doc.build([
        Paragraph(f"EMS Staff Workload Summary - {period.label}", styles["Title"]),
        Paragraph(f"Generated for {current_user.full_name or current_user.username}", styles["Normal"]),
        Spacer(1, 12),
        table,
    ])
    buffer.seek(0)
    try:
        log_action(db, current_user, EXPORT_WORKLOAD_SUMMARY_PDF,
                   table_name="staffworkloads",
                   new_values={"file_type": "pdf", "export_scope": "period",
                               "row_count": len(snapshot["summary"]),
                               "semester": period.semester,
                               "academic_year": period.academic_year,
                               "exam_type": period.exam_type},
                   http_status=200, request=request)
    except Exception:
        pass
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"EMS_workload_summary_{period.semester}_{period.academic_year}_{period.exam_type}.pdf\"'},
    )


@router.get("/paper-distribution-pdf")
def export_paper_distribution_pdf(
    semester: str = Query(None),
    academic_year: str = Query(None),
    exam_type: str = Query("final"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
    request: Request = None,
):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        raise HTTPException(500, "กรุณาติดตั้ง reportlab: pip install reportlab")

    period = resolve_export_period(db, semester, academic_year, exam_type)
    assignments = db.query(models.PaperDistributionAssignment).options(
        joinedload(models.PaperDistributionAssignment.user)
    ).filter(
        models.PaperDistributionAssignment.exam_period_id == period.id
    ).order_by(
        models.PaperDistributionAssignment.exam_date,
        models.PaperDistributionAssignment.exam_time,
        models.PaperDistributionAssignment.slot_order,
    ).all()
    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
    ).join(models.Section).filter(
        models.Section.academic_year == period.academic_year,
        models.Section.semester == period.semester,
        models.ExamSchedule.exam_type == period.exam_type,
    ).all()
    context_by_slot: dict[tuple[str, str], dict[str, list[str]]] = {}
    for schedule in schedules:
        key = (str(schedule.exam_date) if schedule.exam_date else "", schedule.exam_time or "")
        context = context_by_slot.setdefault(key, {"courses": [], "rooms": []})
        if schedule.section and schedule.section.course:
            label = f"{schedule.section.course.course_id} Sec {schedule.section.section_no}"
            if label not in context["courses"]:
                context["courses"].append(label)
        if schedule.room and schedule.room.room_name not in context["rooms"]:
            context["rooms"].append(schedule.room.room_name)
    rows = [["Staff", "Department", "Date", "Time", "Covered Courses", "Covered Rooms", "Load"]]
    for assignment in assignments:
        context = context_by_slot.get((assignment.exam_date, assignment.exam_time), {"courses": [], "rooms": []})
        rows.append([
            assignment.user.full_name if assignment.user else f"User #{assignment.user_id}",
            (assignment.user.division or assignment.user.unit) if assignment.user else "",
            assignment.exam_date,
            assignment.exam_time,
            ", ".join(context["courses"]),
            ", ".join(context["rooms"]),
            str(assignment.workload_units or 1),
        ])
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2d52")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    doc.build([
        Paragraph(f"EMS Paper Distribution Assignments - {period.label}", styles["Title"]),
        Paragraph(f"Generated for {current_user.full_name or current_user.username}", styles["Normal"]),
        Spacer(1, 12),
        table,
    ])
    buffer.seek(0)
    try:
        log_action(db, current_user, EXPORT_PAPER_DISTRIBUTION_PDF,
                   table_name="paper_distribution_assignments",
                   new_values={"file_type": "pdf", "export_scope": "period",
                               "row_count": len(assignments),
                               "semester": period.semester,
                               "academic_year": period.academic_year,
                               "exam_type": period.exam_type},
                   http_status=200, request=request)
    except Exception:
        pass
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"EMS_paper_distribution_{period.semester}_{period.academic_year}_{period.exam_type}.pdf\"'},
    )


@router.get("/supervision-stats/{user_id}")
def get_supervision_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """สถิติการคุมสอบ — baseline (ก่อน swap) vs actual"""
    if current_user.id != user_id and current_user.role != models.UserRole.admin:
        raise HTTPException(403, "ไม่มีสิทธิ์ดูสถิติของคนอื่น")

    # Baseline (original assignment)
    baselines = db.query(models.SupervisionBaseline).options(
        joinedload(models.SupervisionBaseline.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.SupervisionBaseline.schedule)
            .joinedload(models.ExamSchedule.room),
    ).filter(models.SupervisionBaseline.user_id == user_id).all()

    # Actual current
    actuals = db.query(models.Supervision).options(
        joinedload(models.Supervision.schedule)
            .joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
    ).filter(models.Supervision.user_id == user_id).all()

    baseline_count = len(baselines)
    actual_count   = len(actuals)
    swapped_count  = sum(1 for s in actuals if s.is_swapped)

    return {
        "user_id": user_id,
        "baseline_count": baseline_count,
        "actual_count":   actual_count,
        "swapped_out":    baseline_count - actual_count + swapped_count,
        "swapped_in":     swapped_count,
        "baseline_sessions": [
            {
                "date": b.schedule.exam_date if b.schedule else None,
                "time": b.schedule.exam_time if b.schedule else None,
                "course": (b.schedule.section.course.course_id
                           if b.schedule and b.schedule.section
                           and b.schedule.section.course else None),
                "room": (b.schedule.room.room_name
                         if b.schedule and b.schedule.room else None),
                "slot_order": b.slot_order,
            }
            for b in baselines
        ],
        "actual_sessions": [
            {
                "id": s.id,
                "date": s.schedule.exam_date if s.schedule else None,
                "time": s.schedule.exam_time if s.schedule else None,
                "course": (s.schedule.section.course.course_id
                           if s.schedule and s.schedule.section
                           and s.schedule.section.course else None),
                "is_swapped": s.is_swapped,
                "is_emergency": s.is_emergency_sub,
                "slot_order": s.slot_order,
            }
            for s in actuals
        ],
    }


# ── GET /api/exports/audit-logs ───────────────────────────────
@router.get("/audit-logs")
def get_audit_logs(
    table_name:   str = None,
    record_id:    int = None,
    actor_id:     int = None,
    action:       str = None,
    from_date:    str = None,
    to_date:      str = None,
    request_id:   str = None,
    page:         int = 1,
    limit:        int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Query audit logs with filters — สำหรับ admin trace ปัญหา
    ตัวอย่าง:
      /audit-logs?table_name=exam_submissions&record_id=42
      /audit-logs?action=EXAM_APPROVE&from_date=2026-03-01
      /audit-logs?request_id=abc-123  ← trace request เดียวทุก log
    """
    if limit > 200: limit = 200
    q = db.query(models.AuditLog)
    if table_name:   q = q.filter(models.AuditLog.table_name == table_name)
    if record_id:    q = q.filter(models.AuditLog.record_id  == record_id)
    if actor_id:     q = q.filter(models.AuditLog.actor_id   == actor_id)
    if action:       q = q.filter(models.AuditLog.action.ilike(f"%{action}%"))
    if request_id:   q = q.filter(models.AuditLog.request_id == request_id)
    if from_date:
        from datetime import datetime, timezone
        q = q.filter(models.AuditLog.timestamp >= datetime.fromisoformat(from_date))
    if to_date:
        from datetime import datetime, timezone, timedelta
        q = q.filter(models.AuditLog.timestamp < datetime.fromisoformat(to_date) + timedelta(days=1))

    total = q.count()
    logs  = q.order_by(models.AuditLog.timestamp.desc())              .offset((page-1)*limit).limit(limit).all()

    return {
        "total":  total,
        "page":   page,
        "limit":  limit,
        "pages":  (total + limit - 1) // limit,
        "logs": [
            {
                "id":           l.id,
                "actor":        l.actor.full_name if l.actor else f"user#{l.actor_id}",
                "actor_id":     l.actor_id,
                "action":       l.action,
                "table_name":   l.table_name,
                "record_id":    l.record_id,
                "request_id":   l.request_id,
                "duration_ms":  l.duration_ms,
                "http_status":  l.http_status,
                "old_values":   l.old_values,
                "new_values":   l.new_values,
                "timestamp":    l.timestamp.isoformat() if l.timestamp else None,
            }
            for l in logs
        ]
    }


# ── GET /api/exports/import-report/{session_id} ──────────────
@router.get("/import-report/{session_id}")
def get_import_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """ดูรายงาน import session: imported/skipped/validation errors"""
    sess = db.query(models.ImportSession).filter(
        models.ImportSession.id == session_id
    ).first()
    if not sess:
        raise HTTPException(404, "ไม่พบ import session")

    records = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.import_session_id == session_id
    ).count()

    sections = db.query(models.Section).filter(
        models.Section.import_session_id == session_id
    ).count()

    return {
        "session_id":       session_id,
        "academic_year":    sess.academic_year,
        "semester":         sess.semester,
        "exam_type":        sess.exam_type,
        "opencourse_rows":  sess.opencourse_rows,
        "enrollment_rows":  sess.enrollment_rows,
        "sections_created": sections,
        "enrollment_records": records,
        "created_at":       sess.created_at.isoformat() if sess.created_at else None,
    }
