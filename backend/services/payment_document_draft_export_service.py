"""Draft payment document Excel export service.

Generates a draft-labelled Excel workbook from the term-specific
payment document settings. Export is blocked unless all gate checks
pass. No database writes occur; export is stateless.

Safety invariants enforced:
  - payment_authorization_enabled remains false
  - final_export_enabled remains false
  - document_status remains DRAFT_NOT_AUTHORIZED
  - requires ACCEPTED_FOR_DRAFT_EXPORT review record with comment
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from services.official_payment_document_draft_service import (
    build_official_payment_document_draft_preview,
)

THAI_DRAFT_LABEL = "ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย"
ENGLISH_DRAFT_LABEL = "Draft for review only. Not payment authorization."
DRAFT_NOT_AUTHORIZED = "DRAFT_NOT_AUTHORIZED"


def _document_id(payload: dict[str, Any]) -> str:
    academic_year = payload.get("academic_year") or "unknown"
    semester = payload.get("semester") or "unknown"
    exam_type = payload.get("exam_type") or "unknown"
    period_id = payload.get("period_id") or "all"
    return f"ADVANCE_PAYMENT_DRAFT_SUMMARY:{academic_year}:{semester}:{exam_type}:{period_id}"


def _find_accepted_review(
    db: Session, document_id: str
) -> models.PaymentDocumentReviewRecord:
    record = (
        db.query(models.PaymentDocumentReviewRecord)
        .filter(
            models.PaymentDocumentReviewRecord.document_id == document_id,
            models.PaymentDocumentReviewRecord.review_status == "ACCEPTED_FOR_DRAFT_EXPORT",
        )
        .order_by(models.PaymentDocumentReviewRecord.created_at.desc())
        .first()
    )
    if record is None:
        raise HTTPException(
            status_code=400,
            detail="export gate: no ACCEPTED_FOR_DRAFT_EXPORT review record for this document",
        )
    if not record.comment:
        raise HTTPException(
            status_code=400,
            detail="export gate: reviewer comment is required",
        )
    return record


def _check_gate(draft: dict[str, Any]) -> None:
    meta = draft["metadata"]
    if meta.get("settings_source_status") != "CONFIGURED":
        raise HTTPException(400, "export gate: settings_source_status must be CONFIGURED")
    if meta.get("settings_status") != "ACTIVE_FOR_DRAFT_PREVIEW":
        raise HTTPException(400, "export gate: settings_status must be ACTIVE_FOR_DRAFT_PREVIEW")
    if meta.get("calculation_status") != "CALCULATED_FROM_SETTINGS":
        raise HTTPException(400, "export gate: calculation_status must be CALCULATED_FROM_SETTINGS")
    if not meta.get("paper_distribution_responsible_group"):
        raise HTTPException(400, "export gate: paper_distribution_responsible_group is required")
    if draft.get("payment_authorization_enabled", False):
        raise HTTPException(400, "export gate: payment_authorization_enabled invariant violated")
    if draft.get("final_export_enabled", False):
        raise HTTPException(400, "export gate: final_export_enabled invariant violated")


def _fmt_amount(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{Decimal(str(value)):.2f}"
    except Exception:
        return str(value)


def _fmt_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _build_workbook(
    draft: dict[str, Any],
    review: models.PaymentDocumentReviewRecord,
    generated_at: str,
) -> Any:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    meta = draft["metadata"]
    rows = draft["rows"]
    totals = draft["totals"]

    YELLOW_FILL = PatternFill("solid", fgColor="FFFF99")
    BLUE_FILL = PatternFill("solid", fgColor="BDD7EE")
    GRAY_FILL = PatternFill("solid", fgColor="F2F2F2")
    RED_FONT = Font(bold=True, color="C00000")
    BOLD = Font(bold=True)
    BOLD_WHITE = Font(bold=True, color="FFFFFF")
    CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
    RIGHT = Alignment(horizontal="right", vertical="center")

    # ── Sheet 1: ร่างเอกสาร ──────────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "ร่างเอกสาร"

    num_cols = 8

    def _banner_row(ws: Any, row_num: int, text: str, fill: Any, font: Font) -> None:
        ws.merge_cells(start_row=row_num, start_column=1, end_row=row_num, end_column=num_cols)
        cell = ws.cell(row_num, 1, text)
        cell.fill = fill
        cell.font = font
        cell.alignment = CENTER
        ws.row_dimensions[row_num].height = 22

    _banner_row(ws1, 1, THAI_DRAFT_LABEL, YELLOW_FILL, Font(bold=True, size=12))
    _banner_row(ws1, 2, ENGLISH_DRAFT_LABEL, YELLOW_FILL, Font(size=10))
    _banner_row(ws1, 3, DRAFT_NOT_AUTHORIZED, YELLOW_FILL, Font(bold=True, color="C00000"))

    ws1.row_dimensions[4].height = 8

    term_label = meta.get("term_label") or f"{meta.get('semester','')}/{meta.get('academic_year','')}"
    _banner_row(ws1, 5, f"สรุปจำนวนกรรมการและค่าตอบแทน — ภาคการศึกษาที่ {term_label}", PatternFill(), BOLD)

    weekday_rate = _fmt_amount(meta.get("settings_weekday_rate"))
    weekend_rate = _fmt_amount(meta.get("settings_weekend_rate"))
    calc_status = meta.get("calculation_status", "")
    ws1.merge_cells(start_row=6, start_column=1, end_row=6, end_column=num_cols)
    ws1.cell(6, 1, f"อัตราวันจันทร์-ศุกร์: {weekday_rate} บาท | อัตราวันเสาร์-อาทิตย์: {weekend_rate} บาท | {calc_status}").alignment = LEFT

    group = meta.get("paper_distribution_responsible_group") or "-"
    person = meta.get("paper_distribution_responsible_person") or ""
    responsible = f"{group}" + (f" / {person}" if person else "")
    ws1.merge_cells(start_row=7, start_column=1, end_row=7, end_column=num_cols)
    ws1.cell(7, 1, f"ผู้รับผิดชอบจ่ายข้อสอบ: {responsible}").alignment = LEFT

    ws1.row_dimensions[8].height = 8

    headers = [
        "วันที่สอบ",
        "ช่วงเวลา",
        "ประเภทวัน",
        "จำนวนกรรมการคุมสอบ",
        "ค่าตอบแทนคุมสอบ (บาท)",
        "จำนวนกรรมการจ่ายข้อสอบ",
        "ค่าตอบแทนจ่ายข้อสอบ (บาท)",
        "รวมค่าตอบแทน (บาท)",
    ]
    HEADER_ROW = 9
    for col_idx, header in enumerate(headers, 1):
        cell = ws1.cell(HEADER_ROW, col_idx, header)
        cell.fill = BLUE_FILL
        cell.font = BOLD
        cell.alignment = CENTER
    ws1.row_dimensions[HEADER_ROW].height = 30

    DATA_START = 10
    for row_num, row in enumerate(rows, DATA_START):
        day_type_th = "วันหยุด" if row["day_type"] == "WEEKEND" else ("วันธรรมดา" if row["day_type"] == "WEEKDAY" else row["day_type"])
        values = [
            row.get("exam_date") or "",
            row.get("time_slot") or "",
            day_type_th,
            _fmt_int(row.get("invigilation_committee_count")),
            _fmt_amount(row.get("invigilation_compensation_amount")),
            _fmt_int(row.get("paper_distribution_committee_count")),
            _fmt_amount(row.get("paper_distribution_compensation_amount")),
            _fmt_amount(row.get("total_compensation_amount")),
        ]
        fill = GRAY_FILL if (row_num - DATA_START) % 2 == 1 else PatternFill()
        for col_idx, val in enumerate(values, 1):
            cell = ws1.cell(row_num, col_idx, val)
            cell.fill = fill
            cell.alignment = RIGHT if col_idx >= 4 else LEFT

    totals_row = DATA_START + len(rows)
    totals_values = [
        "รวมทั้งสิ้น", "",  "", "",
        _fmt_amount(totals.get("invigilation_compensation_amount")),
        "",
        _fmt_amount(totals.get("paper_distribution_compensation_amount")),
        _fmt_amount(totals.get("grand_total_amount")),
    ]
    for col_idx, val in enumerate(totals_values, 1):
        cell = ws1.cell(totals_row, col_idx, val)
        cell.font = RED_FONT
        cell.alignment = RIGHT if col_idx >= 4 else LEFT

    inv_count = _fmt_int(totals.get("invigilation_committee_count"))
    paper_count = _fmt_int(totals.get("paper_distribution_committee_count"))
    ws1.cell(totals_row, 4, inv_count).font = RED_FONT
    ws1.cell(totals_row, 6, paper_count).font = RED_FONT

    ts_row = totals_row + 2
    ws1.merge_cells(start_row=ts_row, start_column=1, end_row=ts_row, end_column=num_cols)
    ws1.cell(ts_row, 1, f"สร้างไฟล์เมื่อ: {generated_at}").alignment = LEFT
    ts_row2 = ts_row + 1
    ws1.merge_cells(start_row=ts_row2, start_column=1, end_row=ts_row2, end_column=num_cols)
    ws1.cell(ts_row2, 1, f"{THAI_DRAFT_LABEL}").font = Font(bold=True, color="C00000")
    ws1.cell(ts_row2, 1).alignment = CENTER
    ws1.cell(ts_row2, 1).fill = YELLOW_FILL

    col_widths = [16, 18, 14, 20, 24, 24, 28, 22]
    for col_idx, width in enumerate(col_widths, 1):
        ws1.column_dimensions[get_column_letter(col_idx)].width = width

    # ── Sheet 2: การตรวจร่าง ─────────────────────────────────────────────────
    ws2 = wb.create_sheet("การตรวจร่าง")

    _banner_row(ws2, 1, THAI_DRAFT_LABEL, YELLOW_FILL, Font(bold=True, size=12))
    _banner_row(ws2, 2, ENGLISH_DRAFT_LABEL, YELLOW_FILL, Font(size=10))
    ws2.row_dimensions[3].height = 8

    review_headers = ["ผู้ตรวจ", "บทบาท", "สถานะการตรวจ", "เวลาตรวจ"]
    for col_idx, h in enumerate(review_headers, 1):
        cell = ws2.cell(4, col_idx, h)
        cell.fill = BLUE_FILL
        cell.font = BOLD
        cell.alignment = CENTER

    reviewed_at = getattr(review, "reviewed_at", None) or getattr(review, "created_at", None)
    ws2.cell(5, 1, getattr(review, "reviewer_name", "") or "").alignment = LEFT
    ws2.cell(5, 2, getattr(review, "reviewer_role", "") or "").alignment = LEFT
    ws2.cell(5, 3, getattr(review, "review_status", "") or "").alignment = LEFT
    ws2.cell(5, 4, str(reviewed_at) if reviewed_at else "-").alignment = LEFT

    ws2.row_dimensions[6].height = 8

    ws2.merge_cells(start_row=7, start_column=1, end_row=7, end_column=4)
    ws2.cell(7, 1, "ความเห็นผู้ตรวจ:").font = BOLD

    comment_text = getattr(review, "comment", "") or ""
    ws2.merge_cells(start_row=8, start_column=1, end_row=8, end_column=4)
    comment_cell = ws2.cell(8, 1, comment_text)
    comment_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws2.row_dimensions[8].height = 60

    ws2.row_dimensions[9].height = 8

    settings_ref = f"ภาคเรียน: {meta.get('settings_term') or term_label} | สถานะการตั้งค่า: {meta.get('settings_status') or '-'}"
    ws2.merge_cells(start_row=10, start_column=1, end_row=10, end_column=4)
    ws2.cell(10, 1, settings_ref).alignment = LEFT

    ws2.merge_cells(start_row=11, start_column=1, end_row=11, end_column=4)
    ws2.cell(11, 1, f"สร้างไฟล์เมื่อ: {generated_at}").alignment = LEFT

    ws2.merge_cells(start_row=12, start_column=1, end_row=12, end_column=4)
    ws2.cell(12, 1, f"{DRAFT_NOT_AUTHORIZED}").font = Font(bold=True, color="C00000")

    for col_idx, width in enumerate([28, 16, 28, 22], 1):
        ws2.column_dimensions[get_column_letter(col_idx)].width = width

    return wb


def _export_filename(payload: dict[str, Any], generated_at: datetime) -> str:
    semester = payload.get("semester") or "x"
    academic_year = payload.get("academic_year") or "xxxx"
    ts = generated_at.strftime("%Y%m%d_%H%M")
    return f"EMS_DRAFT_PAYMENT_DOCUMENT_{semester}-{academic_year}_{ts}.xlsx"


def build_payment_document_draft_export(
    db: Session,
    request_payload: dict[str, Any],
) -> tuple[Any, str]:
    """Build draft payment document Excel workbook.

    Returns (workbook, filename). Raises HTTPException on gate failure.
    This function performs no DB writes.
    """
    doc_id = _document_id(request_payload)
    review = _find_accepted_review(db, doc_id)

    draft = build_official_payment_document_draft_preview(db, request_payload)
    _check_gate(draft)

    generated_at = datetime.now(timezone.utc)
    wb = _build_workbook(draft, review, generated_at.strftime("%Y-%m-%d %H:%M UTC"))
    filename = _export_filename(request_payload, generated_at)
    return wb, filename
