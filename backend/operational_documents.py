from __future__ import annotations

import io
import math
import os
import re
from datetime import date
from typing import Iterable

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = A4
FACULTY_NAME = "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่"

_FONT_READY = False
_FONT_NAME = "Helvetica"
_FONT_BOLD_NAME = "Helvetica-Bold"

_THAI_DAYS = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]
_THAI_MONTHS_SHORT = [
    "ม.ค.",
    "ก.พ.",
    "มี.ค.",
    "เม.ย.",
    "พ.ค.",
    "มิ.ย.",
    "ก.ค.",
    "ส.ค.",
    "ก.ย.",
    "ต.ค.",
    "พ.ย.",
    "ธ.ค.",
]


def _font_candidates() -> list[tuple[str, str]]:
    return [
        ("EMS-Thai", r"C:\Windows\Fonts\THSarabunNew.ttf"),
        ("EMS-Thai-Bold", r"C:\Windows\Fonts\THSarabunNew Bold.ttf"),
        ("EMS-Thai", "/usr/share/fonts/truetype/thaifonts/THSarabunNew.ttf"),
        ("EMS-Thai-Bold", "/usr/share/fonts/truetype/thaifonts/THSarabunNew Bold.ttf"),
        ("EMS-Thai", "/usr/share/fonts/truetype/tlwg/THSarabunNew.ttf"),
        ("EMS-Thai-Bold", "/usr/share/fonts/truetype/tlwg/THSarabunNew-Bold.ttf"),
    ]


def ensure_document_fonts() -> tuple[str, str]:
    global _FONT_READY, _FONT_NAME, _FONT_BOLD_NAME
    if _FONT_READY:
        return _FONT_NAME, _FONT_BOLD_NAME

    registered: set[str] = set()
    for alias, path in _font_candidates():
        if not os.path.exists(path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(alias, path))
            registered.add(alias)
        except Exception:
            continue

    if "EMS-Thai" in registered:
        _FONT_NAME = "EMS-Thai"
    if "EMS-Thai-Bold" in registered:
        _FONT_BOLD_NAME = "EMS-Thai-Bold"
    else:
        _FONT_BOLD_NAME = _FONT_NAME

    _FONT_READY = True
    return _FONT_NAME, _FONT_BOLD_NAME


def _safe_text(value: object | None) -> str:
    return str(value).strip() if value not in (None, "") else "-"


def _safe_filename(value: str) -> str:
    return re.sub(r"[^\w\-.]+", "_", value, flags=re.UNICODE).strip("_") or "document"


def _new_canvas() -> tuple[canvas.Canvas, io.BytesIO]:
    ensure_document_fonts()
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    pdf.setTitle("EMS Operational Exam Documents")
    return pdf, buf


def _set_font(pdf: canvas.Canvas, size: float, bold: bool = False) -> None:
    normal_name, bold_name = ensure_document_fonts()
    pdf.setFont(bold_name if bold else normal_name, size)


def _truncate_text(text: str, max_width: float, size: float, bold: bool = False) -> str:
    normal_name, bold_name = ensure_document_fonts()
    font_name = bold_name if bold else normal_name
    candidate = text
    if pdfmetrics.stringWidth(candidate, font_name, size) <= max_width:
        return candidate
    ellipsis = "..."
    while candidate:
        candidate = candidate[:-1]
        trimmed = f"{candidate}{ellipsis}"
        if pdfmetrics.stringWidth(trimmed, font_name, size) <= max_width:
            return trimmed
    return ellipsis


def _draw_centered(pdf: canvas.Canvas, text: str, y: float, size: float, bold: bool = False) -> None:
    _set_font(pdf, size, bold=bold)
    pdf.drawCentredString(PAGE_WIDTH / 2, y, text)


def _draw_label_value(
    pdf: canvas.Canvas,
    label: str,
    value: str,
    x: float,
    y: float,
    label_width: float,
    value_width: float,
    *,
    size: float = 14,
) -> None:
    _set_font(pdf, size, bold=False)
    pdf.drawString(x, y, label)
    _set_font(pdf, size, bold=True)
    pdf.drawString(x + label_width, y, _truncate_text(value, value_width, size, bold=True))


