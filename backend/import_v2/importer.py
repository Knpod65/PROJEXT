from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
import re
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

import models
from auth_utils import hash_password
from import_v2.normalizers import (
    clean_whitespace,
    is_placeholder_lecturer,
    normalize_person_name,
    normalize_room_code,
    room_building_from_code,
)


COURSE_KEYS = ("COURSENO", "COURESNO", "COURSE CODE", "COURSE NO", "COURSE")
SECTION_KEYS = ("SECLEC", "SECTION", "SECTION NO", "SECTION_NO", "SEC")
STUDENT_KEYS = ("ID", "STUDENT ID", "STUDENT_ID")
TEACHER_KEYS = ("LECTURER", "TEACHER", "INSTRUCTOR")
EMAIL_KEYS = ("CMU_MAIL", "CMU MAIL", "EMAIL", "E-MAIL")
DEPARTMENT_KEYS = ("DEPARTMENT", "DEPT", "DEPT_CODE")
ROLE_KEYS = ("ROLE", "POSITION", "EMPLOYEE_ROLE")
FULL_NAME_KEYS = ("FULL_NAME", "FULL NAME", "FULLNAME")
FIRST_NAME_KEYS = ("NAME", "FIRST_NAME", "FIRST NAME")
SURNAME_KEYS = ("SNAME", "SURNAME", "LAST_NAME", "LAST NAME")
TITLE_KEYS = ("TITLE",)
ROOM_KEYS = ("ROOM",)
CAPACITY_KEYS = ("MAX", "CAPACITY")
# room_capacity import — broader key sets matching validators.py
ROOM_CODE_CAPACITY_KEYS = ("ROOM", "ROOM_ID", "ROOM NAME", "ROOM_NAME", "ROOM_CODE")
ROOM_CAPACITY_NEW_KEYS = ("CAPACITY", "ROOM_CAP", "SEATS", "MAX_STUDENTS", "MAX")
NUM_STUDENT_KEYS = ("REGIST", "NUM_STUDENTS", "NUM STUDENTS")
CREDITS_KEYS = ("CRELEC", "CREDITS", "CREDIT")
COURSE_TITLE_KEYS = ("TITLE", "COURSE_NAME", "COURSE TITLE", "TITLE_TH")
MID_DAY_KEYS = ("MID_DAY", "MID DAY")
MID_TIME_KEYS = ("MID_TIME", "MID TIME")
FIN_DAY_KEYS = ("FIN_DAY", "FIN DAY")
FIN_TIME_KEYS = ("FIN_TIME", "FIN TIME")
MAJOR_KEYS = ("MAJOR",)
FACULTY_KEYS = ("FAC_NAME", "FACULTY_NAME", "FACULTY")
TYPE_REGIST_KEYS = ("TYPE_REGIST", "TYPE REGIST")
GRADE_KEYS = ("GRADE",)
DIVISION_KEYS = ("DIVISION",)
UNIT_KEYS = ("UNIT",)
MOBILE_KEYS = ("MOBILE", "PHONE")
EXT_KEYS = ("EXT", "EXTENSION")
EMPLOYEE_ID_KEYS = ("EMPLOYEE_ID", "EMPLOYEE ID")
TEACHER_ID_KEYS = ("TEACHER_ID", "TEACHER ID")

DEFAULT_IMPORTED_PASSWORD = "ems-import-v2-managed-account"
MONTHS = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
}


