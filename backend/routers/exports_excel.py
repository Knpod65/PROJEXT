"""
exports_excel.py — Export Excel รายงาน

GET /api/exports/compensation          → Excel ค่าตอบแทนกรรมการ per period
GET /api/exports/schedule-excel        → Excel ตารางสอบ
GET /api/exports/submissions-excel     → Excel สถานะข้อสอบทุกวิชา
"""

import io, math
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date
from database import get_db
import models
from auth_utils import require_admin, require_staff_or_admin, get_current_user, require_view_all, log_action, get_effective_role
from staff_workloads import get_period_workload_snapshot

router = APIRouter()


def _resolve_period(db: Session, semester: str | None, academic_year: str | None, exam_type: str | None = "final") -> models.ExamPeriod:
    if semester and academic_year:
        period = db.query(models.ExamPeriod).filter(
            models.ExamPeriod.semester == semester,
            models.ExamPeriod.academic_year == academic_year,
            models.ExamPeriod.exam_type == exam_type,
        ).first()
        if period:
            return period
    period = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not period:
        raise HTTPException(400, "ไม่มี active period")
    return period


def _workbook_response(wb, filename: str) -> StreamingResponse:
    """Return openpyxl workbook as streaming Excel download"""
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _style_header(ws, row: int, cols: int,
                  fill_color="0F1B35", font_color="FFFFFF"):
    """Style header row"""
    try:
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        fill = PatternFill("solid", fgColor=fill_color)
        font = Font(bold=True, color=font_color, size=11)
        bd   = Border(
            bottom=Side(style="medium", color="C41230"),
        )
        for col in range(1, cols + 1):
            cell = ws.cell(row=row, column=col)
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = bd
    except ImportError:
        pass


def _auto_width(ws):
    """Auto-adjust column widths"""
    try:
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    val = str(cell.value or "")
                    max_len = max(max_len, len(val))
                except:
                    pass
            ws.column_dimensions[col_letter].width = min(max_len + 4, 40)
    except:
        pass