def _draw_metadata_grid(
    pdf: canvas.Canvas,
    x: float,
    top_y: float,
    width: float,
    rows: list[tuple[str, str, str, str]],
    *,
    row_height: float = 12 * mm,
) -> float:
    left_col = width * 0.5
    right_col = width - left_col
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.75)
    for index, (left_label, left_value, right_label, right_value) in enumerate(rows):
        y = top_y - (index + 1) * row_height
        pdf.rect(x, y, width, row_height, stroke=1, fill=0)
        pdf.line(x + left_col, y, x + left_col, y + row_height)
        _draw_label_value(pdf, left_label, left_value, x + 4 * mm, y + 3.5 * mm, 22 * mm, left_col - 30 * mm)
        _draw_label_value(pdf, right_label, right_value, x + left_col + 4 * mm, y + 3.5 * mm, 18 * mm, right_col - 26 * mm)
    return top_y - len(rows) * row_height


def _format_exam_type_th(exam_type: str | None) -> str:
    return "ปลายภาค" if str(exam_type or "").lower() == "final" else "กลางภาค"


def _format_exam_date_th(value: str | date | None) -> str:
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError:
            return _safe_text(value)
    if not isinstance(value, date):
        return "-"
    weekday = _THAI_DAYS[value.weekday()]
    month = _THAI_MONTHS_SHORT[value.month - 1]
    thai_year = value.year + 543 if value.year < 2400 else value.year
    return f"{weekday} {value.day} {month} {thai_year}"


def _term_line(exam_type: str, semester: str, academic_year: str) -> str:
    exam_type_th = _format_exam_type_th(exam_type)
    return f"การสอบ{exam_type_th} ภาคการศึกษาที่ {semester} ปีการศึกษา {academic_year}"


def _participant_ranges(student_ids: list[str]) -> list[str]:
    cleaned = [item.strip() for item in student_ids if item and item.strip()]
    if not cleaned:
        return []
    ranges: list[str] = []
    start = cleaned[0]
    prev = cleaned[0]
    prev_num: int | None = int(prev) if prev.isdigit() else None
    for current in cleaned[1:]:
        current_num: int | None = int(current) if current.isdigit() else None
        sequential = (
            prev_num is not None
            and current_num is not None
            and len(current) == len(prev)
            and current_num == prev_num + 1
        )
        if sequential:
            prev = current
            prev_num = current_num
            continue
        ranges.append(start if start == prev else f"{start} - {prev}")
        start = current
        prev = current
        prev_num = current_num
    ranges.append(start if start == prev else f"{start} - {prev}")
    return ranges