class ImportExecutionBlocked(Exception):
    def __init__(self, message: str, blocking_reasons: Optional[list[dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.blocking_reasons = blocking_reasons or []


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _pick_value(row: Dict[str, Any], candidate_keys: Iterable[str]) -> Any:
    for key in candidate_keys:
        if key in row and not _is_empty(row.get(key)):
            return row.get(key)
    return None


def _clean_text(value: Any) -> Optional[str]:
    return clean_whitespace(value)


def _normalize_numeric_text(value: Any) -> Optional[str]:
    text = _clean_text(value)
    if text is None:
        return None
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".", 1)[0]
    return text


def _normalize_email(value: Any) -> Optional[str]:
    text = _clean_text(value)
    return text.lower() if text else None


def _safe_int(value: Any, default: int = 0) -> int:
    text = _normalize_numeric_text(value)
    if text is None:
        return default
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default


def _compose_full_name(row: Dict[str, Any]) -> Optional[str]:
    direct = _clean_text(_pick_value(row, FULL_NAME_KEYS))
    if direct:
        return direct

    title = _clean_text(_pick_value(row, TITLE_KEYS))
    first_name = _clean_text(_pick_value(row, FIRST_NAME_KEYS))
    surname = _clean_text(_pick_value(row, SURNAME_KEYS))

    parts = [part for part in (title, first_name, surname) if part]
    if not parts:
        return None
    return " ".join(parts)


def _normalized_name_key(value: Any) -> Optional[str]:
    return normalize_person_name(value)


def _find_room_by_code(db: Session, room_code: str) -> Optional[models.Room]:
    for room in db.query(models.Room).all():
        normalized_existing = normalize_room_code(room.room_name)
        if normalized_existing == room_code:
            return room
    return None


def _make_username(email: str) -> str:
    return email.split("@", 1)[0].lower().strip()


def _unique_username(db: Session, base: str) -> str:
    candidate = base
    counter = 1
    while db.query(models.User).filter(models.User.username == candidate).first():
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate


def _default_password_hash() -> str:
    return hash_password(DEFAULT_IMPORTED_PASSWORD)


def _summarize_pairs(pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(pairs)
    summary = [
        {"code": code, "message": message, "count": count}
        for (code, message), count in counts.items()
    ]
    summary.sort(key=lambda item: (-item["count"], item["code"]))
    return summary


def _get_or_create_import_session(
    db: Session,
    academic_year: str,
    semester: str,
    exam_type: str,
    current_user_id: int,
) -> models.ImportSession:
    session = db.query(models.ImportSession).filter(
        and_(
            models.ImportSession.academic_year == academic_year,
            models.ImportSession.semester == semester,
            models.ImportSession.exam_type == exam_type,
        )
    ).first()
    if session:
        return session

    session = models.ImportSession(
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
        created_by=current_user_id,
    )
    db.add(session)
    db.flush()
    return session


def _parse_exam_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        pass

    match = re.match(r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})", text.upper())
    if not match:
        return None

    day, month_key, year = match.groups()
    month = MONTHS.get(month_key)
    if not month:
        return None

    return date(int(year), int(month), int(day))


def _resolve_exam_fields(row: Dict[str, Any], exam_type: str) -> tuple[Optional[date], Optional[str]]:
    if exam_type == "midterm":
        return (
            _parse_exam_date(_pick_value(row, MID_DAY_KEYS)),
            _clean_text(_pick_value(row, MID_TIME_KEYS)),
        )
    if exam_type == "final":
        return (
            _parse_exam_date(_pick_value(row, FIN_DAY_KEYS)),
            _clean_text(_pick_value(row, FIN_TIME_KEYS)),
        )
    return None, None


def _coerce_user_role(raw_value: Any) -> models.UserRole:
    text = (_clean_text(raw_value) or "").lower().replace("-", "_").replace(" ", "_")

    if text in {"admin"}:
        return models.UserRole.admin
    if text in {"teacher", "lecturer", "instructor"}:
        return models.UserRole.teacher
    if text in {"dept_supervisor", "department_supervisor", "supervisor", "head_of_department"}:
        return models.UserRole.dept_supervisor
    if text in {"secretary"}:
        return models.UserRole.secretary
    if text in {"esq", "esq_head", "governance", "governance_head", "head_of_unit"}:
        return models.UserRole.esq_head
    if text in {"print_shop", "printshop", "printing"}:
        return models.UserRole.print_shop
    if text in {"student"}:
        return models.UserRole.student
    return models.UserRole.staff


def _resolve_teacher_user_id(db: Session, lecturer_value: Any) -> Optional[int]:
    lecturer = _clean_text(lecturer_value)
    if not lecturer:
        return None

    if is_placeholder_lecturer(lecturer):
        return None

    lecturer_lower = lecturer.lower()
    normalized_lecturer = _normalized_name_key(lecturer)

    if "@" in lecturer_lower:
        user = db.query(models.User).filter(
            func.lower(models.User.email) == lecturer_lower
        ).first()
        if user:
            return user.id

    mapping = db.query(models.LecturerNameMap).filter(
        func.lower(models.LecturerNameMap.raw_name) == lecturer_lower
    ).first()
    if mapping:
        return mapping.teacher_id

    for alias in db.query(models.LecturerNameMap).all():
        if _normalized_name_key(alias.raw_name) == normalized_lecturer:
            return alias.teacher_id

    teachers = db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
    ).all()

    for teacher in teachers:
        if _normalized_name_key(teacher.full_name) == normalized_lecturer:
            return teacher.id

    surname = (normalized_lecturer or "").split()[-1] if normalized_lecturer else None
    if surname:
        for teacher in teachers:
            teacher_name = _normalized_name_key(teacher.full_name)
            if teacher_name and teacher_name.split() and teacher_name.split()[-1] == surname:
                return teacher.id

    return None


def _is_room_used_in_locked_term(db: Session, room_id: int) -> bool:
    """Defense-in-depth check at execute time. Mirrors validators._room_used_in_locked_term."""
    _locked_statuses = ["confirmed", "swap_open", "swap_confirming", "locked"]

    if (
        db.query(models.ExamSchedule)
        .filter(
            and_(
                models.ExamSchedule.room_id == room_id,
                models.ExamSchedule.status == models.ScheduleStatus.locked,
            )
        )
        .first()
    ):
        return True

    return (
        db.query(models.ExamSchedule)
        .join(models.Section, models.ExamSchedule.section_id == models.Section.id)
        .join(
            models.ExamPeriod,
            and_(
                models.ExamPeriod.academic_year == models.Section.academic_year,
                models.ExamPeriod.semester == models.Section.semester,
            ),
        )
        .join(
            models.OptimizeSession,
            models.OptimizeSession.exam_period_id == models.ExamPeriod.id,
        )
        .filter(
            models.ExamSchedule.room_id == room_id,
            models.OptimizeSession.status.in_(_locked_statuses),
        )
        .first()
    ) is not None


def _get_or_create_room(db: Session, row: Dict[str, Any]) -> Optional[models.Room]:
    room_name = normalize_room_code(_pick_value(row, ROOM_KEYS))
    if not room_name:
        return None

    room = _find_room_by_code(db, room_name)
    if room:
        if room.room_name != room_name:
            room.room_name = room_name
        if not room.building:
            room.building = room_building_from_code(room_name)
        return room

    room = models.Room(
        room_name=room_name,
        building=room_building_from_code(room_name),
        capacity=_safe_int(_pick_value(row, CAPACITY_KEYS), default=30),
    )
    db.add(room)
    db.flush()
    return room


def _execute_room_capacity(
    db: Session,
    rows: list[dict[str, Any]],
) -> tuple[set[int], dict[str, Any]]:
    """
    Execute room capacity import. Three cases per selected row:
      CREATE  — room does not exist → insert
      UPDATE  — room exists, capacity changed, term not locked → update
      SKIP    — room exists, capacity unchanged → no write
    Raises ImportExecutionBlocked if any selected row would modify a locked term.
    """
    imported_rows: set[int] = set()
    created = updated = skipped = blocked = 0
    blocking_reasons: list[dict[str, Any]] = []

    for row in rows:
        if not row.get("selected"):
            continue

        data = row["data"]
        room_code = normalize_room_code(_pick_value(data, ROOM_CODE_CAPACITY_KEYS))
        if not room_code:
            continue

        new_capacity = _safe_int(_pick_value(data, ROOM_CAPACITY_NEW_KEYS), default=0)
        if new_capacity <= 0:
            continue

        existing_room = _find_room_by_code(db, room_code)

        if existing_room is None:
            # ── CASE: CREATE ────────────────────────────────────────
            new_room = models.Room(
                room_name=room_code,
                capacity=new_capacity,
                building=room_building_from_code(room_code),
                is_active=True,
            )
            db.add(new_room)
            db.flush()
            row["change_type"] = "create"
            row["previous_capacity"] = None
            row["new_capacity"] = new_capacity
            imported_rows.add(row["_row"])
            created += 1

        else:
            if existing_room.room_name != room_code:
                existing_room.room_name = room_code
            if not existing_room.building:
                existing_room.building = room_building_from_code(room_code)
            old_capacity = existing_room.capacity or 0

            if old_capacity == new_capacity:
                # ── CASE: SKIP (no change) ───────────────────────────
                row["change_type"] = "skip"
                row["previous_capacity"] = old_capacity
                row["new_capacity"] = new_capacity
                imported_rows.add(row["_row"])
                skipped += 1

            elif _is_room_used_in_locked_term(db, existing_room.id):
                # ── CASE: BLOCK (locked term) ────────────────────────
                row["change_type"] = "blocked"
                row["previous_capacity"] = old_capacity
                row["new_capacity"] = new_capacity
                blocked += 1
                blocking_reasons.append({
                    "code": "locked_term_change",
                    "message": (
                        f"Room {room_code} capacity cannot change "
                        f"({old_capacity} → {new_capacity}): "
                        "used in a locked exam period"
                    ),
                })

            else:
                # ── CASE: UPDATE ─────────────────────────────────────
                existing_room.capacity = new_capacity
                row["change_type"] = "update"
                row["previous_capacity"] = old_capacity
                row["new_capacity"] = new_capacity
                imported_rows.add(row["_row"])
                updated += 1

    if blocking_reasons:
        raise ImportExecutionBlocked(
            "Room capacity import blocked — one or more rooms are used in locked exam periods.",
            blocking_reasons,
        )

    return imported_rows, {
        "room_changes": {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "blocked": blocked,
        }
    }


def _write_row_logs(
    db: Session,
    import_session: models.ImportSession,
    prepared_rows: list[dict[str, Any]],
    imported_row_numbers: set[int],
    override_user_id: int,
) -> None:
    now = datetime.now(timezone.utc)
    for row in prepared_rows:
        error_codes = row.get("error_codes", [])
        warning_codes = row.get("warning_codes", [])
        errors = row.get("errors", [])
        warnings = row.get("warnings", [])

        error_code = error_codes[0] if error_codes else warning_codes[0] if warning_codes else None
        error_message = errors[0] if errors else warnings[0] if warnings else None
        override_reason = row.get("override_reason")

        db.add(models.ImportRowLog(
            session_id=import_session.id,
            row_number=row.get("_row", -1),
            raw_data=row.get("data", {}),
            status=row.get("status", "valid"),
            error_code=error_code,
            error_message=error_message,
            was_selected=bool(row.get("selected")),
            was_imported=row.get("_row") in imported_row_numbers,
            override_reason=override_reason,
            override_by=override_user_id if override_reason else None,
            override_at=now if override_reason else None,
            change_type=row.get("change_type"),
            previous_capacity=row.get("previous_capacity"),
            new_capacity=row.get("new_capacity"),
        ))


def _execute_personnel(
    db: Session,
    rows: list[dict[str, Any]],
) -> tuple[set[int], dict[str, Any]]:
    imported_rows: set[int] = set()
    created_count = 0
    updated_count = 0

    for row in rows:
        if not row.get("selected"):
            continue

        data = row["data"]
        email = _normalize_email(_pick_value(data, EMAIL_KEYS))
        if not email:
            continue

        user = db.query(models.User).filter(func.lower(models.User.email) == email).first()
        full_name = _compose_full_name(data)
        department = _clean_text(_pick_value(data, DEPARTMENT_KEYS))
        title = _clean_text(_pick_value(data, TITLE_KEYS))
        mobile = _clean_text(_pick_value(data, MOBILE_KEYS))
        ext = _clean_text(_pick_value(data, EXT_KEYS))
        employee_id = _safe_int(_pick_value(data, TEACHER_ID_KEYS), default=0) or None

        if not user:
            user = models.User(
                username=_unique_username(db, _make_username(email)),
                email=email,
                password_hash=_default_password_hash(),
                role=models.UserRole.teacher,
                full_name=full_name,
                department=department,
                dept_code=department,
                title=title,
                mobile=mobile,
                ext=ext,
                employee_id=employee_id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_count += 1
        else:
            if user.role != models.UserRole.admin:
                user.role = models.UserRole.teacher
            if full_name:
                user.full_name = full_name
            if department:
                user.department = department
                user.dept_code = department
            if title:
                user.title = title
            if mobile:
                user.mobile = mobile
            if ext:
                user.ext = ext
            if employee_id is not None:
                user.employee_id = employee_id
            updated_count += 1

        imported_rows.add(row["_row"])

    return imported_rows, {
        "created_teachers": created_count,
        "updated_teachers": updated_count,
    }


def _execute_employee(
    db: Session,
    rows: list[dict[str, Any]],
) -> tuple[set[int], dict[str, Any]]:
    imported_rows: set[int] = set()
    created_count = 0
    updated_count = 0

    for row in rows:
        if not row.get("selected"):
            continue

        data = row["data"]
        email = _normalize_email(_pick_value(data, EMAIL_KEYS))
        if not email:
            continue

        role = _coerce_user_role(_pick_value(data, ROLE_KEYS))
        user = db.query(models.User).filter(func.lower(models.User.email) == email).first()

        full_name = _compose_full_name(data)
        department = _clean_text(_pick_value(data, DEPARTMENT_KEYS))
        division = _clean_text(_pick_value(data, DIVISION_KEYS))
        unit = _clean_text(_pick_value(data, UNIT_KEYS))
        title = _clean_text(_pick_value(data, TITLE_KEYS))
        mobile = _clean_text(_pick_value(data, MOBILE_KEYS))
        ext = _clean_text(_pick_value(data, EXT_KEYS))
        employee_id = _safe_int(_pick_value(data, EMPLOYEE_ID_KEYS), default=0) or None

        if not user:
            user = models.User(
                username=_unique_username(db, _make_username(email)),
                email=email,
                password_hash=_default_password_hash(),
                role=role,
                full_name=full_name,
                department=department or division,
                division=division,
                unit=unit,
                title=title,
                mobile=mobile,
                ext=ext,
                employee_id=employee_id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_count += 1
        else:
            if user.role != models.UserRole.admin:
                user.role = role
            if full_name:
                user.full_name = full_name
            if department or division:
                user.department = department or division
            if division:
                user.division = division
            if unit:
                user.unit = unit
            if title:
                user.title = title
            if mobile:
                user.mobile = mobile
            if ext:
                user.ext = ext
            if employee_id is not None:
                user.employee_id = employee_id
            updated_count += 1

        imported_rows.add(row["_row"])

    return imported_rows, {
        "created_employees": created_count,
        "updated_employees": updated_count,
    }


def _execute_opencourse(
    db: Session,
    rows: list[dict[str, Any]],
    import_session: models.ImportSession,
    academic_year: str,
    semester: str,
    exam_type: Optional[str],
) -> tuple[set[int], dict[str, Any]]:
    imported_rows: set[int] = set()
    created_courses = 0
    created_sections = 0
    updated_sections = 0
    created_schedules = 0
    updated_schedules = 0

    for row in rows:
        if not row.get("selected"):
            continue

        data = row["data"]
        course_code = _normalize_numeric_text(_pick_value(data, COURSE_KEYS))
        section_no = _normalize_numeric_text(_pick_value(data, SECTION_KEYS))
        if not course_code or not section_no:
            continue

        course = db.query(models.Course).filter(models.Course.course_id == course_code).first()
        title = _clean_text(_pick_value(data, COURSE_TITLE_KEYS))
        credits = _safe_int(_pick_value(data, CREDITS_KEYS), default=3)

        if not course:
            course = models.Course(
                course_id=course_code,
                course_name_th=title,
                course_name_en=title,
                credits=credits or 3,
            )
            db.add(course)
            db.flush()
            created_courses += 1
        else:
            if title and not course.course_name_th:
                course.course_name_th = title
            if title and not course.course_name_en:
                course.course_name_en = title
            if credits:
                course.credits = credits

        section = db.query(models.Section).filter(
            and_(
                models.Section.course_id == course.id,
                models.Section.section_no == section_no,
                models.Section.semester == semester,
                models.Section.academic_year == academic_year,
            )
        ).first()

        num_students = _safe_int(_pick_value(data, NUM_STUDENT_KEYS), default=0)
        teacher_id = _resolve_teacher_user_id(db, _pick_value(data, TEACHER_KEYS))

        if not section:
            section = models.Section(
                course_id=course.id,
                section_no=section_no,
                teacher_id=teacher_id,
                num_students=num_students,
                semester=semester,
                academic_year=academic_year,
                import_session_id=import_session.id,
            )
            db.add(section)
            db.flush()
            created_sections += 1
        else:
            section.num_students = num_students
            section.import_session_id = import_session.id
            if teacher_id:
                section.teacher_id = teacher_id
            updated_sections += 1

        if exam_type in {"midterm", "final"}:
            room = _get_or_create_room(db, data)
            exam_date, exam_time = _resolve_exam_fields(data, exam_type)
            if exam_date:
                schedule = db.query(models.ExamSchedule).filter(
                    and_(
                        models.ExamSchedule.section_id == section.id,
                        models.ExamSchedule.exam_type == getattr(models.ExamType, exam_type),
                    )
                ).first()
                if not schedule:
                    schedule = models.ExamSchedule(
                        section_id=section.id,
                        room_id=room.id if room else None,
                        exam_date=exam_date,
                        exam_time=exam_time,
                        exam_type=getattr(models.ExamType, exam_type),
                        status=models.ScheduleStatus.draft,
                        num_pages=0,
                        total_sheets=0,
                    )
                    db.add(schedule)
                    created_schedules += 1
                else:
                    schedule.exam_date = exam_date
                    schedule.exam_time = exam_time
                    if room:
                        schedule.room_id = room.id
                    updated_schedules += 1

        imported_rows.add(row["_row"])

    import_session.opencourse_rows = len(rows)
    import_session.last_updated = datetime.now(timezone.utc)

    return imported_rows, {
        "created_courses": created_courses,
        "created_sections": created_sections,
        "updated_sections": updated_sections,
        "created_schedules": created_schedules,
        "updated_schedules": updated_schedules,
    }


def _build_enrollment_blockers(
    db: Session,
    rows: list[dict[str, Any]],
    academic_year: str,
    semester: str,
) -> tuple[dict[str, models.Course], dict[tuple[int, str], models.Section], list[dict[str, Any]]]:
    selected_rows = [row for row in rows if row.get("selected")]
    course_codes = sorted({
        _normalize_numeric_text(_pick_value(row["data"], COURSE_KEYS))
        for row in selected_rows
        if _normalize_numeric_text(_pick_value(row["data"], COURSE_KEYS))
    })

    courses = {
        course.course_id: course
        for course in db.query(models.Course).filter(models.Course.course_id.in_(course_codes)).all()
    } if course_codes else {}

    sections = {
        (section.course_id, section.section_no): section
        for section in db.query(models.Section).filter(
            and_(
                models.Section.semester == semester,
                models.Section.academic_year == academic_year,
            )
        ).all()
    }

    blocking_pairs: list[tuple[str, str]] = []

    for row in selected_rows:
        data = row["data"]
        course_code = _normalize_numeric_text(_pick_value(data, COURSE_KEYS))
        section_no = _normalize_numeric_text(_pick_value(data, SECTION_KEYS))
        course = courses.get(course_code) if course_code else None
        if not course and course_code:
            blocking_pairs.append((
                "missing_course_reference",
                f"Course {course_code} does not exist for enrollment import",
            ))
            continue
        if course and section_no and (course.id, section_no) not in sections:
            blocking_pairs.append((
                "missing_section_reference",
                f"Section {course_code}/{section_no} does not exist for {academic_year}/{semester}",
            ))

    return courses, sections, _summarize_pairs(blocking_pairs)


def _execute_enrollment(
    db: Session,
    rows: list[dict[str, Any]],
    import_session: models.ImportSession,
    academic_year: str,
    semester: str,
) -> tuple[set[int], dict[str, Any]]:
    imported_rows: set[int] = set()
    created_records = 0
    updated_records = 0
    touched_sections: set[int] = set()

    courses, sections, blockers = _build_enrollment_blockers(
        db,
        rows,
        academic_year,
        semester,
    )
    if blockers:
        raise ImportExecutionBlocked(
            "Enrollment rows reference courses or sections that are not ready for import.",
            blockers,
        )

    for row in rows:
        if not row.get("selected"):
            continue

        data = row["data"]
        course_code = _normalize_numeric_text(_pick_value(data, COURSE_KEYS))
        section_no = _normalize_numeric_text(_pick_value(data, SECTION_KEYS))
        student_id = _normalize_numeric_text(_pick_value(data, STUDENT_KEYS))
        if not all((course_code, section_no, student_id)):
            continue

        if str(_pick_value(data, GRADE_KEYS) or "").strip().upper() == "W":
            continue

        course = courses.get(course_code)
        if not course:
            continue

        section = sections.get((course.id, section_no))
        if not section:
            continue

        record = db.query(models.EnrollmentRecord).filter(
            and_(
                models.EnrollmentRecord.import_session_id == import_session.id,
                models.EnrollmentRecord.section_id == section.id,
                models.EnrollmentRecord.student_id == student_id,
            )
        ).first()

        student_name = " ".join(
            part for part in (
                _clean_text(_pick_value(data, FIRST_NAME_KEYS)),
                _clean_text(_pick_value(data, SURNAME_KEYS)),
            ) if part
        ) or _compose_full_name(data)

        if not record:
            record = models.EnrollmentRecord(
                import_session_id=import_session.id,
                section_id=section.id,
                student_id=student_id,
                student_name=student_name,
                major=_clean_text(_pick_value(data, MAJOR_KEYS)),
                faculty_name=_clean_text(_pick_value(data, FACULTY_KEYS)),
                type_regist=_clean_text(_pick_value(data, TYPE_REGIST_KEYS)),
            )
            db.add(record)
            created_records += 1
        else:
            record.student_name = student_name
            record.major = _clean_text(_pick_value(data, MAJOR_KEYS))
            record.faculty_name = _clean_text(_pick_value(data, FACULTY_KEYS))
            record.type_regist = _clean_text(_pick_value(data, TYPE_REGIST_KEYS))
            updated_records += 1

        touched_sections.add(section.id)
        imported_rows.add(row["_row"])

    db.flush()

    for section_id in touched_sections:
        total_students = db.query(func.count(models.EnrollmentRecord.id)).filter(
            and_(
                models.EnrollmentRecord.import_session_id == import_session.id,
                models.EnrollmentRecord.section_id == section_id,
            )
        ).scalar() or 0
        db.query(models.Section).filter(models.Section.id == section_id).update({
            "num_students": total_students,
        })

    import_session.enrollment_rows = len(rows)
    import_session.last_updated = datetime.now(timezone.utc)

    return imported_rows, {
        "created_enrollments": created_records,
        "updated_enrollments": updated_records,
        "sections_synced": len(touched_sections),
    }


def execute_import(
    db: Session,
    *,
    import_type: str,
    academic_year: str,
    semester: str,
    exam_type: str,
    prepared_rows: list[dict[str, Any]],
    confirmed_by: int,
    source_filename: Optional[str],
) -> dict[str, Any]:
    import_session = _get_or_create_import_session(
        db,
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
        current_user_id=confirmed_by,
    )

    if import_type == "opencourse":
        imported_row_numbers, write_summary = _execute_opencourse(
            db,
            prepared_rows,
            import_session,
            academic_year,
            semester,
            exam_type,
        )
    elif import_type == "enrollment":
        imported_row_numbers, write_summary = _execute_enrollment(
            db,
            prepared_rows,
            import_session,
            academic_year,
            semester,
        )
    elif import_type == "personnel":
        imported_row_numbers, write_summary = _execute_personnel(db, prepared_rows)
    elif import_type == "employee":
        imported_row_numbers, write_summary = _execute_employee(db, prepared_rows)
    elif import_type == "room_capacity":
        imported_row_numbers, write_summary = _execute_room_capacity(db, prepared_rows)
    else:
        raise ImportExecutionBlocked("Unsupported import_type for execution.")

    _write_row_logs(
        db,
        import_session,
        prepared_rows,
        imported_row_numbers,
        override_user_id=confirmed_by,
    )
    db.flush()

    override_count = sum(1 for row in prepared_rows if row.get("override_reason"))
    imported_count = len(imported_row_numbers)

    return {
        "success": True,
        "total_rows": len(prepared_rows),
        "imported_count": imported_count,
        "skipped_count": len(prepared_rows) - imported_count,
        "override_count": override_count,
        "import_session_id": import_session.id,
        "summary": {
            "import_type": import_type,
            "academic_year": academic_year,
            "semester": semester,
            "exam_type": exam_type,
            "historical_mode": True,
            "source_filename": source_filename,
            "selected_count": sum(1 for row in prepared_rows if row.get("selected")),
            "row_logs_written": len(prepared_rows),
            "business_writes": write_summary,
        },
    }
