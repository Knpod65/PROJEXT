"""
import_service.py — orchestration for import operations.

Owns:
- import_opencourse orchestration
- import_enrollment orchestration
- session management coordination
- delegates to import_v2 pipeline for parsing
"""
from typing import Optional
from sqlalchemy.orm import Session
import models
from repositories.import_repository import ImportRepository
from validators.import_validator import ImportValidator
from serializers.import_serializer import (
    serialize_session_audit,
    serialize_import_result,
    serialize_enrollment_result,
    serialize_session_summary,
)
from datetime import datetime, timezone
import pandas as pd
import io
import re


def _parse_thai_date(val) -> Optional[str]:
    """แปลง '23 MAR 2026' → '2026-03-23'"""
    if not val or pd.isna(val):
        return None
    MONTHS = {
        "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
        "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
        "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    }
    s = str(val).strip().upper()
    m = re.match(r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})", s)
    if not m:
        return None
    d, mon, y = m.group(1).zfill(2), MONTHS.get(m.group(2)), m.group(3)
    return f"{y}-{mon}-{d}" if mon else None


def _read_uploaded_file(upload) -> pd.DataFrame:
    """อ่านไฟล์ .xls หรือ .xlsx หรือ .csv"""
    content = upload.file.read()
    fname = upload.filename.lower()

    if fname.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")

    try:
        return pd.read_excel(io.BytesIO(content), engine="openpyxl")
    except Exception:
        pass

    try:
        return pd.read_excel(io.BytesIO(content), engine="xlrd")
    except Exception:
        pass

    try:
        tables = pd.read_html(io.BytesIO(content), encoding="utf-8")
        if tables:
            return tables[0]
    except Exception:
        pass

    from fastapi import HTTPException
    raise HTTPException(400, "ไม่สามารถอ่านไฟล์ได้ — รองรับ .xls .xlsx .csv")


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.upper()
    return df


