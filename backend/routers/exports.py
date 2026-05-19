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
from utils.error_response import error_detail
from config.audit_actions import (
    EXPORT_PAPER_DISTRIBUTION_PDF,
    EXPORT_SCHEDULE_PDF,
    EXPORT_WORKLOAD_SUMMARY_PDF,
)
from config.periods import resolve_export_period
from staff_workloads import get_period_workload_snapshot
from services.export_service import ExportService
from validators.export_validator import ExportValidator
from policies.export_policy import ExportPolicy
import io

router = APIRouter()

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
    return ""


def _build_pdf_response(buf, filename: str) -> StreamingResponse:
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/schedule")
def export_schedule_pdf(
    semester: str = Query("2"),
    academic_year: str = Query("2568"),
    exam_type: str = Query("final"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_view_all),
    request: Request = None
):
    ExportValidator.validate_exam_type(exam_type)
    ExportValidator.validate_semester(semester)
    ExportPolicy.require_export_permission(current_user, "schedule")

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import os

        font_name = "Helvetica"
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

        schedules = ExportService.get_schedule_export_data(db, semester, academic_year, exam_type)
        if not schedules:
            raise HTTPException(404, error_detail("ไม่พบข้อมูลตารางสอบ", "errors.exports.periodNotFound"))

        from collections import defaultdict
        by_date = defaultdict(lambda: defaultdict(list))
        for s in schedules:
            by_date[s.exam_date][s.exam_time].append(s)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title", fontName=font_name, fontSize=14, alignment=TA_CENTER, spaceAfter=4)
        sub_style = ParagraphStyle("Sub", fontName=font_name, fontSize=11, alignment=TA_CENTER, spaceAfter=2)
        cell_style = ParagraphStyle("Cell", fontName=font_name, fontSize=8, leading=10, wordWrap="CJK")
        day_style = ParagraphStyle("Day", fontName=font_name, fontSize=10, spaceAfter=2, spaceBefore=8)

        elements = []
        exam_type_th = "ปลายภาค" if exam_type == "final" else "กลางภาค"
        elements.append(Paragraph(f"ตารางสอบ{exam_type_th} ระดับปริญญาตรี-โท ประจำภาคการศึกษาที่ {semester} ปีการศึกษา {academic_year}", title_style))
        elements.append(Paragraph("คณะรัฐศาสตร์และรัฐประศาสนศาสตร์", sub_style))
        elements.append(Spacer(1, 4*mm))

        col_widths = [3.5*cm, 3*cm, 4*cm, 1.8*cm, 3*cm, 5*cm, 3*cm]
        header_row = [Paragraph("<b>วัน/เวลาสอบ</b>", cell_style), Paragraph("<b>กระบวนวิชา</b>", cell_style), Paragraph("<b>อาจารย์ผู้สอน</b>", cell_style), Paragraph("<b>จำนวน นศ.</b>", cell_style), Paragraph("<b>ห้อง</b>", cell_style), Paragraph("<b>กรรมการคุมสอบ</b>", cell_style), Paragraph("<b>กรรมการจ่ายข้อสอบ</b>", cell_style)]
        all_rows = [header_row]
        row_styles = []
        current_row = 1

        for date_key in sorted(by_date.keys()):
            day_name, day_num, month_name, year = parse_date_th(date_key)
            date_label = f"{day_name} {day_num} {month_name} {year}"
            date_header = [Paragraph(f"<b>{date_label}</b>", cell_style), "", "", "", "", "", ""]
            all_rows.append(date_header)
            row_styles.append(("BACKGROUND", (0, current_row), (-1, current_row), colors.HexColor("#E8E8E8")))
            row_styles.append(("SPAN", (0, current_row), (-1, current_row)))
            current_row += 1

            for time_key in sorted(by_date[date_key].keys()):
                time_label = time_key + " น."
                time_scheds = by_date[date_key][time_key]
                first = True

                for sch in time_scheds:
                    sec = sch.section
                    course = sec.course if sec else None
                    teacher = sec.teacher if sec else None
                    room = sch.room

                    course_id = course.course_id if course else "—"
                    section_no = sec.section_no if sec else "—"
                    course_str = f"{course_id} Sec {section_no}"
                    teacher_str = teacher.full_name if teacher else (sch.paper_distributor or "—")
                    students_n = sec.num_students if sec else 0
                    room_str = room.room_name if room else "—"
                    sups_str = get_supervisions_str(sch.supervisions or [])
                    dist_str = sch.paper_distributor or get_distributor_str(sch.supervisions or []) or "—"

                    row = [Paragraph(time_label if first else "", cell_style), Paragraph(course_str, cell_style), Paragraph(teacher_str, cell_style), Paragraph(str(students_n), cell_style), Paragraph(room_str, cell_style), Paragraph(sups_str, cell_style), Paragraph(dist_str, cell_style)]
                    all_rows.append(row)
                    if hasattr(sch, 'is_swapped') and sch.is_swapped:
                        row_styles.append(("TEXTCOLOR", (0, current_row), (-1, current_row), colors.HexColor("#AAAAAA")))
                    current_row += 1
                    first = False

        table = Table(all_rows, colWidths=col_widths, repeatRows=1)
        base_style = [("FONTNAME", (0,0), (-1,-1), font_name), ("FONTSIZE", (0,0), (-1,-1), 8), ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a2d52")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTSIZE", (0,0), (-1,0), 9), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]), ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING",(0,0),(-1,-1), 3), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING",(0,0), (-1,-1), 4)]
        table.setStyle(TableStyle(base_style + row_styles))
        elements.append(table)
        doc.build(elements)

        filename = ExportService.generate_schedule_filename(semester, academic_year, exam_type)
        try:
            log_action(db, current_user, EXPORT_SCHEDULE_PDF, table_name="exam_schedules", new_values={"file_type": "pdf", "export_scope": "schedule", "row_count": len(schedules), "semester": semester, "academic_year": academic_year, "exam_type": exam_type}, request=request, http_status=200)
        except Exception:
            pass
        return _build_pdf_response(buf, filename)
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
    snapshot = ExportService.get_workload_export_data(db, period)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    rows = [["Staff", "Department", "Invigilation", "Paper Distribution", "External Exam", "Current Total", "Historical Total"]]
    for row in snapshot["summary"]:
        rows.append([row["staff_name"], row["department"], str(row["invigilation_count"]), str(row["paper_distribution_count"]), str(row["external_exam_count"]), str(row["total_workload"]), str(row["historical_total_workload"])])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2d52")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])]))
    doc.build([Paragraph(f"EMS Staff Workload Summary - {period.label}", styles["Title"]), Paragraph(f"Generated for {current_user.full_name or current_user.username}", styles["Normal"]), Spacer(1, 12), table])
    buffer.seek(0)
    try:
        log_action(db, current_user, EXPORT_WORKLOAD_SUMMARY_PDF, table_name="staffworkloads", new_values={"file_type": "pdf", "export_scope": "period", "row_count": len(snapshot["summary"]), "semester": period.semester, "academic_year": period.academic_year, "exam_type": period.exam_type}, http_status=200, request=request)
    except Exception:
        pass
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="EMS_workload_summary_{period.semester}_{period.academic_year}_{period.exam_type}.pdf"'})