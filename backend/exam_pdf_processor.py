"""
exam_pdf_processor.py — ประมวลผล PDF ข้อสอบ

ฟังก์ชันหลัก:
  stamp_exam_header(pdf_bytes, student_order, total_pages_in_set)
    → PDF ที่มี header บนทุกหน้า:
      "ชื่อ........  นามสกุล........  รหัสนักศึกษา........  ลำดับที่ N  หน้า X/Y"

  build_full_exam_set(exam_pdf_bytes, cover_page_bytes, num_students,
                       room_capacity, student_list, buffer_pct)
    → {
        "preview_pdf":   bytes,   # ตัวอย่างให้อาจารย์ตรวจ (1 ชุด พร้อม header + ใบปะหน้า)
        "page_count":    int,     # หน้ารวม (ข้อสอบ + ใบปะหน้า 2 ใบ)
        "print_sets":    int,     # จำนวนชุดสั่งพิมพ์ (รวม buffer)
        "print_sheets":  int,     # หน้ารวมทั้งหมด (print_sets × page_count)
        "room_splits":   list,    # [{room, start_order, end_order, count}]
      }

  split_students_by_room(students_sorted, room_capacities)
    → จัดนักศึกษาเข้าห้อง ห้องแรก = ลำดับต้น (ตามความจุ)
"""

import io, math
from typing import List, Optional
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas

from services.thai_export_service import register_reportlab_thai_fonts

# ── Font setup ────────────────────────────────────────────────
_FONT_REGISTERED = False
_FONT_NAME = "Helvetica"

def _ensure_font():
    global _FONT_REGISTERED, _FONT_NAME
    if _FONT_REGISTERED:
        return
    registration = register_reportlab_thai_fonts("EMS-Exam-Thai")
    _FONT_NAME = registration.normal_name
    _FONT_REGISTERED = True


