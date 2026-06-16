"""Thai-safe export helpers for EMS document downloads.

The helpers centralize workbook font styling, CSV encoding, RFC 5987 download
filenames, and ReportLab Thai font registration without changing export data.
"""
from __future__ import annotations

import csv
import io
import os
import re
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import quote

from fastapi.responses import StreamingResponse

THAI_OFFICIAL_FONT_STACK = (
    "TH Sarabun New",
    "Sarabun",
    "Noto Sans Thai",
    "Tahoma",
    "Arial Unicode MS",
    "sans-serif",
)
XLSX_THAI_FONT = "TH Sarabun New"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV_MIME = "text/csv; charset=utf-8"
MOJIBAKE_MARKERS = ("โ€", "๏ฟฝ", "\ufffd")


def contains_thai(value: str) -> bool:
    return any("\u0e00" <= char <= "\u0e7f" for char in value)


def has_mojibake_marker(value: object) -> bool:
    if value is None:
        return False
    text = str(value)
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def assert_no_mojibake(value: object, *, context: str = "export") -> None:
    if has_mojibake_marker(value):
        raise ValueError(f"Potential mojibake marker found in {context}: {value!r}")


def safe_ascii_filename(filename: str, *, default: str = "EMS_EXPORT") -> str:
    """Return a conservative ASCII fallback filename for Content-Disposition."""
    name = Path(filename or default).name
    stem, suffix = os.path.splitext(name)
    ascii_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    ascii_suffix = re.sub(r"[^A-Za-z0-9.]+", "", suffix)[:16]
    if not ascii_stem:
        ascii_stem = default
    return f"{ascii_stem}{ascii_suffix or ''}"


def content_disposition(
    filename: str,
    *,
    disposition: str = "attachment",
    ascii_fallback: str | None = None,
) -> str:
    """Build a download header with ASCII fallback plus UTF-8 filename*."""
    fallback = safe_ascii_filename(ascii_fallback or filename)
    utf8_name = quote(Path(filename).name, safe="")
    return f"{disposition}; filename=\"{fallback}\"; filename*=UTF-8''{utf8_name}"


def download_headers(
    filename: str,
    *,
    disposition: str = "attachment",
    ascii_fallback: str | None = None,
) -> dict[str, str]:
    return {
        "Content-Disposition": content_disposition(
            filename,
            disposition=disposition,
            ascii_fallback=ascii_fallback,
        )
    }


def _thai_font(font, *, size: int | float | None = None, bold: bool | None = None, color: str | None = None):
    cloned = copy(font)
    cloned.name = XLSX_THAI_FONT
    if size is not None:
        cloned.sz = size
    if bold is not None:
        cloned.bold = bold
    if color is not None:
        cloned.color = color
    return cloned


def _wrapped_alignment(alignment):
    cloned = copy(alignment)
    cloned.wrap_text = True
    if not cloned.vertical:
        cloned.vertical = "top"
    return cloned


def apply_official_thai_cell_style(cell, *, size: int = 14) -> None:
    cell.font = _thai_font(cell.font, size=size)
    cell.alignment = _wrapped_alignment(cell.alignment)


def apply_thai_header_style(cell, *, size: int = 14) -> None:
    cell.font = _thai_font(cell.font, size=size, bold=True)
    cell.alignment = _wrapped_alignment(cell.alignment)


def apply_thai_title_style(cell, *, size: int = 16) -> None:
    cell.font = _thai_font(cell.font, size=size, bold=True)
    cell.alignment = _wrapped_alignment(cell.alignment)


