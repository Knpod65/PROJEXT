"""
Import Router — นำเข้าข้อมูลจากไฟล์ทะเบียน มช.
  POST /api/import/opencourse   — วิชาที่เปิด + อาจารย์ + ตารางสอบ (opencourse.xls)
  POST /api/import/enrollment   — รายชื่อนักศึกษาที่ลงทะเบียน (Book1.xls)
  GET  /api/import/sessions     — รายการ session ที่ import แล้ว
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from database import get_db
import models
from auth_utils import require_admin
from datetime import datetime, timezone
import pandas as pd
import io, re

router = APIRouter()


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
    return [
        {
            "id":               s.id,
            "academic_year":    s.academic_year,
            "semester":         s.semester,
            "exam_type":        s.exam_type,
            "opencourse_rows":  s.opencourse_rows,
            "enrollment_rows":  s.enrollment_rows,
            "created_at":       s.created_at.isoformat() if s.created_at else None,
            "last_updated":     s.last_updated.isoformat() if s.last_updated else None,
        }
        for s in sessions
    ]


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