def _draw_three_column_list(
    pdf: canvas.Canvas,
    items: list[str],
    x: float,
    top_y: float,
    width: float,
    bottom_y: float,
    *,
    row_height: float = 10 * mm,
) -> None:
    col_width = width / 3
    rows_per_page = max(1, int((top_y - bottom_y) // row_height))
    index = 0
    while index < len(items):
        for row_index in range(rows_per_page):
            y = top_y - (row_index + 1) * row_height
            if y < bottom_y:
                break
            for col_index in range(3):
                if index >= len(items):
                    return
                cell_x = x + col_index * col_width
                pdf.rect(cell_x, y, col_width, row_height, stroke=1, fill=0)
                _set_font(pdf, 15, bold=False)
                text = _truncate_text(items[index], col_width - 8 * mm, 15)
                pdf.drawString(cell_x + 3 * mm, y + 3.2 * mm, text)
                index += 1
        if index < len(items):
            pdf.showPage()
            _draw_centered(pdf, "รหัสผู้เข้าสอบ", PAGE_HEIGHT - 18 * mm, 22, bold=True)


def generate_participant_code_announcement_pdf(payload: dict[str, object]) -> bytes:
    pdf, buf = _new_canvas()
    exam_type = _safe_text(payload.get("exam_type"))
    semester = _safe_text(payload.get("semester"))
    academic_year = _safe_text(payload.get("academic_year"))
    course_code = _safe_text(payload.get("course_code"))
    course_name = _safe_text(payload.get("course_name"))
    section_no = _safe_text(payload.get("section_no"))
    room_name = _safe_text(payload.get("room_name"))
    exam_date = _format_exam_date_th(payload.get("exam_date"))
    exam_time = _safe_text(payload.get("exam_time"))
    total_students = _safe_text(payload.get("total_students"))
    instructor_name = _safe_text(payload.get("instructor_name"))
    student_rows = payload.get("student_rows") or []
    student_ids = [str(item.get("student_id", "")).strip() for item in student_rows if isinstance(item, dict)]
    ranges = _participant_ranges(student_ids)

    top = PAGE_HEIGHT - 20 * mm
    _draw_centered(pdf, "รหัสผู้เข้าสอบ", top, 24, bold=True)
    _draw_centered(pdf, FACULTY_NAME, top - 10 * mm, 17, bold=True)
    _draw_centered(pdf, _term_line(exam_type, semester, academic_year), top - 18 * mm, 16, bold=False)

    grid_bottom = _draw_metadata_grid(
        pdf,
        18 * mm,
        top - 30 * mm,
        PAGE_WIDTH - 36 * mm,
        [
            ("กระบวนวิชา", f"{course_code} {course_name}", "ตอน", section_no),
            ("ห้องสอบ", room_name, "วันที่", exam_date),
            ("เวลา", exam_time, "จำนวนนักศึกษา", total_students),
            ("อาจารย์ผู้สอน", instructor_name, "เอกสาร", "รหัสผู้เข้าสอบ"),
        ],
    )
    _set_font(pdf, 15, bold=False)
    pdf.drawString(18 * mm, grid_bottom - 8 * mm, "ได้แก่")
    _draw_three_column_list(pdf, ranges or ["-"], 18 * mm, grid_bottom - 12 * mm, PAGE_WIDTH - 36 * mm, 18 * mm)
    pdf.save()
    return buf.getvalue()


def _draw_signature_table_header(pdf: canvas.Canvas, x: float, y: float, widths: tuple[float, float, float], row_height: float) -> None:
    pdf.rect(x, y - row_height, sum(widths), row_height, stroke=1, fill=0)
    pdf.line(x + widths[0], y - row_height, x + widths[0], y)
    pdf.line(x + widths[0] + widths[1], y - row_height, x + widths[0] + widths[1], y)
    _set_font(pdf, 15, bold=True)
    pdf.drawCentredString(x + widths[0] / 2, y - row_height + 3.5 * mm, "ชื่อ - นามสกุล")
    pdf.drawCentredString(x + widths[0] + widths[1] / 2, y - row_height + 3.5 * mm, "รหัสนักศึกษา")
    pdf.drawCentredString(x + widths[0] + widths[1] + widths[2] / 2, y - row_height + 3.5 * mm, "ลายมือชื่อ")


def _draw_signature_header(pdf: canvas.Canvas, payload: dict[str, object]) -> float:
    exam_type = _safe_text(payload.get("exam_type"))
    semester = _safe_text(payload.get("semester"))
    academic_year = _safe_text(payload.get("academic_year"))
    course_code = _safe_text(payload.get("course_code"))
    course_name = _safe_text(payload.get("course_name"))
    section_no = _safe_text(payload.get("section_no"))
    room_name = _safe_text(payload.get("room_name"))
    exam_date = _format_exam_date_th(payload.get("exam_date"))
    exam_time = _safe_text(payload.get("exam_time"))
    total_students = _safe_text(payload.get("total_students"))
    instructor_name = _safe_text(payload.get("instructor_name"))

    top = PAGE_HEIGHT - 20 * mm
    _draw_centered(pdf, "ใบลงลายมือชื่อผู้เข้าสอบ", top, 24, bold=True)
    _draw_centered(pdf, FACULTY_NAME, top - 10 * mm, 17, bold=True)
    _draw_centered(pdf, _term_line(exam_type, semester, academic_year), top - 18 * mm, 16, bold=False)
    return _draw_metadata_grid(
        pdf,
        18 * mm,
        top - 30 * mm,
        PAGE_WIDTH - 36 * mm,
        [
            ("กระบวนวิชา", f"{course_code} {course_name}", "ตอน", section_no),
            ("ห้องสอบ", room_name, "วันที่", exam_date),
            ("เวลา", exam_time, "จำนวนนักศึกษา", total_students),
            ("อาจารย์ผู้สอน", instructor_name, "เอกสาร", "ใบลงลายมือชื่อ"),
        ],
    )


def generate_signature_sheet_pdf(payload: dict[str, object]) -> bytes:
    pdf, buf = _new_canvas()
    rows = payload.get("student_rows") or []
    student_rows = [item for item in rows if isinstance(item, dict)]
    table_x = 18 * mm
    table_width = PAGE_WIDTH - 36 * mm
    widths = (table_width * 0.5, table_width * 0.2, table_width * 0.3)
    row_height = 9 * mm
    rows_per_page = 23

    index = 0
    while True:
        grid_bottom = _draw_signature_header(pdf, payload)
        current_y = grid_bottom - 6 * mm
        _draw_signature_table_header(pdf, table_x, current_y, widths, row_height)
        current_y -= row_height

        page_items = student_rows[index:index + rows_per_page]
        if not page_items:
            page_items = [{}]

        for row_offset, item in enumerate(page_items, start=1):
            y = current_y - row_height
            pdf.rect(table_x, y, table_width, row_height, stroke=1, fill=0)
            pdf.line(table_x + widths[0], y, table_x + widths[0], y + row_height)
            pdf.line(table_x + widths[0] + widths[1], y, table_x + widths[0] + widths[1], y + row_height)
            name = _safe_text(item.get("student_name") if isinstance(item, dict) else None)
            student_id = _safe_text(item.get("student_id") if isinstance(item, dict) else None)
            _set_font(pdf, 14, bold=False)
            numbered_name = f"{index + row_offset}. {name}"
            pdf.drawString(table_x + 3 * mm, y + 3.0 * mm, _truncate_text(numbered_name, widths[0] - 6 * mm, 14))
            pdf.drawCentredString(table_x + widths[0] + widths[1] / 2, y + 3.0 * mm, _truncate_text(student_id, widths[1] - 6 * mm, 14))
            pdf.line(table_x + widths[0] + widths[1] + 4 * mm, y + 3 * mm, table_x + widths[0] + widths[1] + widths[2] - 4 * mm, y + 3 * mm)
            current_y = y

        index += len(page_items if student_rows else [])
        if index >= len(student_rows):
            break
        pdf.showPage()

    pdf.save()
    return buf.getvalue()


def _draw_qr_box(pdf: canvas.Canvas, x: float, y: float, size: float, value: str | None, title: str, subtitle: str) -> None:
    pdf.rect(x, y, size, size, stroke=1, fill=0)
    _set_font(pdf, 13, bold=True)
    pdf.drawCentredString(x + size / 2, y + size + 5 * mm, title)
    _set_font(pdf, 11, bold=False)
    pdf.drawCentredString(x + size / 2, y - 4 * mm, subtitle)

    if not value:
        drawing = Drawing(size, size)
        drawing.add(Rect(0, 0, size, size, strokeColor=colors.black, fillColor=None))
        drawing.add(String(8, size / 2 - 5, "QR Placeholder", fontSize=10))
        renderPDF.draw(drawing, pdf, x, y)
        return

    qr = QrCodeWidget(value)
    bounds = qr.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, pdf, x, y)


def generate_envelope_cover_pdf(payload: dict[str, object]) -> bytes:
    pdf, buf = _new_canvas()
    exam_type = _safe_text(payload.get("exam_type"))
    semester = _safe_text(payload.get("semester"))
    academic_year = _safe_text(payload.get("academic_year"))
    course_code = _safe_text(payload.get("course_code"))
    course_name = _safe_text(payload.get("course_name"))
    section_no = _safe_text(payload.get("section_no"))
    room_name = _safe_text(payload.get("room_name"))
    exam_date = _format_exam_date_th(payload.get("exam_date"))
    exam_time = _safe_text(payload.get("exam_time"))
    instructor_name = _safe_text(payload.get("instructor_name"))
    invigilators = [
        _safe_text(item.get("name") if isinstance(item, dict) else item)
        for item in (payload.get("invigilators") or [])
    ]

    top = PAGE_HEIGHT - 18 * mm
    _draw_centered(pdf, f"การสอบ{_format_exam_type_th(exam_type)}/Final Exams", top, 22, bold=True)
    _draw_centered(pdf, FACULTY_NAME, top - 8 * mm, 16, bold=True)
    _draw_centered(pdf, f"ภาคเรียนที่/Semester {semester} ปีการศึกษา/Academic Year {academic_year}", top - 16 * mm, 15, bold=False)

    body_bottom = _draw_metadata_grid(
        pdf,
        18 * mm,
        top - 28 * mm,
        PAGE_WIDTH - 36 * mm,
        [
            ("Course", course_code, "Section", section_no),
            ("ชื่อวิชา", course_name, "Date", exam_date),
            ("Room", room_name, "Time", exam_time),
            ("Instructor", instructor_name, "Document", "ปกซองข้อสอบ"),
        ],
    )

    list_top = body_bottom - 10 * mm
    pdf.rect(18 * mm, list_top - 55 * mm, PAGE_WIDTH - 36 * mm, 55 * mm, stroke=1, fill=0)
    _set_font(pdf, 15, bold=True)
    pdf.drawString(21 * mm, list_top - 6 * mm, "กรรมการคุมสอบ/Invigilator")
    _set_font(pdf, 14, bold=False)
    display_rows = invigilators or ["ยังไม่ได้มอบหมายผู้คุมสอบ"]
    for index, name in enumerate(display_rows[:6], start=1):
        line_y = list_top - (index * 8.5 * mm)
        pdf.drawString(24 * mm, line_y, f"{index}. {name}")
        pdf.line(120 * mm, line_y - 1.5 * mm, PAGE_WIDTH - 24 * mm, line_y - 1.5 * mm)

    qr_size = 42 * mm
    qr_y = 24 * mm
    qr_x_left = 28 * mm
    qr_y_left = PAGE_WIDTH - 28 * mm - qr_size
    _draw_qr_box(
        pdf,
        qr_x_left,
        qr_y,
        qr_size,
        str(payload.get("qr_x_value") or ""),
        "QR X",
        "ยืนยันการรับข้อสอบ",
    )
    _draw_qr_box(
        pdf,
        qr_y_left,
        qr_y,
        qr_size,
        None,
        "QR Y",
        "ระเบียบ / วิธีการ (กำหนดภายหลัง)",
    )

    pdf.save()
    return buf.getvalue()


def build_document_filename(document_type: str, payload: dict[str, object]) -> str:
    course_code = _safe_filename(_safe_text(payload.get("course_code")))
    section_no = _safe_filename(_safe_text(payload.get("section_no")))
    room_name = _safe_filename(_safe_text(payload.get("room_name")))
    prefix = f"{course_code}_sec{section_no}_{room_name}"
    names = {
        "participant_codes": f"รหัสผู้เข้าสอบ_{prefix}.pdf",
        "signature_sheet": f"ใบลงลายมือชื่อ_{prefix}.pdf",
        "envelope_cover": f"ปกซองข้อสอบ_{prefix}.pdf",
    }
    return names.get(document_type, f"{document_type}_{prefix}.pdf")


def build_bundle_filename(scope_label: str, document_type: str) -> str:
    suffix = "all" if document_type == "all" else _safe_filename(document_type)
    return f"ems_exam_documents_{_safe_filename(scope_label)}_{suffix}.zip"


def normalize_document_type(document_type: str | None) -> str:
    value = (document_type or "all").strip().lower()
    aliases = {
        "participant": "participant_codes",
        "participant_code": "participant_codes",
        "participant_codes": "participant_codes",
        "announcement": "participant_codes",
        "signature": "signature_sheet",
        "signature_sheet": "signature_sheet",
        "attendance": "signature_sheet",
        "cover": "envelope_cover",
        "envelope": "envelope_cover",
        "envelope_cover": "envelope_cover",
        "all": "all",
    }
    normalized = aliases.get(value)
    if not normalized:
        raise ValueError(f"Unsupported document type: {document_type}")
    return normalized


def iter_document_types(document_type: str) -> Iterable[str]:
    normalized = normalize_document_type(document_type)
    if normalized == "all":
        return ("participant_codes", "signature_sheet", "envelope_cover")
    return (normalized,)