def apply_workbook_thai_style(
    workbook,
    *,
    body_size: int = 14,
    header_rows: Sequence[int] = (1,),
    title_rows: Sequence[int] = (1,),
) -> None:
    """Apply Thai-capable font names and wrapping to all populated cells."""
    for worksheet in workbook.worksheets:
        assert_no_mojibake(worksheet.title, context=f"sheet title {worksheet.title!r}")
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                assert_no_mojibake(cell.value, context=f"{worksheet.title}!{cell.coordinate}")
                if cell.row in title_rows:
                    apply_thai_title_style(cell, size=max(body_size + 2, 16))
                elif cell.row in header_rows or bool(getattr(cell.font, "bold", False)):
                    apply_thai_header_style(cell, size=body_size)
                else:
                    apply_official_thai_cell_style(cell, size=body_size)
        for row_dimension in worksheet.row_dimensions.values():
            if row_dimension.height is None:
                row_dimension.height = 24


def assert_workbook_thai_safe(workbook) -> None:
    for worksheet in workbook.worksheets:
        assert_no_mojibake(worksheet.title, context=f"sheet title {worksheet.title!r}")
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is not None:
                    assert_no_mojibake(cell.value, context=f"{worksheet.title}!{cell.coordinate}")


def workbook_streaming_response(
    workbook,
    filename: str,
    *,
    ascii_fallback: str | None = None,
) -> StreamingResponse:
    assert_workbook_thai_safe(workbook)
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type=XLSX_MIME,
        headers=download_headers(filename, ascii_fallback=ascii_fallback),
    )


def csv_bytes(header: Sequence[object], rows: Iterable[Sequence[object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    text = buffer.getvalue()
    assert_no_mojibake(text, context="csv")
    return text.encode("utf-8-sig")


def csv_streaming_response(
    filename: str,
    header: Sequence[object],
    rows: Iterable[Sequence[object]],
) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(csv_bytes(header, rows)),
        media_type=CSV_MIME,
        headers=download_headers(filename),
    )


def binary_streaming_response(
    data,
    *,
    media_type: str,
    filename: str,
    disposition: str = "attachment",
    ascii_fallback: str | None = None,
) -> StreamingResponse:
    if hasattr(data, "seek"):
        data.seek(0)
        stream = data
    else:
        stream = io.BytesIO(data)
    return StreamingResponse(
        stream,
        media_type=media_type,
        headers=download_headers(filename, disposition=disposition, ascii_fallback=ascii_fallback),
    )


@dataclass(frozen=True)
class ThaiPdfFontRegistration:
    normal_name: str
    bold_name: str
    normal_path: str | None
    bold_path: str | None
    embedded: bool


def _font_candidates() -> list[tuple[str, str | None]]:
    windows = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    return [
        (str(windows / "THSarabunNew.ttf"), str(windows / "THSarabunNew Bold.ttf")),
        (str(windows / "Sarabun-Regular.ttf"), str(windows / "Sarabun-Bold.ttf")),
        (str(windows / "NotoSansThai-Regular.ttf"), str(windows / "NotoSansThai-Bold.ttf")),
        ("/usr/share/fonts/truetype/tlwg/THSarabunNew.ttf", "/usr/share/fonts/truetype/tlwg/THSarabunNew-Bold.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf", "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf"),
        ("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"),
    ]


def register_reportlab_thai_fonts(prefix: str = "EMS-Thai") -> ThaiPdfFontRegistration:
    """Register available local Thai-capable ReportLab fonts.

    No font binaries are bundled. If no local candidate exists, callers receive
    Helvetica as a fallback with embedded=False.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        return ThaiPdfFontRegistration("Helvetica", "Helvetica-Bold", None, None, False)

    for normal_path, bold_path in _font_candidates():
        if not os.path.exists(normal_path):
            continue
        normal_name = f"{prefix}-Regular"
        bold_name = f"{prefix}-Bold"
        try:
            pdfmetrics.registerFont(TTFont(normal_name, normal_path))
            if bold_path and os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            else:
                bold_name = normal_name
                bold_path = normal_path
            return ThaiPdfFontRegistration(normal_name, bold_name, normal_path, bold_path, True)
        except Exception:
            continue
    return ThaiPdfFontRegistration("Helvetica", "Helvetica-Bold", None, None, False)
