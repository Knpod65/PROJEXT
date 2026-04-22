from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple

from import_v2.normalizers import normalize_room_code

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


COURSE_KEYS = ("COURSENO", "COURESNO", "COURSE CODE", "COURSE NO", "COURSE")
SECTION_KEYS = ("SECLEC", "SECTION", "SECTION NO", "SECTION_NO", "SEC")
STUDENT_KEYS = ("ID", "STUDENT ID", "STUDENT_ID")
TEACHER_KEYS = ("LECTURER", "TEACHER", "INSTRUCTOR")
EMAIL_KEYS = ("CMU_MAIL", "CMU MAIL", "EMAIL", "E-MAIL")
DEPARTMENT_KEYS = ("DEPARTMENT", "DEPT", "DEPT_CODE")
ROLE_KEYS = ("ROLE", "POSITION", "EMPLOYEE_ROLE")
ROOM_CODE_KEYS = ("ROOM", "ROOM_ID", "ROOM NAME", "ROOM_NAME")
BUILDING_KEYS = ("BUILDING",)
ROOM_CAPACITY_KEYS = ("CAPACITY", "ROOM_CAP", "SEATS", "MAX_STUDENTS", "MAX")
GRADE_KEYS = ("GRADE",)

SUPPORTED_IMPORT_TYPES = {
    "opencourse",
    "personnel",
    "employee",
    "enrollment",
    "room_capacity",
}

OVERRIDE_POLICY_RULES = {
    "duplicate_enrollment_row": "allowed",
    "missing_section": "disallowed",
    "missing_student_id": "disallowed",
    "missing_course_code": "disallowed",
    "duplicate_course_section": "disallowed",
    "missing_teacher_email": "disallowed",
    "missing_cmu_mail": "disallowed",
    "duplicate_cmu_mail": "disallowed",
    "empty_row": "disallowed",
    "duplicate_room_code": "allowed",
    "capacity_change_large": "allowed",
    "locked_term_change": "disallowed",
    "missing_room_code": "disallowed",
    "missing_capacity": "disallowed",
    "invalid_capacity": "disallowed",
    "withdrawn_enrollment": "disallowed",
    "missing_course_reference": "disallowed",
    "missing_section_reference": "disallowed",
}


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


def _is_empty_row(row: Dict[str, Any]) -> bool:
    for key, value in row.items():
        if key == "_row":
            continue
        if not _is_empty(value):
            return False
    return True


def _add_issue(
    messages: List[str],
    codes: List[str],
    code: str,
    message: str,
) -> None:
    if code in codes:
        return
    messages.append(message)
    codes.append(code)