# ── GET /api/exports/compensation ────────────────────────────
@router.get("/compensation")
def export_compensation(
    semester:      str = None,
    academic_year: str = None,
    exam_type:     str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
    request: Request = None,
):
    """
    Excel ค่าตอบแทนกรรมการคุมสอบ
    - Sheet 1: รายบุคคล (ชื่อ, จำนวนครั้ง, ค่าตอบแทนรวม)
    - Sheet 2: รายวิชา (แต่ละวิชา กรรมการ ค่าตอบแทน)
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side, numbers
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise HTTPException(500, "openpyxl ไม่ได้ติดตั้ง — pip install openpyxl")

    # หา active period ถ้าไม่ระบุ
    if not semester or not academic_year:
        p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
        if p:
            semester      = semester      or p.semester
            academic_year = academic_year or p.academic_year

    # query supervisions
    sups = db.query(models.Supervision).options(
        joinedload(models.Supervision.user),
        joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.room),
    ).join(models.ExamSchedule).join(models.Section).filter(
        models.Section.semester      == semester,
        models.Section.academic_year == academic_year,
        models.ExamSchedule.exam_type == exam_type,
    ).all()

    # คำนวณค่าตอบแทนจาก settings
    settings = {s.key: s.value for s in db.query(models.SystemSetting).all()}
    rate_internal = float(settings.get("compensation_rate_internal", "200"))
    rate_external = float(settings.get("compensation_rate_external", "300"))

    wb = openpyxl.Workbook()

    # ══ Sheet 1: รายบุคคล ══════════════════════════════════════
    ws1 = wb.active
    ws1.title = "ค่าตอบแทนรายบุคคล"
    ws1.row_dimensions[1].height = 30

    headers1 = ["ลำดับ","รหัสพนักงาน","ชื่อ-สกุล","ตำแหน่ง","สังกัด",
                "จำนวนครั้งคุมสอบ","ค่าตอบแทน/ครั้ง (บาท)","รวม (บาท)"]
    for c, h in enumerate(headers1, 1):
        ws1.cell(1, c, h)
    _style_header(ws1, 1, len(headers1))

    # รวม per user
    user_data = {}
    for sup in sups:
        if not sup.user: continue
        uid = sup.user_id
        if uid not in user_data:
            user_data[uid] = {
                "user": sup.user, "count": 0,
                "rate": rate_internal,
                "total": 0.0,
            }
        user_data[uid]["count"] += 1
        rate = float(sup.compensation) if sup.compensation else rate_internal
        user_data[uid]["rate"]  = rate
        user_data[uid]["total"] += rate

    for i, (uid, d) in enumerate(sorted(user_data.items(), key=lambda x: x[1]["user"].full_name or ""), 1):
        u = d["user"]
        row = [i, u.employee_id or "", u.full_name or u.username,
               u.title or "", u.division or "",
               d["count"], d["rate"], d["total"]]
        ws1.append(row)
        # สีแถวสลับ
        if i % 2 == 0:
            for c in range(1, len(headers1) + 1):
                ws1.cell(i+1, c).fill = PatternFill("solid", fgColor="F8FAFC")
        # bold total column
        ws1.cell(i+1, 8).font = Font(bold=True)
        ws1.cell(i+1, 8).number_format = '#,##0.00'

    # Grand total row
    total_row = len(user_data) + 2
    ws1.cell(total_row, 6, sum(d["count"] for d in user_data.values()))
    ws1.cell(total_row, 8, sum(d["total"] for d in user_data.values()))
    ws1.cell(total_row, 6).font = Font(bold=True, color="C41230")
    ws1.cell(total_row, 8).font = Font(bold=True, color="C41230")
    ws1.cell(total_row, 8).number_format = '#,##0.00'
    ws1.cell(total_row, 5, "รวมทั้งสิ้น").font = Font(bold=True)

    _auto_width(ws1)

    # ══ Sheet 2: รายวิชา ═══════════════════════════════════════
    ws2 = wb.create_sheet("รายวิชา")
    headers2 = ["รหัสวิชา","ชื่อวิชา","ตอน","วันสอบ","เวลา","ห้อง",
                "จำนวน นศ.","กรรมการ 1","กรรมการ 2","กรรมการ 3","รวมค่าตอบแทน"]
    for c, h in enumerate(headers2, 1):
        ws2.cell(1, c, h)
    _style_header(ws2, 1, len(headers2))

    # group by schedule
    schedules = {}
    for sup in sups:
        sid = sup.schedule_id
        if sid not in schedules:
            schedules[sid] = {"sch": sup.schedule, "sups": []}
        schedules[sid]["sups"].append(sup)

    for i, (sid, d) in enumerate(sorted(
        schedules.items(),
        key=lambda x: (str(x[1]["sch"].exam_date or ""), x[1]["sch"].exam_time or "")
    ), 1):
        sch  = d["sch"]
        sec  = sch.section
        course = sec.course if sec else None
        room   = sch.room
        sups_sorted = sorted(d["sups"], key=lambda s: s.slot_order or 99)
        sup_names = [s.user.full_name if s.user else "" for s in sups_sorted[:3]]
        while len(sup_names) < 3: sup_names.append("")
        total_comp = sum(float(s.compensation or rate_internal) for s in d["sups"])
        row = [
            course.course_id    if course else "",
            course.course_name_th if course else "",
            sec.section_no      if sec    else "",
            str(sch.exam_date)  if sch.exam_date else "",
            sch.exam_time       or "",
            room.room_name      if room   else "",
            sec.num_students    if sec    else 0,
            sup_names[0], sup_names[1], sup_names[2],
            total_comp,
        ]
        ws2.append(row)
        ws2.cell(i+1, 11).number_format = '#,##0.00'
        if i % 2 == 0:
            for c in range(1, len(headers2)+1):
                ws2.cell(i+1, c).fill = PatternFill("solid", fgColor="F8FAFC")

    _auto_width(ws2)

    # ══ Sheet 3: สรุปรวม ════════════════════════════════════════
    ws3 = wb.create_sheet("สรุป")
    exam_type_th = "ปลายภาค" if exam_type == "final" else "กลางภาค"
    info = [
        ["รายงานค่าตอบแทนกรรมการคุมสอบ", ""],
        ["ภาคการศึกษา", f"{semester}/{academic_year}"],
        ["ประเภทสอบ", exam_type_th],
        ["วันที่ออกรายงาน", str(date.today())],
        ["", ""],
        ["จำนวนวิชาที่สอบ", len(schedules)],
        ["จำนวนกรรมการทั้งหมด", len(user_data)],
        ["จำนวนครั้งคุมสอบรวม", sum(d["count"] for d in user_data.values())],
        ["ค่าตอบแทนรวมทั้งสิ้น", sum(d["total"] for d in user_data.values())],
    ]
    for r, (k, v) in enumerate(info, 1):
        ws3.cell(r, 1, k).font = Font(bold=(r == 1 or r >= 6))
        ws3.cell(r, 2, v)
        if k == "ค่าตอบแทนรวมทั้งสิ้น":
            ws3.cell(r, 2).number_format = '#,##0.00'
            ws3.cell(r, 2).font = Font(bold=True, color="C41230", size=13)
    ws3.title = "สรุป"
    _auto_width(ws3)

    filename = f"EMS_compensation_{semester}_{academic_year}_{exam_type}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_compensation",
            table_name="supervisions",
            new_values={
                "file_type": "xlsx",
                "export_scope": "compensation",
                "row_count": len(schedules) if 'schedules' in locals() else 0,
                "semester": semester,
                "academic_year": academic_year,
                "exam_type": exam_type,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, filename)


# ── GET /api/exports/schedule-excel ──────────────────────────
@router.get("/schedule-excel")
def export_schedule_excel(
    semester:      str = None,
    academic_year: str = None,
    exam_type:     str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_view_all),
    request: Request = None,
):
    """Excel ตารางสอบ — sort by date + time"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        raise HTTPException(500, "ต้อง pip install openpyxl")

    if not semester or not academic_year:
        p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active==True).first()
        if p:
            semester = semester or p.semester
            academic_year = academic_year or p.academic_year

    scheds = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).join(models.Section).filter(
        models.Section.semester      == semester,
        models.Section.academic_year == academic_year,
        models.ExamSchedule.exam_type == exam_type,
    ).order_by(models.ExamSchedule.exam_date, models.ExamSchedule.exam_time).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ตารางสอบ"
    headers = ["วันที่","เวลา","รหัสวิชา","ชื่อวิชา","ตอน","ห้อง",
               "จำนวน นศ.","อาจารย์","กรรมการ 1","กรรมการ 2","กรรมการ 3","สถานะ"]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    _style_header(ws, 1, len(headers))

    for i, s in enumerate(scheds, 1):
        sec    = s.section
        course = sec.course  if sec else None
        room   = s.room
        teacher= sec.teacher if sec else None
        sups   = sorted(s.supervisions or [], key=lambda x: x.slot_order or 99)
        names  = [sv.user.full_name for sv in sups[:3] if sv.user]
        while len(names) < 3: names.append("")

        row = [
            str(s.exam_date)         if s.exam_date else "",
            s.exam_time              or "",
            course.course_id         if course  else "",
            course.course_name_th    if course  else "",
            sec.section_no           if sec     else "",
            room.room_name           if room    else "",
            sec.num_students         if sec     else 0,
            teacher.full_name        if teacher else "",
            names[0], names[1], names[2],
            s.status.value           if s.status else "",
        ]
        ws.append(row)
        if i % 2 == 0:
            for c in range(1, len(headers)+1):
                ws.cell(i+1, c).fill = PatternFill("solid", fgColor="F8FAFC")

    _auto_width(ws)
    fname = f"EMS_schedule_{semester}_{academic_year}_{exam_type}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_schedule_excel",
            table_name="exam_schedules",
            new_values={
                "file_type": "xlsx",
                "export_scope": "schedule",
                "row_count": len(scheds),
                "semester": semester,
                "academic_year": academic_year,
                "exam_type": exam_type,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, fname)


