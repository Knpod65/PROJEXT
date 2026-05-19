"""
Import Router — นำเข้าข้อมูลจากไฟล์ทะเบียน มช.
  POST /api/import/opencourse   — วิชาที่เปิด + อาจารย์ + ตารางสอบ (opencourse.xls)
  POST /api/import/enrollment   — รายชื่อนักศึกษาที่ลงทะเบียน (Book1.xls)
  GET  /api/import/sessions     — รายการ session ที่ import แล้ว
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import models
from auth_utils import require_admin
from services.import_service import ImportService
from serializers.import_serializer import serialize_session_audit
from sqlalchemy import and_, func, case

router = APIRouter()


def _detect_import_type(session: models.ImportSession) -> str:
    if (session.opencourse_rows or 0) > 0 and (session.enrollment_rows or 0) > 0:
        return "mixed"
    if (session.opencourse_rows or 0) > 0:
        return "opencourse"
    if (session.enrollment_rows or 0) > 0:
        return "enrollment"
    return "personnel_or_employee"


def _build_session_audit_payload(
    session: models.ImportSession,
    user_lookup: dict[int, str],
    counts: dict[str, int],
) -> dict:
    return serialize_session_audit(session, user_lookup, counts)


# ═══════════════════════════════════════════════════════════════
# POST /api/import/opencourse
# ═══════════════════════════════════════════════════════════════

@router.post("/opencourse")
async def import_opencourse(
    file:          UploadFile = File(..., description="opencourse.xls จากระบบทะเบียน"),
    academic_year: str  = Form(..., description="ปีการศึกษา เช่น 2568"),
    semester:      str  = Form(..., description="ภาคเรียน: 1 หรือ 2"),
    exam_type:     str  = Form(..., description="ประเภทสอบ: midterm หรือ final"),
    db:            Session = Depends(get_db),
    current_user:  models.User = Depends(require_admin),
    request:       Request = None,
):
    return ImportService.import_opencourse(
        db=db, file=file, academic_year=academic_year, semester=semester,
        exam_type=exam_type, current_user=current_user, request=request
    )


# ═══════════════════════════════════════════════════════════════
# POST /api/import/enrollment
# ═══════════════════════════════════════════════════════════════

@router.post("/enrollment")
async def import_enrollment(
    dry_run: bool = Form(False),
    file:          UploadFile = File(..., description="Book1.xls — รายชื่อนักศึกษาที่ลงทะเบียน"),
    academic_year: str  = Form(..., description="ปีการศึกษา เช่น 2568"),
    semester:      str  = Form(..., description="ภาคเรียน: 1 หรือ 2"),
    exam_type:     str  = Form(..., description="ประเภทสอบ: midterm หรือ final"),
    db:            Session = Depends(get_db),
    current_user:  models.User = Depends(require_admin),
    request:       Request = None,
):
    return ImportService.import_enrollment(
        db=db, file=file, academic_year=academic_year, semester=semester,
        exam_type=exam_type, current_user=current_user, request=request, dry_run=dry_run
    )


# ═══════════════════════════════════════════════════════════════
# GET /api/import/sessions
# ═══════════════════════════════════════════════════════════════

@router.get("/sessions")
def list_import_sessions(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sessions = db.query(models.ImportSession).order_by(
        models.ImportSession.created_at.desc()
    ).all()

    if not sessions:
        return []

    session_ids = [s.id for s in sessions]
    creator_ids = list({s.created_by for s in sessions if s.created_by is not None})

    user_lookup = {
        u.id: (u.full_name or u.username or "unknown")
        for u in db.query(models.User).filter(models.User.id.in_(creator_ids)).all()
    } if creator_ids else {}

    grouped_rows = db.query(
        models.ImportRowLog.session_id,
        models.ImportRowLog.status,
        func.count(models.ImportRowLog.id),
    ).filter(
        models.ImportRowLog.session_id.in_(session_ids)
    ).group_by(
        models.ImportRowLog.session_id,
        models.ImportRowLog.status,
    ).all()

    grouped_selected_imported = db.query(
        models.ImportRowLog.session_id,
        func.sum(case((models.ImportRowLog.was_imported == True, 1), else_=0)),
        func.sum(case((models.ImportRowLog.was_imported == False, 1), else_=0)),
    ).filter(
        models.ImportRowLog.session_id.in_(session_ids)
    ).group_by(
        models.ImportRowLog.session_id,
    ).all()

    count_map: dict[int, dict[str, int]] = {sid: {
        "total_rows": 0,
        "valid_rows": 0,
        "warning_rows": 0,
        "error_rows": 0,
        "imported_rows": 0,
        "skipped_rows": 0,
    } for sid in session_ids}

    for session_id, status, count in grouped_rows:
        stats = count_map.setdefault(session_id, {
            "total_rows": 0,
            "valid_rows": 0,
            "warning_rows": 0,
            "error_rows": 0,
            "imported_rows": 0,
            "skipped_rows": 0,
        })
        stats["total_rows"] += int(count or 0)
        if status == "valid":
            stats["valid_rows"] += int(count or 0)
        elif status == "warning":
            stats["warning_rows"] += int(count or 0)
        elif status == "error":
            stats["error_rows"] += int(count or 0)

    for session_id, imported_count, skipped_count in grouped_selected_imported:
        stats = count_map.setdefault(session_id, {
            "total_rows": 0,
            "valid_rows": 0,
            "warning_rows": 0,
            "error_rows": 0,
            "imported_rows": 0,
            "skipped_rows": 0,
        })
        stats["imported_rows"] = int(imported_count or 0)
        stats["skipped_rows"] = int(skipped_count or 0)

    return [
        _build_session_audit_payload(s, user_lookup, count_map.get(s.id, {}))
        for s in sessions
    ]


@router.get("/sessions/{session_id}/audit")
def session_audit_detail(
    session_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sess = db.query(models.ImportSession).filter(models.ImportSession.id == session_id).first()
    if not sess:
        raise HTTPException(404, "ไม่พบ session")

    creator = None
    if sess.created_by:
        creator = db.query(models.User).filter(models.User.id == sess.created_by).first()

    user_lookup = {
        sess.created_by: (creator.full_name or creator.username) if creator else "unknown"
    } if sess.created_by else {}

    grouped_rows = db.query(
        models.ImportRowLog.status,
        func.count(models.ImportRowLog.id),
    ).filter(
        models.ImportRowLog.session_id == session_id
    ).group_by(
        models.ImportRowLog.status,
    ).all()

    imported_skipped = db.query(
        func.sum(case((models.ImportRowLog.was_imported == True, 1), else_=0)),
        func.sum(case((models.ImportRowLog.was_imported == False, 1), else_=0)),
    ).filter(
        models.ImportRowLog.session_id == session_id
    ).first()

    issue_rows = db.query(
        models.ImportRowLog.error_code,
        models.ImportRowLog.error_message,
        func.count(models.ImportRowLog.id),
    ).filter(
        models.ImportRowLog.session_id == session_id,
        models.ImportRowLog.error_code.isnot(None),
    ).group_by(
        models.ImportRowLog.error_code,
        models.ImportRowLog.error_message,
    ).order_by(
        func.count(models.ImportRowLog.id).desc(),
        models.ImportRowLog.error_code.asc(),
    ).all()

    counts = {
        "total_rows": 0,
        "valid_rows": 0,
        "warning_rows": 0,
        "error_rows": 0,
        "imported_rows": int((imported_skipped[0] if imported_skipped else 0) or 0),
        "skipped_rows": int((imported_skipped[1] if imported_skipped else 0) or 0),
    }

    for status, count in grouped_rows:
        c = int(count or 0)
        counts["total_rows"] += c
        if status == "valid":
            counts["valid_rows"] += c
        elif status == "warning":
            counts["warning_rows"] += c
        elif status == "error":
            counts["error_rows"] += c

    return {
        "session": _build_session_audit_payload(sess, user_lookup, counts),
        "issue_summary": [
            {
                "code": code,
                "message": message,
                "count": int(count or 0),
            }
            for code, message, count in issue_rows
        ],
    }


@router.get("/sessions/{session_id}/rows")
def session_row_logs(
    session_id: int,
    status: Optional[str] = Query(default=None),
    error_code: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sess = db.query(models.ImportSession).filter(models.ImportSession.id == session_id).first()
    if not sess:
        raise HTTPException(404, "ไม่พบ session")

    query = db.query(models.ImportRowLog).filter(models.ImportRowLog.session_id == session_id)

    if status:
        query = query.filter(models.ImportRowLog.status == status)
    if error_code:
        query = query.filter(models.ImportRowLog.error_code == error_code)

    row_logs = query.order_by(models.ImportRowLog.row_number.asc()).all()

    keyword = (q or "").strip().lower()
    rows = []
    for row in row_logs:
        raw_data = row.raw_data or {}
        raw_values_text = " ".join(str(value) for value in raw_data.values()).lower() if isinstance(raw_data, dict) else str(raw_data).lower()

        if keyword:
            row_number_text = str(row.row_number)
            searchable = " ".join([
                row_number_text,
                str(row.error_code or ""),
                str(row.error_message or ""),
                raw_values_text,
            ]).lower()
            if keyword not in searchable:
                continue

        rows.append({
            "id": row.id,
            "row_number": row.row_number,
            "status": row.status,
            "error_code": row.error_code,
            "error_message": row.error_message,
            "was_selected": bool(row.was_selected),
            "was_imported": bool(row.was_imported),
            "override_reason": row.override_reason,
            "raw_data": raw_data,
            "raw_data_preview": raw_values_text[:280],
            "created_at": row.created_at.isoformat() if row.created_at else None,
        })

    return {
        "session_id": session_id,
        "total_rows": len(rows),
        "rows": rows,
    }


@router.get("/sessions/{session_id}/summary")
def session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sess = db.query(models.ImportSession).filter(
        models.ImportSession.id == session_id
    ).first()
    if not sess:
        raise HTTPException(404, "ไม่พบ session")

    sections = db.query(models.Section).filter(
        and_(
            models.Section.semester      == sess.semester,
            models.Section.academic_year == sess.academic_year,
        )
    ).all()

    total_students = sum(s.num_students or 0 for s in sections)

    return {
        "session":        {"id": sess.id, "academic_year": sess.academic_year,
                           "semester": sess.semester, "exam_type": sess.exam_type},
        "total_sections": len(sections),
        "total_students": total_students,
        "sections":       [
            {
                "course_id":    s.course.course_id if s.course else None,
                "course_name":  s.course.course_name_th if s.course else None,
                "section_no":   s.section_no,
                "num_students": s.num_students,
            }
            for s in sections
        ],
    }