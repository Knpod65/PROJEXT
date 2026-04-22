"""
Import Router — นำเข้าข้อมูลจากไฟล์ทะเบียน มช.
  POST /api/import/opencourse   — วิชาที่เปิด + อาจารย์ + ตารางสอบ (opencourse.xls)
  POST /api/import/enrollment   — รายชื่อนักศึกษาที่ลงทะเบียน (Book1.xls)
  GET  /api/import/sessions     — รายการ session ที่ import แล้ว
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, func
from typing import Optional
from database import get_db
import models
from auth_utils import require_admin
from datetime import datetime, timezone
import pandas as pd
import io, re
from term_lifecycle import require_period_editable_for_values

router = APIRouter()


def _detect_import_type(session: models.ImportSession) -> str:
    if (session.opencourse_rows or 0) > 0 and (session.enrollment_rows or 0) > 0:
        return "mixed"
    if (session.opencourse_rows or 0) > 0:
        return "opencourse"
    if (session.enrollment_rows or 0) > 0:
        return "enrollment"
    return "personnel_or_employee"


def _status_from_counts(total_rows: int, imported_rows: int, skipped_rows: int, error_rows: int) -> str:
    if total_rows == 0:
        return "no_logs"
    if imported_rows == 0 and error_rows > 0:
        return "blocked"
    if skipped_rows > 0:
        return "completed_with_skips"
    return "completed"


def _build_session_audit_payload(
    session: models.ImportSession,
    user_lookup: dict[int, str],
    counts: dict[str, int],
) -> dict:
    total_rows = counts.get("total_rows", 0)
    valid_rows = counts.get("valid_rows", 0)
    warning_rows = counts.get("warning_rows", 0)
    error_rows = counts.get("error_rows", 0)
    imported_rows = counts.get("imported_rows", 0)
    skipped_rows = counts.get("skipped_rows", 0)

    return {
        "import_session_id": session.id,
        "id": session.id,
        "import_type": _detect_import_type(session),
        "academic_year": session.academic_year,
        "semester": session.semester,
        "exam_type": session.exam_type,
        "imported_by": user_lookup.get(session.created_by, "unknown"),
        "started_at": session.created_at.isoformat() if session.created_at else None,
        "completed_at": session.last_updated.isoformat() if session.last_updated else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "last_updated": session.last_updated.isoformat() if session.last_updated else None,
        "opencourse_rows": session.opencourse_rows,
        "enrollment_rows": session.enrollment_rows,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "warning_rows": warning_rows,
        "error_rows": error_rows,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
        "status": _status_from_counts(total_rows, imported_rows, skipped_rows, error_rows),
    }


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def parse_thai_date(val) -> Optional[str]:
    """
    แปลง '23 MAR 2026'  → '2026-03-23'
    """
    if not val or pd.isna(val):
        return None
    MONTHS = {
        "JAN":"01","FEB":"02","MAR":"03","APR":"04",
        "MAY":"05","JUN":"06","JUL":"07","AUG":"08",
        "SEP":"09","OCT":"10","NOV":"11","DEC":"12",
    }
    s = str(val).strip().upper()
    m = re.match(r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})", s)
    if not m:
        return None
    d, mon, y = m.group(1).zfill(2), MONTHS.get(m.group(2)), m.group(3)
    if not mon:
        return None
    return f"{y}-{mon}-{d}"


def read_uploaded_file(upload: UploadFile) -> pd.DataFrame:
    """อ่านไฟล์ .xls (HTML export จากทะเบียน) หรือ .xlsx หรือ .csv"""
    content = upload.file.read()
    fname   = upload.filename.lower()

    if fname.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")

    # ลอง openpyxl ก่อน (.xlsx)
    try:
        return pd.read_excel(io.BytesIO(content), engine="openpyxl")
    except Exception:
        pass

    # ลอง xlrd (.xls จริง)
    try:
        return pd.read_excel(io.BytesIO(content), engine="xlrd")
    except Exception:
        pass

    # HTML-disguised-as-xls (ทะเบียน มช. export แบบนี้)
    try:
        tables = pd.read_html(io.BytesIO(content), encoding="utf-8")
        if tables:
            return tables[0]
    except Exception:
        pass

    raise HTTPException(400, "ไม่สามารถอ่านไฟล์ได้ — รองรับ .xls .xlsx .csv")


def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.upper()
    return df


def get_or_create_import_session(
    db: Session,
    academic_year: str,
    semester: str,
    exam_type: str,
    current_user_id: int,
) -> models.ImportSession:
    """หา ImportSession ที่ตรงกัน หรือสร้างใหม่"""
    sess = db.query(models.ImportSession).filter(
        and_(
            models.ImportSession.academic_year == academic_year,
            models.ImportSession.semester      == semester,
            models.ImportSession.exam_type     == exam_type,
        )
    ).first()
    if not sess:
        sess = models.ImportSession(
            academic_year  = academic_year,
            semester       = semester,
            exam_type      = exam_type,
            created_by     = current_user_id,
        )
        db.add(sess)
        db.flush()
    return sess


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
):
    """
    นำเข้าข้อมูลวิชาเปิด + อาจารย์ + วันสอบ จากไฟล์ opencourse.xls

    Columns ที่ใช้:
      COURESNO, TITLE, SECLEC, ROOM, LECTURER, MAX, REGIST,
      MID_DAY, MID_TIME, FIN_DAY, FIN_TIME, SEMESTER, YEAR, LEVEL
    """
    if exam_type not in ("midterm", "final"):
        raise HTTPException(400, "exam_type ต้องเป็น 'midterm' หรือ 'final'")
    if semester not in ("1", "2"):
        raise HTTPException(400, "semester ต้องเป็น '1' หรือ '2'")

    require_period_editable_for_values(db, academic_year, semester, exam_type)

    df = read_uploaded_file(file)
    df = normalize_cols(df)

    required = {"COURESNO", "SECLEC", "LECTURER", "REGIST"}
    missing  = required - set(df.columns)
    if missing:
        raise HTTPException(400, f"ไฟล์ขาด columns: {missing}")

    # rename ให้ตรงกัน (COURESNO มีตัวสะกดผิดในไฟล์จริง)
    df.rename(columns={"COURESNO": "COURSENO"}, inplace=True, errors="ignore")

    sess = get_or_create_import_session(
        db, academic_year, semester, exam_type, current_user.id
    )

    exam_type_enum = models.ExamType.midterm if exam_type == "midterm" else models.ExamType.final

    stats = {"courses_new": 0, "sections_new": 0, "sections_updated": 0, "skipped": 0}

    for _, row in df.iterrows():
        course_id_str = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
        sec_no        = str(int(row["SECLEC"]))   if pd.notna(row.get("SECLEC"))   else None
        if not course_id_str or not sec_no:
            stats["skipped"] += 1
            continue

        title      = str(row.get("TITLE", "")).strip()
        lecturer   = str(row.get("LECTURER", "")).strip()
        num_stu    = int(row["REGIST"]) if pd.notna(row.get("REGIST")) else 0
        max_cap    = int(row["MAX"])    if pd.notna(row.get("MAX"))    else 0
        room_name  = str(row.get("ROOM", "")).strip()
        level      = str(row.get("LEVEL", "Undergraduate")).strip()
        credits    = int(row["CRELEC"]) if pd.notna(row.get("CRELEC")) else 3

        # วันสอบ
        if exam_type == "midterm":
            exam_date = parse_thai_date(row.get("MID_DAY"))
            exam_time = str(row.get("MID_TIME", "")).strip()
        else:
            exam_date = parse_thai_date(row.get("FIN_DAY"))
            exam_time = str(row.get("FIN_TIME", "")).strip()

        # ── Course ──────────────────────────────────────────
        course = db.query(models.Course).filter(
            models.Course.course_id == course_id_str
        ).first()
        if not course:
            course = models.Course(
                course_id      = course_id_str,
                course_name_th = title,
                course_name_en = title,
                credits        = credits,
                department     = "คณะรัฐศาสตร์ฯ",
            )
            db.add(course)
            db.flush()
            stats["courses_new"] += 1

        # ── Section ─────────────────────────────────────────
        section = db.query(models.Section).filter(
            and_(
                models.Section.course_id     == course.id,
                models.Section.section_no    == sec_no,
                models.Section.semester      == semester,
                models.Section.academic_year == academic_year,
            )
        ).first()

        if not section:
            section = models.Section(
                course_id     = course.id,
                section_no    = sec_no,
                num_students  = num_stu,
                semester      = semester,
                academic_year = academic_year,
                import_session_id = sess.id,
            )
            db.add(section)
            db.flush()
            stats["sections_new"] += 1
        else:
            section.num_students      = num_stu
            section.import_session_id = sess.id
            stats["sections_updated"] += 1

        # ── Room ────────────────────────────────────────────
        room = None
        if room_name:
            room = db.query(models.Room).filter(
                models.Room.room_name == room_name
            ).first()
            if not room:
                room = models.Room(
                    room_name = room_name,
                    building  = room_name.split()[0] if " " in room_name else room_name,
                    capacity  = max_cap,
                )
                db.add(room)
                db.flush()

        # ── ExamSchedule ────────────────────────────────────
        if exam_date:
            sched = db.query(models.ExamSchedule).filter(
                and_(
                    models.ExamSchedule.section_id == section.id,
                    models.ExamSchedule.exam_type  == exam_type_enum,
                )
            ).first()
            if not sched:
                sched = models.ExamSchedule(
                    section_id   = section.id,
                    room_id      = room.id if room else None,
                    exam_date    = exam_date,
                    exam_time    = exam_time,
                    exam_type    = exam_type_enum,
                    status       = models.ScheduleStatus.draft,
                    num_pages    = 0,
                    total_sheets = 0,
                )
                db.add(sched)
            else:
                sched.exam_date = exam_date
                sched.exam_time = exam_time
                if room:
                    sched.room_id = room.id

        # ── Teacher lookup by name ───────────────────────────
        if lecturer:
            teacher = db.query(models.User).filter(
                models.User.role == models.UserRole.teacher,
                models.User.full_name.ilike(f"%{lecturer.split()[-1]}%")
            ).first()
            if teacher and not section.teacher_id:
                section.teacher_id = teacher.id

    db.commit()

    # อัปเดต session stats
    sess.opencourse_rows = len(df)
    sess.last_updated    = datetime.now(timezone.utc)
    db.commit()

    return {
        "status":    "ok",
        "session_id": sess.id,
        "academic_year": academic_year,
        "semester":  semester,
        "exam_type": exam_type,
        "file_rows": len(df),
        "stats":     stats,
    }


# ═══════════════════════════════════════════════════════════════
# POST /api/import/enrollment
# ═══════════════════════════════════════════════════════════════

@router.post("/enrollment")
async def import_enrollment(
    dry_run: bool = Form(False),  # ตรวจสอบเท่านั้น ไม่บันทึก
    file:          UploadFile = File(..., description="Book1.xls — รายชื่อนักศึกษาที่ลงทะเบียน"),
    academic_year: str  = Form(..., description="ปีการศึกษา เช่น 2568"),
    semester:      str  = Form(..., description="ภาคเรียน: 1 หรือ 2"),
    exam_type:     str  = Form(..., description="ประเภทสอบ: midterm หรือ final"),
    db:            Session = Depends(get_db),
    current_user:  models.User = Depends(require_admin),
):
    """
    นำเข้ารายชื่อนักศึกษา จาก regist_student_faculty (Book1.xls)

    Columns: ID, NAME, SNAME, COURSENO, SECLEC, SEMESTER, YEAR, MAJOR, FAC_NAME
    → อัปเดต num_students ต่อ section อัตโนมัติ
    → เก็บ EnrollmentRecord แต่ละคนไว้ด้วย
    """
    if exam_type not in ("midterm", "final"):
        raise HTTPException(400, "exam_type ต้องเป็น 'midterm' หรือ 'final'")

    require_period_editable_for_values(db, academic_year, semester, exam_type)

    content = await file.read()
    fname   = file.filename.lower()

    # อ่านไฟล์
    try:
        if fname.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
        else:
            df = pd.read_excel(io.BytesIO(content), engine="xlrd",
                               sheet_name="regist_student_faculty")
    except Exception:
        try:
            df = pd.read_excel(io.BytesIO(content), engine="xlrd")
        except Exception as e:
            raise HTTPException(400, f"อ่านไฟล์ไม่ได้: {e}")

    df = normalize_cols(df)

    required = {"ID", "COURSENO", "SECLEC"}
    missing  = required - set(df.columns)
    if missing:
        raise HTTPException(400, f"ไฟล์ขาด columns: {missing}")

    sess = get_or_create_import_session(
        db, academic_year, semester, exam_type, current_user.id
    )

    # กรองเฉพาะ semester+year ที่ตรงกัน (ถ้ามี column)
    if "SEMESTER" in df.columns and "YEAR" in df.columns:
        df = df[
            (df["SEMESTER"].astype(str) == semester) &
            (df["YEAR"].astype(str) == academic_year)
        ]

    # ── คำนวณ num_students ต่อ section ─────────────────────
    grouped = df.groupby(["COURSENO", "SECLEC"])["ID"].count().reset_index()
    grouped.columns = ["COURSENO", "SECLEC", "COUNT"]

    stats = {
        "total_rows":       len(df),
        "unique_students":  df["ID"].nunique(),
        "sections_updated": 0,
        "records_added":    0,
        "skipped":          0,
    }

    for _, g in grouped.iterrows():
        course_id_str = str(int(g["COURSENO"]))
        sec_no        = str(int(g["SECLEC"]))
        count         = int(g["COUNT"])

        course = db.query(models.Course).filter(
            models.Course.course_id == course_id_str
        ).first()
        if not course:
            stats["skipped"] += 1
            continue

        section = db.query(models.Section).filter(
            and_(
                models.Section.course_id     == course.id,
                models.Section.section_no    == sec_no,
                models.Section.semester      == semester,
                models.Section.academic_year == academic_year,
            )
        ).first()
        if not section:
            stats["skipped"] += 1
            continue

        section.num_students = count
        stats["sections_updated"] += 1

        # อัปเดต total_sheets ใน ExamSchedule ด้วย
        sched = db.query(models.ExamSchedule).filter(
            models.ExamSchedule.section_id == section.id
        ).first()
        if sched and sched.num_pages:
            sched.total_sheets = count * sched.num_pages

    # ── บันทึก EnrollmentRecord รายคน (bulk insert) ──────────
    # ลบของเก่าของ session นี้ก่อน
    db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.import_session_id == sess.id
    ).delete()
    db.flush()

    # ตรวจ optimize lock ก่อน import
    if not dry_run and hasattr(models, 'OptimizeSession') and hasattr(models, 'ExamPeriod'):
        _ap = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active==True).first()
        if _ap:
            _os = db.query(models.OptimizeSession).filter(
                models.OptimizeSession.exam_period_id == _ap.id
            ).first()
            if _os and _os.status in ("confirmed","swap_open","swap_confirming","locked"):
                raise HTTPException(400,
                    f"ไม่สามารถ import ได้ — ตารางสอบถูก confirm แล้ว ({_os.status})")

    # build course+section lookup map ก่อน — ลด queries จาก N→1
    course_map = {
        c.course_id: c.id
        for c in db.query(models.Course).all()
    }
    section_map = {
        (s.course_id, s.section_no): s.id
        for s in db.query(models.Section).filter(
            and_(
                models.Section.semester      == semester,
                models.Section.academic_year == academic_year,
            )
        ).all()
    }

    records_to_insert = []
    for _, row in df.iterrows():
        course_id_str = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
        sec_no        = str(int(row["SECLEC"]))   if pd.notna(row.get("SECLEC"))   else None
        student_id    = str(row["ID"]).strip()     if pd.notna(row.get("ID"))       else None
        if not all([course_id_str, sec_no, student_id]):
            continue

        course_pk = course_map.get(course_id_str)
        if not course_pk:
            continue
        section_pk = section_map.get((course_pk, sec_no))
        if not section_pk:
            continue

        records_to_insert.append({
            "import_session_id": sess.id,
            "section_id":        section_pk,
            "student_id":        student_id,
            "student_name":      f"{str(row.get('NAME','')).strip()} {str(row.get('SNAME','')).strip()}".strip(),
            "major":             str(row.get("MAJOR", "")).strip(),
            "faculty_name":      str(row.get("FAC_NAME", "")).strip(),
            "type_regist":       str(row.get("TYPE_REGIST", "")).strip(),
        })

    # validation: track skipped rows
    skipped = []
    for _, row in df.iterrows():
        cid = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
        sec = str(int(row["SECLEC"]))   if pd.notna(row.get("SECLEC"))   else None
        sid = str(row["ID"]).strip()    if pd.notna(row.get("ID"))       else None
        if not all([cid, sec, sid]):
            skipped.append({"row": int(row.name), "reason": "ข้อมูลไม่ครบ (COURSENO/SECLEC/ID)"})
            continue
        cpk = course_map.get(cid)
        if not cpk:
            skipped.append({"row": int(row.name), "reason": f"ไม่พบรหัสวิชา {cid} ในระบบ"})
            continue
        spk = section_map.get((cpk, sec))
        if not spk:
            skipped.append({"row": int(row.name), "reason": f"ไม่พบ {cid} ตอน {sec} ในเทอมนี้"})

    # bulk insert ทั้งหมดใน 1 transaction — rollback ถ้า fail
    try:
        if records_to_insert:
            db.bulk_insert_mappings(models.EnrollmentRecord, records_to_insert)

        # sync num_students ของ sections ที่มี enrollment
        from collections import Counter
        section_counts = Counter(r["section_id"] for r in records_to_insert)
        for sec_id, count in section_counts.items():
            db.query(models.Section).filter(
                models.Section.id == sec_id
            ).update({"num_students": count})

        if dry_run:
            db.rollback()
            stats["dry_run"]      = True
            stats["records_added"] = len(records_to_insert)
            stats["skipped_count"] = len(skipped) if "skipped" in dir() else 0
            return stats
        db.commit()
        stats["records_added"] = len(records_to_insert)
        stats["skipped_count"] = len(skipped)
        stats["skipped_rows"]  = skipped[:50]  # return max 50 skipped rows
        stats["sections_updated"] = len(section_counts)

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Import ล้มเหลว ข้อมูลถูก rollback ทั้งหมด: {str(e)}")

    sess.enrollment_rows = len(df)
    sess.last_updated    = datetime.now(timezone.utc)
    db.commit()

    return {
        "status":      "ok",
        "session_id":  sess.id,
        "academic_year": academic_year,
        "semester":    semester,
        "exam_type":   exam_type,
        "stats":       stats,
    }


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