# ── Header overlay ─────────────────────────────────────────────
def _make_header_overlay(
    width: float,
    height: float,
    student_order: int,
    page_num: int,
    total_pages: int,
    header_height: float = 26.0,
) -> bytes:
    """สร้าง PDF 1 หน้าที่มีแค่ header bar — ไว้ merge_page ทับ"""
    _ensure_font()
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(width, height))

    y_top = height

    # พื้น header ขาว (ทับ content เดิม)
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, y_top - header_height, width, header_height, fill=1, stroke=0)

    # เส้นขอบล่าง header
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.line(0, y_top - header_height, width, y_top - header_height)

    # ข้อความ
    c.setFillColorRGB(0, 0, 0)
    c.setFont(_FONT_NAME, 9)

    text = (
        f"ชื่อ.......................................  "
        f"นามสกุล.......................................  "
        f"รหัสนักศึกษา.............................  "
        f"ลำดับที่ {student_order}    "
        f"หน้า {page_num}/{total_pages}"
    )
    c.drawString(8, y_top - header_height + 7, text)
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ── stamp_exam_header ──────────────────────────────────────────
def stamp_exam_header(
    pdf_bytes: bytes,
    student_order: int,
) -> bytes:
    """
    ใส่ header บนทุกหน้าของ PDF ข้อสอบ
    header: ชื่อ... นามสกุล... รหัส... ลำดับที่ N  หน้า X/Y
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total  = len(reader.pages)

    for i, page in enumerate(reader.pages):
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        overlay_bytes = _make_header_overlay(w, h, student_order, i + 1, total)
        overlay_page  = PdfReader(io.BytesIO(overlay_bytes)).pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# ── split_students_by_room ─────────────────────────────────────
def split_students_by_room(
    students_sorted: List[dict],   # เรียงตามรหัสนักศึกษา น้อย→มาก แล้ว
    room_capacities: List[dict],   # [{"room_name": str, "capacity": int}, ...]
) -> List[dict]:
    """
    จัดนักศึกษาเข้าห้อง
    - ห้องแรก = ลำดับ 1..cap1
    - ห้องสอง = ลำดับ cap1+1..cap1+cap2
    - ...
    return: [{"room_name": str, "students": [...], "start_order": int, "end_order": int}]
    """
    result = []
    idx = 0
    for room in room_capacities:
        cap = room["capacity"]
        chunk = students_sorted[idx: idx + cap]
        if not chunk:
            break
        result.append({
            "room_name":   room["room_name"],
            "capacity":    cap,
            "students":    chunk,
            "start_order": idx + 1,
            "end_order":   idx + len(chunk),
            "count":       len(chunk),
        })
        idx += len(chunk)
        if idx >= len(students_sorted):
            break
    return result


# ── merge_with_cover ───────────────────────────────────────────
def merge_exam_with_cover(
    stamped_exam_bytes: bytes,
    cover_page_bytes: bytes,          # PDF ของใบปะหน้า (2 หน้า)
) -> bytes:
    """
    รวม: ใบปะหน้า(2หน้า) + ข้อสอบ(พร้อม header)
    → 1 PDF พร้อมส่งพิมพ์
    """
    writer = PdfWriter()

    # ใบปะหน้า 2 หน้าก่อน
    for page in PdfReader(io.BytesIO(cover_page_bytes)).pages:
        writer.add_page(page)

    # ข้อสอบที่ stamp แล้ว
    for page in PdfReader(io.BytesIO(stamped_exam_bytes)).pages:
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# ── build_full_exam_set ────────────────────────────────────────
def build_full_exam_set(
    exam_pdf_bytes: bytes,
    cover_page_bytes: bytes,
    students_sorted: List[dict],     # เรียง รหัสน้อย→มาก
    room_capacities: List[dict],     # [{"room_name":..., "capacity":...}]
    buffer_pct: float = 5.0,         # % สำรอง
) -> dict:
    """
    สร้างข้อมูลสำหรับสั่งพิมพ์ทั้งหมด

    return: {
      "preview_pdf":   bytes   # 1 ชุดตัวอย่าง (ลำดับที่ 1) พร้อม header + ใบปะหน้า
      "exam_pages":    int     # หน้าข้อสอบ (ไม่รวมปะหน้า)
      "cover_pages":   int     # หน้าใบปะหน้า (= 2)
      "total_pages":   int     # หน้ารวมต่อชุด (exam + cover)
      "num_students":  int
      "buffer_sets":   int     # จำนวนชุดสำรอง
      "print_sets":    int     # ชุดทั้งหมดที่ต้องพิมพ์
      "print_sheets":  int     # หน้าทั้งหมด (print_sets × total_pages)
      "room_splits":   list    # การแบ่งห้อง
    }
    """
    # นับหน้า
    exam_pages  = len(PdfReader(io.BytesIO(exam_pdf_bytes)).pages)
    cover_pages = len(PdfReader(io.BytesIO(cover_page_bytes)).pages)
    total_pages = exam_pages + cover_pages

    # แบ่งห้อง
    room_splits = split_students_by_room(students_sorted, room_capacities)
    num_students = len(students_sorted)

    # คำนวณ buffer
    buffer_sets = math.ceil(num_students * buffer_pct / 100)
    print_sets  = num_students + buffer_sets
    print_sheets = print_sets * total_pages

    # Preview: stamp ลำดับที่ 1 แล้วรวมกับใบปะหน้า
    stamped_preview = stamp_exam_header(exam_pdf_bytes, student_order=1)
    preview_pdf     = merge_exam_with_cover(stamped_preview, cover_page_bytes)

    return {
        "preview_pdf":  preview_pdf,
        "exam_pages":   exam_pages,
        "cover_pages":  cover_pages,
        "total_pages":  total_pages,
        "num_students": num_students,
        "buffer_pct":   buffer_pct,
        "buffer_sets":  buffer_sets,
        "print_sets":   print_sets,
        "print_sheets": print_sheets,
        "room_splits":  room_splits,
    }


# ── CLI test ───────────────────────────────────────────────────
if __name__ == "__main__":
    from reportlab.lib.pagesizes import A4

    # สร้าง sample exam PDF 3 หน้า
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    for i in range(3):
        c.setFont("Helvetica", 14)
        c.drawString(100, 700, f"Exam Content — Page {i+1}")
        c.drawString(100, 680, "1. คำถาม: .............................................")
        c.showPage()
    c.save()
    exam_bytes = buf.getvalue()

    # สร้าง sample cover PDF 2 หน้า
    buf2 = io.BytesIO()
    c2 = rl_canvas.Canvas(buf2, pagesize=A4)
    for i in range(2):
        c2.drawString(100, 700, f"Cover Page {i+1} — คณะรัฐศาสตร์ฯ")
        c2.showPage()
    c2.save()
    cover_bytes = buf2.getvalue()

    students = [
        {"student_id": f"6819100{i:02d}", "student_name": f"นักศึกษา {i}"}
        for i in range(1, 84)
    ]
    # เรียงรหัสน้อย→มาก
    students_sorted = sorted(students, key=lambda s: s["student_id"])

    rooms = [
        {"room_name": "PSB 1101", "capacity": 60},
        {"room_name": "PSB 1204", "capacity": 40},
    ]

    result = build_full_exam_set(
        exam_pdf_bytes  = exam_bytes,
        cover_page_bytes= cover_bytes,
        students_sorted = students_sorted,
        room_capacities = rooms,
        buffer_pct      = 5.0,
    )

    print(f"✅ exam_pages:   {result['exam_pages']}")
    print(f"✅ cover_pages:  {result['cover_pages']}")
    print(f"✅ total_pages:  {result['total_pages']} หน้าต่อชุด")
    print(f"✅ num_students: {result['num_students']}")
    print(f"✅ buffer_sets:  {result['buffer_sets']} ชุด (+{result['buffer_pct']}%)")
    print(f"✅ print_sets:   {result['print_sets']} ชุด")
    print(f"✅ print_sheets: {result['print_sheets']} หน้ารวม")
    print()
    for r in result["room_splits"]:
        print(f"   ห้อง {r['room_name']}: ลำดับ {r['start_order']}–{r['end_order']} ({r['count']} คน)")

    with open("/home/claude/doc_output/preview_exam.pdf", "wb") as f:
        f.write(result["preview_pdf"])
    print(f"\n✅ Preview PDF saved ({len(result['preview_pdf'])} bytes)")