# ── GET /api/exports/submissions-excel ───────────────────────
@router.get("/submissions-excel")
def export_submissions_excel(
    semester:      str = None,
    academic_year: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
    request: Request = None,
):
    """Excel สถานะข้อสอบทุกวิชา"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        raise HTTPException(500, "ต้อง pip install openpyxl")

    if not semester or not academic_year:
        p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active==True).first()
        if p:
            semester = semester or p.semester
            academic_year = academic_year or p.academic_year

    subs = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section).joinedload(models.Section.course),
        joinedload(models.ExamSubmission.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSubmission.submitter),
        joinedload(models.ExamSubmission.material_request),
    ).join(models.Section).filter(
        models.Section.semester      == semester,
        models.Section.academic_year == academic_year,
    ).all()

    status_th = {
        "draft":"ร่าง","submitted":"รอตรวจ","approved":"อนุมัติ",
        "rejected":"ปฏิเสธ","released":"ปล่อยแล้ว",
    }
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "สถานะข้อสอบ"

    headers = [
        "รหัสวิชา","ชื่อวิชา","ตอน","อาจารย์ผู้รับผิดชอบ",
        "รูปแบบสอบ","อัปโหลด PDF","สเปคพิมพ์","สถานะ",
        "กระดาษเขียนตอบ","สมุดคำตอบ","OMR","หมายเหตุ",
        "อัปเดตล่าสุด",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    _style_header(ws, 1, len(headers))

    STATUS_COLORS = {
        "draft":"D4D4D4","submitted":"FEF3C7","approved":"DCFCE7",
        "rejected":"FEE2E2","released":"DBEAFE",
    }

    for i, s in enumerate(subs, 1):
        sec    = s.section
        course = sec.course  if sec else None
        mat    = s.material_request
        row = [
            course.course_id     if course else "",
            course.course_name_th if course else "",
            sec.section_no       if sec    else "",
            s.submitter.full_name if s.submitter else "",
            s.exam_type_choice or "—",
            "✅" if s.has_uploaded_pdf else "❌",
            "✅" if s.print_spec_confirmed else "❌",
            status_th.get(s.status.value if s.status else "", "—"),
            mat.answer_paper_sheets  if mat else 0,
            mat.answer_booklet_count if mat else 0,
            mat.omr_sheet_count      if mat else 0,
            mat.special_note         if mat else "",
            str(s.submitted_at.date()) if s.submitted_at else "",
        ]
        ws.append(row)
        color = STATUS_COLORS.get(s.status.value if s.status else "draft", "FFFFFF")
        ws.cell(i+1, 8).fill = PatternFill("solid", fgColor=color)
        ws.cell(i+1, 8).font = Font(bold=True)

    _auto_width(ws)
    fname = f"EMS_submissions_{semester}_{academic_year}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_submissions_excel",
            table_name="exam_submissions",
            new_values={
                "file_type": "xlsx",
                "export_scope": "submissions",
                "row_count": len(subs),
                "semester": semester,
                "academic_year": academic_year,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, fname)


@router.get("/workload-summary-excel")
def export_workload_summary_excel(
    semester: str = None,
    academic_year: str = None,
    exam_type: str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
    request: Request = None,
):
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(500, "ต้องติดตั้ง openpyxl")

    period = _resolve_period(db, semester, academic_year, exam_type)
    snapshot = get_period_workload_snapshot(db, period)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Workload Summary"
    headers = [
        "Staff Name",
        "Department",
        "Invigilation",
        "Paper Distribution",
        "External Exam",
        "Current Total",
        "Historical Total",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    _style_header(ws, 1, len(headers))

    for row in snapshot["summary"]:
        ws.append(
            [
                row["staff_name"],
                row["department"],
                row["invigilation_count"],
                row["paper_distribution_count"],
                row["external_exam_count"],
                row["total_workload"],
                row["historical_total_workload"],
            ]
        )

    _auto_width(ws)
    filename = f"EMS_workload_summary_{period.semester}_{period.academic_year}_{period.exam_type}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_workload_summary_excel",
            table_name="staffworkloads",
            new_values={
                "file_type": "xlsx",
                "export_scope": "workload_summary",
                "row_count": len(snapshot.entries) if 'snapshot' in locals() else 0,
                "semester": period.semester,
                "academic_year": period.academic_year,
                "exam_type": period.exam_type,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, filename)


@router.get("/workload-detail-excel")
def export_workload_detail_excel(
    semester: str = None,
    academic_year: str = None,
    exam_type: str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
    request: Request = None,
):
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(500, "ต้องติดตั้ง openpyxl")

    period = _resolve_period(db, semester, academic_year, exam_type)
    snapshot = get_period_workload_snapshot(db, period)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Workload Detail"
    headers = [
        "Staff Name",
        "Department",
        "Duty Type",
        "Date",
        "Time",
        "Context",
        "Room",
        "Workload Count",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    _style_header(ws, 1, len(headers))

    for row in snapshot["details"]:
        ws.append(
            [
                row["staff_name"],
                row["department"],
                row["duty_type"],
                row["date"],
                row["time"],
                row["context_label"],
                row["room"],
                row["workload_count"],
            ]
        )

    _auto_width(ws)
    filename = f"EMS_workload_detail_{period.semester}_{period.academic_year}_{period.exam_type}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_workload_detail_excel",
            table_name="staffworkloads",
            new_values={
                "file_type": "xlsx",
                "export_scope": "workload_detail",
                "row_count": len(snapshot.entries) if 'snapshot' in locals() else 0,
                "semester": period.semester,
                "academic_year": period.academic_year,
                "exam_type": period.exam_type,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, filename)


@router.get("/paper-distribution-excel")
def export_paper_distribution_excel(
    semester: str = None,
    academic_year: str = None,
    exam_type: str = "final",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
    request: Request = None,
):
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(500, "ต้องติดตั้ง openpyxl")

    period = _resolve_period(db, semester, academic_year, exam_type)
    rows = db.query(models.PaperDistributionAssignment).options(
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

    slot_context: dict[tuple[str, str], dict[str, list[str]]] = {}
    for schedule in schedules:
        key = (str(schedule.exam_date) if schedule.exam_date else "", schedule.exam_time or "")
        context = slot_context.setdefault(key, {"courses": [], "rooms": []})
        if schedule.section and schedule.section.course:
            label = f"{schedule.section.course.course_id} Sec {schedule.section.section_no}"
            if label not in context["courses"]:
                context["courses"].append(label)
        if schedule.room and schedule.room.room_name not in context["rooms"]:
            context["rooms"].append(schedule.room.room_name)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Paper Distribution"
    headers = [
        "Staff Name",
        "Department",
        "Date",
        "Time",
        "Covered Courses",
        "Covered Rooms",
        "Schedules Covered",
        "Workload Count",
        "Assignment Mode",
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    _style_header(ws, 1, len(headers))

    for row in rows:
        context = slot_context.get((row.exam_date, row.exam_time), {"courses": [], "rooms": []})
        ws.append(
            [
                row.user.full_name if row.user else f"User #{row.user_id}",
                (row.user.division or row.user.unit) if row.user else "",
                row.exam_date,
                row.exam_time,
                ", ".join(context["courses"]),
                ", ".join(context["rooms"]),
                row.covered_schedule_count or 0,
                row.workload_units or 1,
                row.assignment_mode,
            ]
        )

    _auto_width(ws)
    filename = f"EMS_paper_distribution_{period.semester}_{period.academic_year}_{period.exam_type}.xlsx"

    # Log export action
    try:
        log_action(
            db=db,
            actor=current_user,
            action="export_paper_distribution_excel",
            table_name="paper_distribution_assignments",
            new_values={
                "file_type": "xlsx",
                "export_scope": "paper_distribution",
                "row_count": len(rows),
                "semester": period.semester,
                "academic_year": period.academic_year,
                "exam_type": period.exam_type,
            },
            request=request,
            http_status=200
        )
    except Exception as e:
        import sys
        print(f"Warning: Export logging failed: {e}", file=sys.stderr)

    return _workbook_response(wb, filename)