def _course_section_key(row: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    course = _pick_value(row, COURSE_KEYS)
    section = _pick_value(row, SECTION_KEYS)
    if any(_is_empty(value) for value in (course, section)):
        return None
    return (str(course).strip(), str(section).strip())


def _enrollment_key(row: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
    course = _pick_value(row, COURSE_KEYS)
    section = _pick_value(row, SECTION_KEYS)
    student = _pick_value(row, STUDENT_KEYS)
    if any(_is_empty(value) for value in (course, section, student)):
        return None
    return (str(course).strip(), str(section).strip(), str(student).strip())


def _email_key(row: Dict[str, Any]) -> Optional[str]:
    email = _pick_value(row, EMAIL_KEYS)
    if _is_empty(email):
        return None
    return str(email).strip().lower()


def _room_code_key(row: Dict[str, Any]) -> Optional[str]:
    room_code = _pick_value(row, ROOM_CODE_KEYS)
    return normalize_room_code(room_code)


def _normalize_numeric_text(value: Any) -> Optional[str]:
    if _is_empty(value):
        return None
    text = str(value).strip()
    if text.endswith(".0") and text.replace(".", "", 1).isdigit():
        return text[:-2]
    return text


def _is_positive_number(value: Any) -> bool:
    if _is_empty(value):
        return False
    try:
        return float(str(value).strip()) > 0
    except (TypeError, ValueError):
        return False


def _looks_like_placeholder_lecturer(value: Any) -> bool:
    if _is_empty(value):
        return False
    text = str(value).strip().lower()
    markers = ("๏ฟฝ", "�", "placeholder")
    return any(marker in text for marker in markers)


def _prepare_duplicate_counters(
    rows: List[Dict[str, Any]],
    import_type: str,
) -> Dict[str, Counter]:
    counters: Dict[str, Counter] = {}

    if import_type == "enrollment":
        counters["enrollment"] = Counter(
            key for key in (_enrollment_key(row) for row in rows) if key is not None
        )
    elif import_type == "opencourse":
        counters["course_section"] = Counter(
            key for key in (_course_section_key(row) for row in rows) if key is not None
        )
    elif import_type in {"personnel", "employee"}:
        counters["email"] = Counter(
            key for key in (_email_key(row) for row in rows) if key is not None
        )
    elif import_type == "room_capacity":
        counters["room_code"] = Counter(
            key for key in (_room_code_key(row) for row in rows) if key is not None
        )

    return counters


def _resolve_override_metadata(
    status: str,
    error_codes: List[str],
    warning_codes: List[str],
) -> tuple[bool, str]:
    policies = [
        OVERRIDE_POLICY_RULES.get(code, "allowed")
        for code in [*error_codes, *warning_codes]
    ]

    if "requires_mapping" in policies:
        return False, "requires_mapping"

    if status == "error":
        if policies and all(policy == "allowed" for policy in policies):
            return True, "allowed"
        return False, "disallowed"

    if status == "warning":
        return True, "allowed"

    return False, "allowed"


def _refresh_row_metadata(row: Dict[str, Any]) -> None:
    if row["error_codes"]:
        row["status"] = "error"
    elif row["warning_codes"]:
        row["status"] = "warning"
    else:
        row["status"] = "valid"

    row["can_override"], row["override_policy"] = _resolve_override_metadata(
        row["status"],
        row["error_codes"],
        row["warning_codes"],
    )


def validate_rows(rows: List[Dict[str, Any]], import_type: str) -> List[Dict[str, Any]]:
    if import_type not in SUPPORTED_IMPORT_TYPES:
        raise ValueError(f"Unsupported import_type: {import_type}")

    counters = _prepare_duplicate_counters(rows, import_type)
    validated_rows: List[Dict[str, Any]] = []

    for row in rows:
        errors: List[str] = []
        warnings: List[str] = []
        error_codes: List[str] = []
        warning_codes: List[str] = []

        if _is_empty_row(row):
            _add_issue(errors, error_codes, "empty_row", "Empty row")
        else:
            if import_type in {"enrollment", "opencourse"}:
                course = _pick_value(row, COURSE_KEYS)
                section = _pick_value(row, SECTION_KEYS)

                if _is_empty(course):
                    _add_issue(errors, error_codes, "missing_course_code", "Missing course code")
                if _is_empty(section):
                    _add_issue(errors, error_codes, "missing_section", "Missing section")

            if import_type == "enrollment":
                student_id = _pick_value(row, STUDENT_KEYS)
                if _is_empty(student_id):
                    _add_issue(errors, error_codes, "missing_student_id", "Missing student ID")

                enrollment_key = _enrollment_key(row)
                if enrollment_key and counters["enrollment"][enrollment_key] > 1:
                    _add_issue(
                        warnings,
                        warning_codes,
                        "duplicate_enrollment_row",
                        "Duplicate enrollment row",
                    )

            elif import_type == "opencourse":
                lecturer = _pick_value(row, TEACHER_KEYS)
                if _is_empty(lecturer):
                    _add_issue(
                        warnings,
                        warning_codes,
                        "missing_teacher_field",
                        "Teacher field is empty",
                    )
                elif _looks_like_placeholder_lecturer(lecturer):
                    _add_issue(
                        warnings,
                        warning_codes,
                        "unresolved_lecturer_placeholder",
                        "Lecturer value needs cleanup before matching",
                    )

                course_section_key = _course_section_key(row)
                if course_section_key and counters["course_section"][course_section_key] > 1:
                    _add_issue(
                        errors,
                        error_codes,
                        "duplicate_course_section",
                        "Duplicate course + section row",
                    )

            elif import_type == "personnel":
                teacher_email = _pick_value(row, EMAIL_KEYS)
                if _is_empty(teacher_email):
                    _add_issue(
                        errors,
                        error_codes,
                        "missing_teacher_email",
                        "Missing teacher email",
                    )

                email_key = _email_key(row)
                if email_key and counters["email"][email_key] > 1:
                    _add_issue(
                        errors,
                        error_codes,
                        "duplicate_cmu_mail",
                        "Duplicate cmu_mail",
                    )

                department = _pick_value(row, DEPARTMENT_KEYS)
                if _is_empty(department):
                    _add_issue(
                        warnings,
                        warning_codes,
                        "missing_department",
                        "Missing department",
                    )

            elif import_type == "employee":
                cmu_mail = _pick_value(row, EMAIL_KEYS)
                if _is_empty(cmu_mail):
                    _add_issue(
                        errors,
                        error_codes,
                        "missing_cmu_mail",
                        "Missing cmu_mail",
                    )

                email_key = _email_key(row)
                if email_key and counters["email"][email_key] > 1:
                    _add_issue(
                        errors,
                        error_codes,
                        "duplicate_cmu_mail",
                        "Duplicate cmu_mail",
                    )

                role = _pick_value(row, ROLE_KEYS)
                if _is_empty(role):
                    _add_issue(
                        warnings,
                        warning_codes,
                        "missing_role",
                        "Missing role",
                    )

            elif import_type == "room_capacity":
                room_code = _pick_value(row, ROOM_CODE_KEYS)
                capacity = _pick_value(row, ROOM_CAPACITY_KEYS)

                if _is_empty(room_code):
                    _add_issue(
                        errors,
                        error_codes,
                        "missing_room_code",
                        "Missing room code",
                    )

                if _is_empty(capacity):
                    _add_issue(
                        errors,
                        error_codes,
                        "missing_capacity",
                        "Missing capacity",
                    )
                elif not _is_positive_number(capacity):
                    _add_issue(
                        errors,
                        error_codes,
                        "invalid_capacity",
                        "Capacity must be greater than zero",
                    )

                room_code_key = _room_code_key(row)
                if room_code_key and counters["room_code"][room_code_key] > 1:
                    _add_issue(
                        warnings,
                        warning_codes,
                        "duplicate_room_code",
                        "Duplicate room code in upload",
                    )

        status = "valid"
        if error_codes:
            status = "error"
        elif warning_codes:
            status = "warning"

        can_override, override_policy = _resolve_override_metadata(
            status,
            error_codes,
            warning_codes,
        )

        validated_rows.append({
            "_row": row.get("_row"),
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "error_codes": error_codes,
            "warning_codes": warning_codes,
            "can_override": can_override,
            "override_policy": override_policy,
            "data": row,
        })

    return validated_rows


_LARGE_CHANGE_THRESHOLD = 0.30
_LOCKED_OPTIMIZE_STATUSES = frozenset(
    ["confirmed", "swap_open", "swap_confirming", "locked"]
)
_BLOCKING_FIELD_CODES = frozenset(
    ["missing_room_code", "missing_capacity", "invalid_capacity", "empty_row"]
)
_ENROLLMENT_BLOCKING_FIELD_CODES = frozenset(
    ["missing_course_code", "missing_section", "missing_student_id", "empty_row"]
)


def validate_room_capacity_db(
    validated_rows: List[Dict[str, Any]],
    db: "Session",
) -> List[Dict[str, Any]]:
    from sqlalchemy import func as sqlfunc
    import models as _models

    room_map = {
        normalize_room_code(room.room_name): room
        for room in db.query(_models.Room).all()
        if normalize_room_code(room.room_name)
    }

    for row in validated_rows:
        if any(code in _BLOCKING_FIELD_CODES for code in row.get("error_codes", [])):
            continue

        data = row.get("data", {})
        room_code = _room_code_key(data)
        capacity_raw = _pick_value(data, ROOM_CAPACITY_KEYS)

        if not room_code or not _is_positive_number(capacity_raw):
            continue

        new_capacity = int(float(str(capacity_raw).strip()))
        existing_room = room_map.get(room_code)

        row["db_state"] = {
            "room_exists": existing_room is not None,
            "previous_capacity": existing_room.capacity if existing_room else None,
            "new_capacity": new_capacity,
            "room_id": existing_room.id if existing_room else None,
            "room_code": room_code,
        }

        if existing_room is None:
            continue

        old_capacity = existing_room.capacity or 0

        if old_capacity != new_capacity:
            if old_capacity > 0:
                diff = abs(new_capacity - old_capacity) / old_capacity
                if diff > _LARGE_CHANGE_THRESHOLD:
                    _add_issue(
                        row["warnings"],
                        row["warning_codes"],
                        "capacity_change_large",
                        (
                            f"Large capacity change: {old_capacity} โ’ {new_capacity} "
                            f"({diff:.0%} difference) โ€” override required"
                        ),
                    )

            used_in_locked = _room_used_in_locked_term(db, existing_room.id, _models)
            if used_in_locked:
                _add_issue(
                    row["errors"],
                    row["error_codes"],
                    "locked_term_change",
                    (
                        f"Room {room_code} is referenced in a locked exam period "
                        f"(capacity {old_capacity} โ’ {new_capacity} blocked)"
                    ),
                )

        _refresh_row_metadata(row)

    return validated_rows


def validate_enrollment_db(
    validated_rows: List[Dict[str, Any]],
    db: "Session",
    academic_year: str,
    semester: str,
) -> List[Dict[str, Any]]:
    from sqlalchemy import and_
    import models as _models

    selected_course_codes = {
        course_code
        for row in validated_rows
        if not any(code in _ENROLLMENT_BLOCKING_FIELD_CODES for code in row.get("error_codes", []))
        for course_code in [_normalize_numeric_text(_pick_value(row.get("data", {}), COURSE_KEYS))]
        if course_code
    }

    courses = {
        course.course_id: course
        for course in db.query(_models.Course).filter(_models.Course.course_id.in_(sorted(selected_course_codes))).all()
    } if selected_course_codes else {}

    sections = {
        (section.course_id, section.section_no): section
        for section in db.query(_models.Section).filter(
            and_(
                _models.Section.semester == semester,
                _models.Section.academic_year == academic_year,
            )
        ).all()
    }

    for row in validated_rows:
        if any(code in _ENROLLMENT_BLOCKING_FIELD_CODES for code in row.get("error_codes", [])):
            continue

        data = row.get("data", {})
        course_code = _normalize_numeric_text(_pick_value(data, COURSE_KEYS))
        section_no = _normalize_numeric_text(_pick_value(data, SECTION_KEYS))
        grade = str(_pick_value(data, GRADE_KEYS) or "").strip().upper()

        row["db_state"] = {
            "course_code": course_code,
            "section_no": section_no,
            "grade": grade or None,
        }

        if grade == "W":
            _add_issue(
                row["errors"],
                row["error_codes"],
                "withdrawn_enrollment",
                "Withdrawn enrollment rows are skipped from import",
            )

        course = courses.get(course_code) if course_code else None
        if not course:
            _add_issue(
                row["errors"],
                row["error_codes"],
                "missing_course_reference",
                f"Course {course_code or '-'} does not exist for enrollment import",
            )
            _refresh_row_metadata(row)
            continue

        if section_no and (course.id, section_no) not in sections:
            _add_issue(
                row["errors"],
                row["error_codes"],
                "missing_section_reference",
                f"Section {course_code}/{section_no} does not exist for {academic_year}/{semester}",
            )

        _refresh_row_metadata(row)

    return validated_rows


def _room_used_in_locked_term(db: "Session", room_id: int, _models: Any) -> bool:
    from sqlalchemy import and_

    if (
        db.query(_models.ExamSchedule)
        .filter(
            _models.ExamSchedule.room_id == room_id,
            _models.ExamSchedule.status == _models.ScheduleStatus.locked,
        )
        .first()
    ):
        return True

    return (
        db.query(_models.ExamSchedule)
        .join(_models.Section, _models.ExamSchedule.section_id == _models.Section.id)
        .join(
            _models.ExamPeriod,
            and_(
                _models.ExamPeriod.academic_year == _models.Section.academic_year,
                _models.ExamPeriod.semester == _models.Section.semester,
            ),
        )
        .join(
            _models.OptimizeSession,
            _models.OptimizeSession.exam_period_id == _models.ExamPeriod.id,
        )
        .filter(
            _models.ExamSchedule.room_id == room_id,
            _models.OptimizeSession.status.in_(list(_LOCKED_OPTIMIZE_STATUSES)),
        )
        .first()
    ) is not None