class ImportService:
    """Orchestration for import operations."""

    @staticmethod
    def import_opencourse(
        db: Session,
        file,
        academic_year: str,
        semester: str,
        exam_type: str,
        current_user,
        request,
    ):
        """Import opencourse data."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import log_action

        ImportValidator.validate_exam_type(exam_type)
        ImportValidator.validate_semester(semester)
        require_period_editable_for_values(db, academic_year, semester, exam_type)

        df = _read_uploaded_file(file)
        df = _normalize_cols(df)
        ImportValidator.validate_opencourse_columns(df)

        df.rename(columns={"COURESNO": "COURSENO"}, inplace=True, errors="ignore")

        sess = ImportRepository.get_or_create_session(
            db, academic_year, semester, exam_type, current_user.id
        )

        exam_type_enum = models.ExamType.midterm if exam_type == "midterm" else models.ExamType.final
        stats = {"courses_new": 0, "sections_new": 0, "sections_updated": 0, "skipped": 0}

        for _, row in df.iterrows():
            course_id_str = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
            sec_no = str(int(row["SECLEC"])) if pd.notna(row.get("SECLEC")) else None
            if not course_id_str or not sec_no:
                stats["skipped"] += 1
                continue

            title = str(row.get("TITLE", "")).strip()
            lecturer = str(row.get("LECTURER", "")).strip()
            num_stu = int(row["REGIST"]) if pd.notna(row.get("REGIST")) else 0
            max_cap = int(row["MAX"]) if pd.notna(row.get("MAX")) else 0
            room_name = str(row.get("ROOM", "")).strip()
            level = str(row.get("LEVEL", "Undergraduate")).strip()
            credits = int(row["CRELEC"]) if pd.notna(row.get("CRELEC")) else 3

            if exam_type == "midterm":
                exam_date = _parse_thai_date(row.get("MID_DAY"))
                exam_time = str(row.get("MID_TIME", "")).strip()
            else:
                exam_date = _parse_thai_date(row.get("FIN_DAY"))
                exam_time = str(row.get("FIN_TIME", "")).strip()

            course = db.query(models.Course).filter(
                models.Course.course_id == course_id_str
            ).first()
            if not course:
                course = models.Course(
                    course_id=course_id_str,
                    course_name_th=title,
                    course_name_en=title,
                    credits=credits,
                    department="คณะรัฐศาสตร์ฯ",
                )
                db.add(course)
                db.flush()
                stats["courses_new"] += 1

            section = db.query(models.Section).filter(
                and_(
                    models.Section.course_id == course.id,
                    models.Section.section_no == sec_no,
                    models.Section.semester == semester,
                    models.Section.academic_year == academic_year,
                )
            ).first()

            if not section:
                section = models.Section(
                    course_id=course.id,
                    section_no=sec_no,
                    num_students=num_stu,
                    semester=semester,
                    academic_year=academic_year,
                    import_session_id=sess.id,
                )
                db.add(section)
                db.flush()
                stats["sections_new"] += 1
            else:
                section.num_students = num_stu
                section.import_session_id = sess.id
                stats["sections_updated"] += 1

            room = None
            if room_name:
                room = db.query(models.Room).filter(
                    models.Room.room_name == room_name
                ).first()
                if not room:
                    room = models.Room(
                        room_name=room_name,
                        building=room_name.split()[0] if " " in room_name else room_name,
                        capacity=max_cap,
                    )
                    db.add(room)
                    db.flush()

            if exam_date:
                sched = db.query(models.ExamSchedule).filter(
                    and_(
                        models.ExamSchedule.section_id == section.id,
                        models.ExamSchedule.exam_type == exam_type_enum,
                    )
                ).first()
                if not sched:
                    sched = models.ExamSchedule(
                        section_id=section.id,
                        room_id=room.id if room else None,
                        exam_date=exam_date,
                        exam_time=exam_time,
                        exam_type=exam_type_enum,
                        status=models.ScheduleStatus.draft,
                        num_pages=0,
                        total_sheets=0,
                    )
                    db.add(sched)
                else:
                    sched.exam_date = exam_date
                    sched.exam_time = exam_time
                    if room:
                        sched.room_id = room.id

            if lecturer:
                teacher = db.query(models.User).filter(
                    models.User.role == models.UserRole.teacher,
                    models.User.full_name.ilike(f"%{lecturer.split()[-1]}%")
                ).first()
                if teacher and not section.teacher_id:
                    section.teacher_id = teacher.id

        db.commit()

        sess.opencourse_rows = len(df)
        sess.last_updated = datetime.now(timezone.utc)
        db.commit()

        try:
            log_action(db, current_user, "IMPORT_COMMIT_OPENCOURSE", "import_sessions",
                       record_id=sess.id,
                       new_values={"import_type": "opencourse",
                                   "academic_year": academic_year,
                                   "semester": semester,
                                   "exam_type": exam_type,
                                   "source_filename": file.filename,
                                   "row_count": len(df)},
                       request=request)
        except Exception:
            pass

        return serialize_import_result(sess.id, academic_year, semester, exam_type, len(df), stats)

    @staticmethod
    def import_enrollment(
        db: Session,
        file,
        academic_year: str,
        semester: str,
        exam_type: str,
        current_user,
        request,
        dry_run: bool = False,
    ):
        """Import enrollment data."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import log_action
        from collections import Counter

        ImportValidator.validate_exam_type(exam_type)
        ImportValidator.validate_semester(semester)
        require_period_editable_for_values(db, academic_year, semester, exam_type)

        content = file.file.read()
        fname = file.filename.lower()

        try:
            if fname.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
            else:
                df = pd.read_excel(io.BytesIO(content), engine="xlrd", sheet_name="regist_student_faculty")
        except Exception:
            try:
                df = pd.read_excel(io.BytesIO(content), engine="xlrd")
            except Exception as e:
                from fastapi import HTTPException
                raise HTTPException(400, f"อ่านไฟล์ไม่ได้: {e}")

        df = _normalize_cols(df)
        ImportValidator.validate_enrollment_columns(df)

        sess = ImportRepository.get_or_create_session(
            db, academic_year, semester, exam_type, current_user.id
        )

        if "SEMESTER" in df.columns and "YEAR" in df.columns:
            df = df[
                (df["SEMESTER"].astype(str) == semester) &
                (df["YEAR"].astype(str) == academic_year)
            ]

        grouped = df.groupby(["COURSENO", "SECLEC"])["ID"].count().reset_index()
        grouped.columns = ["COURSENO", "SECLEC", "COUNT"]

        stats = {
            "total_rows": len(df),
            "unique_students": df["ID"].nunique(),
            "sections_updated": 0,
            "records_added": 0,
            "skipped": 0,
        }

        course_map = {c.course_id: c.id for c in db.query(models.Course).all()}
        section_map = {
            (s.course_id, s.section_no): s.id
            for s in db.query(models.Section).filter(
                and_(
                    models.Section.semester == semester,
                    models.Section.academic_year == academic_year,
                )
            ).all()
        }

        records_to_insert = []
        for _, g in grouped.iterrows():
            course_id_str = str(int(g["COURSENO"]))
            sec_no = str(int(g["SECLEC"]))
            count = int(g["COUNT"])

            course_pk = course_map.get(course_id_str)
            if not course_pk:
                stats["skipped"] += 1
                continue
            section_pk = section_map.get((course_pk, sec_no))
            if not section_pk:
                stats["skipped"] += 1
                continue

            section = db.query(models.Section).filter(models.Section.id == section_pk).first()
            if section:
                section.num_students = count
                stats["sections_updated"] += 1

            if section and section.exam_schedule and section.exam_schedule.num_pages:
                sched = section.exam_schedule
                sched.total_sheets = count * sched.num_pages

        for _, row in df.iterrows():
            course_id_str = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
            sec_no = str(int(row["SECLEC"])) if pd.notna(row.get("SECLEC")) else None
            student_id = str(row["ID"]).strip() if pd.notna(row.get("ID")) else None
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
                "section_id": section_pk,
                "student_id": student_id,
                "student_name": f"{str(row.get('NAME','')).strip()} {str(row.get('SNAME','')).strip()}".strip(),
                "major": str(row.get("MAJOR", "")).strip(),
                "faculty_name": str(row.get("FAC_NAME", "")).strip(),
                "type_regist": str(row.get("TYPE_REGIST", "")).strip(),
            })

        skipped = []
        for _, row in df.iterrows():
            cid = str(int(row["COURSENO"])) if pd.notna(row.get("COURSENO")) else None
            sec = str(int(row["SECLEC"])) if pd.notna(row.get("SECLEC")) else None
            sid = str(row["ID"]).strip() if pd.notna(row.get("ID")) else None
            if not all([cid, sec, sid]):
                skipped.append({"row": int(row.name), "reason": "ข้อมูลไม่ครบ (COURSENO/SECLEC/ID)"})
                continue
            if cid not in course_map:
                skipped.append({"row": int(row.name), "reason": f"ไม่พบรหัสวิชา {cid} ในระบบ"})
                continue
            if (course_map[cid], sec) not in section_map:
                skipped.append({"row": int(row.name), "reason": f"ไม่พบ {cid} ตอน {sec} ในเทอมนี้"})

        try:
            if records_to_insert:
                db.bulk_insert_mappings(models.EnrollmentRecord, records_to_insert)

            section_counts = Counter(r["section_id"] for r in records_to_insert)
            for sec_id, count in section_counts.items():
                db.query(models.Section).filter(models.Section.id == sec_id).update({"num_students": count})

            if dry_run:
                db.rollback()
                stats["dry_run"] = True
                stats["records_added"] = len(records_to_insert)
                stats["skipped_count"] = len(skipped)
                return serialize_enrollment_result(sess.id, academic_year, semester, exam_type, stats)

            db.commit()
            stats["records_added"] = len(records_to_insert)
            stats["skipped_count"] = len(skipped)
            stats["skipped_rows"] = skipped[:50]
            stats["sections_updated"] = len(section_counts)

        except Exception as e:
            db.rollback()
            from fastapi import HTTPException
            raise HTTPException(500, f"Import ล้มเหลว ข้อมูลถูก rollback ทั้งหมด: {str(e)}")

        sess.enrollment_rows = len(df)
        sess.last_updated = datetime.now(timezone.utc)
        db.commit()

        try:
            log_action(db, current_user, "IMPORT_COMMIT_ENROLLMENT", "import_sessions",
                       record_id=sess.id,
                       new_values={"import_type": "enrollment",
                                   "academic_year": academic_year,
                                   "semester": semester,
                                   "exam_type": exam_type,
                                   "source_filename": file.filename,
                                   "row_count": len(df),
                                   "records_added": stats.get("records_added")},
                       request=request)
        except Exception:
            pass

        return serialize_enrollment_result(sess.id, academic_year, semester, exam_type, stats)