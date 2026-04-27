from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from pathlib import Path
import re
from typing import Any, Iterable, Optional

from pypdf import PdfReader
from sqlalchemy.orm import Session

import models
from import_v2.normalizers import normalize_person_name, normalize_room_code


ROOM_OPENING_START_SETTING_KEY = "room_opening_rotation_start_username"
DEFAULT_ROOM_OPENING_START_USERNAME = "thiraphan.y"
ROOM_OPENING_NAME_HINTS = ("ธีราภัณฑ์", "ชนะชล")
PDF_COLUMN_BOUNDS = {
    "left": 120,
    "course": 205,
    "teacher": 360,
    "count": 405,
    "room": 480,
    "inv": 665,
}
THAI_MONTHS = {
    "มกราคม": 1,
    "กุมภาพันธ์": 2,
    "มีนาคม": 3,
    "เมษายน": 4,
    "พฤษภาคม": 5,
    "มิถุนายน": 6,
    "กรกฎาคม": 7,
    "สิงหาคม": 8,
    "กันยายน": 9,
    "ตุลาคม": 10,
    "พฤศจิกายน": 11,
    "ธันวาคม": 12,
}
TITLE_START_RE = re.compile(r"(ผศ\.ดร\.|รศ\.ดร\.|ศ\.ดร\.|อ\.ดร\.|ผศ\.|รศ\.|ศ\.|อ\.)")
COURSE_ROW_RE = re.compile(r"^(?P<course>\d{6})\s+Sec\s+(?P<section>[A-Za-z0-9]+)$")
ROOM_RE = re.compile(r"(online|auditorium50th|PSB\s*\d(?:\s*\d){3})", re.IGNORECASE)
TIME_RE = re.compile(r"(?P<start>\d{2}\.\d{2})\s*-\s*(?P<end>\d{2}\.\d{2})")

# Thai column-header / administrative-label strings that must never be treated as person names.
# These appear in PDF table header rows and sometimes bleed into data bands on new pages.
_COLUMN_HEADER_TEXT: frozenset[str] = frozenset({
    "กรรมการคุมสอบ",
    "กรรมการจ่ายข้อสอบ",
    "กรรมการจ่ายข้อสอบ/เปิดห้อง",
    "กรรมการจ่ายข้อสอบ / เปิดห้อง",
    "กรรมการจ่าย ข้อสอบ / เปิดห้อง",
    "เปิดห้อง",
    "รหัสวิชา",
    "อาจารย์ผู้สอน",
    "ห้องสอบ",
    "จำนวนนักศึกษา",
    "จำนวน",
    "วัน/เวลา",
    "วัน/เวลาสอบ",
    "รายวิชา",
    "วิชา",
})

# Course-column texts that indicate a repeating table header row (not a data row).
_COURSE_HEADER_TEXT: frozenset[str] = frozenset({
    "รหัสวิชา",
    "วิชา",
    "รายวิชา",
    "course",
})


@dataclass
class ParsedEntry:
    row_order: int
    exam_date: date
    exam_time: str
    exam_time_start: str | None
    exam_time_end: str | None
    course_code: str
    section_no: str
    instructor_name: str
    student_count: int
    room_name: str | None = None
    invigilators_raw: str | None = None
    distribution_raw: str | None = None
    paper_distribution_staff_name: str | None = None
    room_opening_staff_name: str | None = None
    inherited_room: bool = False
    inherited_invigilators: bool = False
    inherited_distribution: bool = False
    parse_flags: list[str] = field(default_factory=list)
    course_ref_id: int | None = None
    section_ref_id: int | None = None
    teacher_ref_id: int | None = None


@dataclass
class ParsedInvigilator:
    display_name: str
    normalized_name: str | None
    user_id: int | None
    role_kind: models.HistoricalInvigilatorKind
    notes: str | None = None


@dataclass
class ParsedDistributionSlot:
    exam_date: date
    exam_time: str
    exam_time_start: str | None
    exam_time_end: str | None
    raw_value: str | None
    paper_distribution_staff_name: str | None
    room_opening_staff_name: str | None
    paper_distribution_user_id: int | None
    room_opening_user_id: int | None
    source_mode: str
    covered_courses: list[str]
    covered_rooms: list[str]
    covered_row_count: int
    notes: str | None = None


class NameResolver:
    def __init__(self, db: Session):
        self._users = db.query(models.User).filter(models.User.is_active == True).all()
        self._by_exact: dict[str, list[models.User]] = defaultdict(list)
        self._token_index: dict[str, list[models.User]] = defaultdict(list)
        for user in self._users:
            normalized = normalize_person_name(user.full_name)
            if not normalized:
                continue
            self._by_exact[normalized].append(user)
            for token in normalized.split():
                self._token_index[token].append(user)

    def resolve_user(self, raw_name: str | None) -> models.User | None:
        if not raw_name:
            return None
        for candidate in self._candidate_normalizations(raw_name):
            exact = self._by_exact.get(candidate, [])
            if len(exact) == 1:
                return exact[0]
            prefix_matches = [user for user in self._users if normalize_person_name(user.full_name or "") and normalize_person_name(user.full_name or "").startswith(candidate)]
            if len(prefix_matches) == 1:
                return prefix_matches[0]
            token_matches = self._token_index.get(candidate, [])
            if len(token_matches) == 1:
                return token_matches[0]
        return None

    def _candidate_normalizations(self, raw_name: str) -> list[str]:
        values: list[str] = []
        for candidate in {raw_name, raw_name.replace(" ", ""), raw_name.replace("-", " "), raw_name.replace("–", " ")}:
            normalized = normalize_person_name(candidate)
            if normalized and normalized not in values:
                values.append(normalized)
        return values


def _compact_titles(text: str | None) -> str:
    if not text:
        return ""
    value = re.sub(r"\s+", " ", text.replace("\u00a0", " ")).strip()
    value = value.replace("–", "-")
    value = value.replace(" .", ".").replace(". ", ".")
    value = re.sub(r"([ผรศอ])\s*\.\s*ดร\s*\.", r"\1.ดร.", value)
    value = re.sub(r"\bผศ\s*\.", "ผศ.", value)
    value = re.sub(r"\bรศ\s*\.", "รศ.", value)
    value = re.sub(r"\bศ\s*\.", "ศ.", value)
    value = re.sub(r"\bอ\s*\.", "อ.", value)
    value = re.sub(r"\s*,\s*", ", ", value)
    value = re.sub(r"\s*-\s*", " - ", value)
    value = re.sub(r"\s+", " ", value)
    # Deduplicate repeated Thai diacritics caused by PDF extraction (e.g. ์์ → ์)
    value = re.sub("์{2,}", "์", value)  # thanthakat ์
    value = re.sub("็{2,}", "็", value)  # maitaikhu ็
    return value.strip()


def _normalize_pdf_room_name(value: str | None) -> str | None:
    if not value:
        return None
    compact = _compact_titles(value)
    if compact.lower() == "online":
        return "online"
    if compact.lower() == "auditorium50th":
        return "auditorium50th"
    compact = re.sub(r"(PSB)\s+(\d)\s+(\d{3})", r"\1 \2\3", compact, flags=re.IGNORECASE)
    normalized = normalize_room_code(compact)
    return normalized or compact


def _parse_thai_date(value: str) -> date | None:
    cleaned = _compact_titles(value)
    match = re.search(r"วัน[^\d]*(\d{1,2})\s+([ก-๙]+)\s+(\d{4})", cleaned)
    if not match:
        return None
    day = int(match.group(1))
    month = THAI_MONTHS.get(match.group(2))
    year_be = int(match.group(3))
    if not month:
        return None
    return date(year_be - 543, month, day)


def _extract_display_time(value: str | None) -> tuple[str | None, str | None, str | None]:
    if not value:
        return None, None, None
    match = TIME_RE.search(value)
    if not match:
        return None, None, None
    start = match.group("start")
    end = match.group("end")
    return f"{start} - {end} น.", start.replace(".", ":"), end.replace(".", ":")


def _build_positioned_bands(pdf_path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(pdf_path))
    bands: list[dict[str, Any]] = []
    for page_index, page in enumerate(reader.pages):
        items: list[tuple[float, float, str]] = []

        def visitor(text: str, cm: Any, tm: Any, font_dict: Any, font_size: Any):
            cleaned = text.strip()
            if cleaned:
                items.append((float(tm[4]), float(tm[5]), cleaned))

        page.extract_text(visitor_text=visitor)
        grouped: list[dict[str, Any]] = []
        for x, y, text in sorted(items, key=lambda item: (-item[1], item[0])):
            target = next((band for band in grouped if abs(band["y"] - y) <= 1.3), None)
            if target is None:
                target = {"y": y, "items": []}
                grouped.append(target)
            target["items"].append((x, text))

        for band in sorted(grouped, key=lambda item: -item["y"]):
            columns = defaultdict(list)
            for x, text in sorted(band["items"], key=lambda item: item[0]):
                if x < PDF_COLUMN_BOUNDS["left"]:
                    columns["left"].append(text)
                elif x < PDF_COLUMN_BOUNDS["course"]:
                    columns["course"].append(text)
                elif x < PDF_COLUMN_BOUNDS["teacher"]:
                    columns["teacher"].append(text)
                elif x < PDF_COLUMN_BOUNDS["count"]:
                    columns["count"].append(text)
                elif x < PDF_COLUMN_BOUNDS["room"]:
                    columns["room"].append(text)
                elif x < PDF_COLUMN_BOUNDS["inv"]:
                    columns["inv"].append(text)
                else:
                    columns["dist"].append(text)
            row = {key: _compact_titles(" ".join(columns.get(key, []))) for key in ("left", "course", "teacher", "count", "room", "inv", "dist")}
            if row["left"].startswith("วัน") and re.fullmatch(r"\d{4}", row["course"] or ""):
                row["left"] = _compact_titles(f"{row['left']} {row['course']}")
                row["course"] = ""
            if row["teacher"].startswith("( ร่าง)") or row["teacher"].startswith("(ร่าง)"):
                continue
            row["page_index"] = page_index
            row["y"] = band["y"]
            bands.append(row)
    return bands


def _extract_count_and_room(count_text: str | None, room_text: str | None) -> tuple[int, str | None]:
    count_candidate = _compact_titles(count_text)
    room_candidate = _normalize_pdf_room_name(room_text)
    if count_candidate:
        direct_match = re.match(r"^(?P<count>\d+)\s+(?P<room>.+)$", count_candidate)
        if direct_match and not room_candidate:
            return int(direct_match.group("count")), _normalize_pdf_room_name(direct_match.group("room"))
        count_only = re.search(r"\d+", count_candidate)
        if count_only:
            return int(count_only.group(0)), room_candidate
    return 0, room_candidate


def _split_fragment_by_titles(fragment: str) -> list[str]:
    text = _compact_titles(fragment)
    if not text:
        return []
    positions = [match.start() for match in TITLE_START_RE.finditer(text)]
    if len(positions) <= 1:
        return [text]
    values: list[str] = []
    for index, start in enumerate(positions):
        end = positions[index + 1] if index + 1 < len(positions) else len(text)
        piece = _compact_titles(text[start:end])
        if piece:
            values.append(piece)
    return values


def _split_invigilator_names(raw_value: str | None) -> list[str]:
    text = _compact_titles(raw_value)
    if not text or text == "-":
        return []
    if text in _COLUMN_HEADER_TEXT:
        return []
    pieces: list[str] = []
    for dash_part in re.split(r"\s+-\s+", text):
        for comma_part in [part.strip() for part in dash_part.split(",")]:
            if not comma_part:
                continue
            pieces.extend(_split_fragment_by_titles(comma_part))
    results: list[str] = []
    for piece in pieces:
        cleaned = _compact_titles(piece)
        if cleaned and cleaned not in results and cleaned not in _COLUMN_HEADER_TEXT:
            results.append(cleaned)
    return results


def _parse_distribution_pair(raw_value: str | None) -> tuple[str | None, str | None]:
    text = _compact_titles(raw_value)
    if not text or text == "-":
        return None, None
    parts = [part.strip() for part in re.split(r"\s+-\s+", text, maxsplit=1)]
    if len(parts) == 2:
        return parts[0] or None, parts[1] or None
    return parts[0] or None, None


def _resolve_section_refs(
    db: Session,
    semester: str,
    academic_year: str,
    course_code: str,
    section_no: str,
) -> tuple[int | None, int | None, int | None]:
    course = db.query(models.Course).filter(models.Course.course_id == course_code).first()
    if not course:
        return None, None, None
    section = db.query(models.Section).filter(
        models.Section.course_id == course.id,
        models.Section.section_no == section_no,
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).first()
    return course.id, section.id if section else None, section.teacher_id if section and section.teacher_id else None


def _classify_invigilator(
    raw_name: str,
    instructor_name: str,
    resolver: NameResolver,
    instructor_user_id: int | None = None,
) -> ParsedInvigilator:
    normalized = normalize_person_name(raw_name)
    resolved_user = resolver.resolve_user(raw_name)
    instructor_normalized = normalize_person_name(instructor_name)
    is_instructor_name = bool(
        normalized
        and instructor_normalized
        and (
            normalized == instructor_normalized
            or instructor_normalized.startswith(normalized)
            or normalized.startswith(instructor_normalized)
        )
    )
    if is_instructor_name:
        role_kind = models.HistoricalInvigilatorKind.instructor_invigilator
        # If direct name lookup failed (abbreviated name), fall back to the known section teacher.
        user_id = resolved_user.id if resolved_user else instructor_user_id
    elif resolved_user and resolved_user.role == models.UserRole.staff:
        role_kind = models.HistoricalInvigilatorKind.staff_invigilator
        user_id = resolved_user.id
    elif resolved_user and resolved_user.role in {models.UserRole.teacher, models.UserRole.admin, models.UserRole.dept_supervisor}:
        role_kind = models.HistoricalInvigilatorKind.instructor_invigilator
        user_id = resolved_user.id
    else:
        role_kind = models.HistoricalInvigilatorKind.unknown_invigilator
        user_id = resolved_user.id if resolved_user else None
    return ParsedInvigilator(
        display_name=_compact_titles(raw_name),
        normalized_name=normalized,
        user_id=user_id,
        role_kind=role_kind,
        notes=None if user_id else "unresolved_name",
    )


def get_room_opening_candidates(db: Session) -> list[models.User]:
    return db.query(models.User).filter(
        models.User.special_role == "room_keeper",
        models.User.is_active == True,
    ).order_by(models.User.username).all()


def get_room_opening_start_username(db: Session) -> str:
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == ROOM_OPENING_START_SETTING_KEY).first()
    if setting and setting.value:
        return setting.value
    candidates = get_room_opening_candidates(db)
    if any(candidate.username == DEFAULT_ROOM_OPENING_START_USERNAME for candidate in candidates):
        return DEFAULT_ROOM_OPENING_START_USERNAME
    return candidates[0].username if candidates else DEFAULT_ROOM_OPENING_START_USERNAME


def set_room_opening_start_username(db: Session, username: str, actor_id: int | None = None) -> str:
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.special_role == "room_keeper",
        models.User.is_active == True,
    ).first()
    if not user:
        raise ValueError("Invalid room-opening user")
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == ROOM_OPENING_START_SETTING_KEY).first()
    if not setting:
        setting = models.SystemSetting(key=ROOM_OPENING_START_SETTING_KEY)
        db.add(setting)
    setting.value = username
    setting.description = "Starting room-opening staff rotation for historical schedule parsing fallback."
    setting.updated_by = actor_id
    db.flush()
    return username


def _room_opening_fallback_for_date(
    exam_date: date,
    sorted_dates: list[date],
    candidates: list[models.User],
    start_username: str,
) -> tuple[str | None, int | None]:
    if len(candidates) < 2:
        if candidates:
            return candidates[0].full_name, candidates[0].id
        return None, None
    by_username = {candidate.username: candidate for candidate in candidates}
    starter = by_username.get(start_username) or candidates[0]
    second = next(candidate for candidate in candidates if candidate.id != starter.id)
    index = sorted_dates.index(exam_date)
    choice = starter if index % 2 == 0 else second
    return choice.full_name, choice.id


def _parse_pdf_snapshot(
    db: Session,
    pdf_path: Path,
    version_kind: models.HistoricalScheduleVersion,
    semester: str,
    academic_year: str,
    exam_type: str,
    room_opening_start_username: str,
) -> tuple[list[ParsedEntry], dict[tuple[date, str], ParsedDistributionSlot], list[str]]:
    bands = _build_positioned_bands(pdf_path)
    rows: list[ParsedEntry] = []
    slot_distribution_raw: dict[tuple[date, str], str] = {}
    parse_log: list[str] = []
    current_date: date | None = None
    current_time: str | None = None
    current_start: str | None = None
    current_end: str | None = None
    current_slot: tuple[date, str] | None = None
    pending: ParsedEntry | None = None
    last_room: str | None = None
    last_invigilators: str | None = None
    row_order = 0

    def finalize_pending() -> None:
        nonlocal pending
        if not pending:
            return
        if not pending.room_name and last_room:
            pending.room_name = last_room
            pending.inherited_room = True
            pending.parse_flags.append("inherited_room")
        if not pending.invigilators_raw and last_invigilators:
            pending.invigilators_raw = last_invigilators
            pending.inherited_invigilators = True
            pending.parse_flags.append("inherited_invigilators")
        if not pending.room_name and pending.course_code != "140104":
            pending.parse_flags.append("missing_room")
        if not pending.invigilators_raw:
            pending.parse_flags.append("missing_invigilators")
        rows.append(pending)
        pending = None

    for band in bands:
        left_text = band["left"]
        course_text = band["course"]
        if left_text.startswith("วัน/"):
            continue
        detected_date = _parse_thai_date(left_text)
        if detected_date:
            finalize_pending()
            current_date = detected_date
            current_time = None
            current_start = None
            current_end = None
            current_slot = None
            last_room = None
            last_invigilators = None
            continue

        detected_time, start_time, end_time = _extract_display_time(left_text)
        if detected_time:
            finalize_pending()
            current_time = detected_time
            current_start = start_time
            current_end = end_time
            current_slot = (current_date, current_time) if current_date else None
            last_room = None
            last_invigilators = None

        if band["dist"] and current_slot:
            slot_distribution_raw[current_slot] = band["dist"]

        course_match = COURSE_ROW_RE.match(course_text or "")
        if not course_match:
            # Skip repeating table header rows (detected by course column text)
            if _compact_titles(course_text or "").casefold() in {h.casefold() for h in _COURSE_HEADER_TEXT}:
                continue
            if pending and (band["room"] or band["inv"]):
                supplemental_room = _normalize_pdf_room_name(band["room"])
                supplemental_inv = _compact_titles(band["inv"])
                if supplemental_room:
                    pending.room_name = supplemental_room
                    last_room = supplemental_room
                if supplemental_inv and supplemental_inv not in _COLUMN_HEADER_TEXT:
                    pending.invigilators_raw = supplemental_inv
                    last_invigilators = supplemental_inv
            continue

        finalize_pending()
        row_order += 1
        if not current_date or not current_time:
            parse_log.append(f"row_without_slot:{course_match.group('course')} Sec {course_match.group('section')}")
            continue

        student_count, room_name = _extract_count_and_room(band["count"], band["room"])
        invigilators_raw = _compact_titles(band["inv"]) or None
        if room_name:
            last_room = room_name
        if invigilators_raw:
            last_invigilators = invigilators_raw

        pending = ParsedEntry(
            row_order=row_order,
            exam_date=current_date,
            exam_time=current_time,
            exam_time_start=current_start,
            exam_time_end=current_end,
            course_code=course_match.group("course"),
            section_no=course_match.group("section"),
            instructor_name=_compact_titles(band["teacher"]),
            student_count=student_count,
            room_name=room_name,
            invigilators_raw=invigilators_raw,
        )

    finalize_pending()

    room_opening_candidates = get_room_opening_candidates(db)
    sorted_dates = sorted({entry.exam_date for entry in rows})
    resolver = NameResolver(db)
    slot_assignments: dict[tuple[date, str], ParsedDistributionSlot] = {}
    rows_by_slot: dict[tuple[date, str], list[ParsedEntry]] = defaultdict(list)
    for entry in rows:
        rows_by_slot[(entry.exam_date, entry.exam_time)].append(entry)

    for slot_key, slot_rows in rows_by_slot.items():
        raw_value = slot_distribution_raw.get(slot_key)
        paper_name, room_name = _parse_distribution_pair(raw_value)
        source_mode = "imported"
        room_user = resolver.resolve_user(room_name) if room_name else None
        if not room_name:
            fallback_name, fallback_id = _room_opening_fallback_for_date(slot_key[0], sorted_dates, room_opening_candidates, room_opening_start_username)
            room_name = fallback_name
            room_user = db.query(models.User).filter(models.User.id == fallback_id).first() if fallback_id else None
            if fallback_name:
                source_mode = "fallback_rotation"
        paper_user = resolver.resolve_user(paper_name) if paper_name else None
        slot_assignments[slot_key] = ParsedDistributionSlot(
            exam_date=slot_key[0],
            exam_time=slot_key[1],
            exam_time_start=slot_rows[0].exam_time_start,
            exam_time_end=slot_rows[0].exam_time_end,
            raw_value=raw_value,
            paper_distribution_staff_name=paper_name,
            room_opening_staff_name=room_name,
            paper_distribution_user_id=paper_user.id if paper_user else None,
            room_opening_user_id=room_user.id if room_user else None,
            source_mode=source_mode,
            covered_courses=[f"{row.course_code} Sec {row.section_no}" for row in slot_rows],
            covered_rooms=sorted({row.room_name for row in slot_rows if row.room_name}),
            covered_row_count=len(slot_rows),
            notes=None if raw_value else "missing_distribution_raw",
        )
        for row in slot_rows:
            row.distribution_raw = raw_value
            row.paper_distribution_staff_name = paper_name
            row.room_opening_staff_name = room_name
            if raw_value:
                row.inherited_distribution = True
            elif room_name:
                row.parse_flags.append("room_opening_fallback")

        if not paper_name and any(row.room_name != "online" for row in slot_rows):
            parse_log.append(f"missing_paper_distribution:{slot_key[0]} {slot_key[1]}")

    for row in rows:
        course_ref_id, section_ref_id, teacher_ref_id = _resolve_section_refs(
            db,
            semester=semester,
            academic_year=academic_year,
            course_code=row.course_code,
            section_no=row.section_no,
        )
        row.course_ref_id = course_ref_id
        row.section_ref_id = section_ref_id
        row.teacher_ref_id = teacher_ref_id

        classifications = [
            _classify_invigilator(name, row.instructor_name, resolver, instructor_user_id=row.teacher_ref_id)
            for name in _split_invigilator_names(row.invigilators_raw)
        ]
        unresolved = [item.display_name for item in classifications if item.user_id is None]
        if unresolved:
            row.parse_flags.append(f"unresolved_invigilators:{', '.join(unresolved)}")

    return rows, slot_assignments, parse_log


def _serialize_flags(flags: Iterable[str]) -> list[str] | None:
    unique = []
    for flag in flags:
        if flag and flag not in unique:
            unique.append(flag)
    return unique or None


def import_historical_schedule_snapshot(
    db: Session,
    pdf_path: str | Path,
    version_kind: models.HistoricalScheduleVersion,
    source_label: str,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
    imported_by: int | None = None,
    room_opening_start_username: str | None = None,
) -> models.HistoricalScheduleBatch:
    source_path = Path(pdf_path).expanduser().resolve()
    raw_bytes = source_path.read_bytes()
    checksum = sha256(raw_bytes).hexdigest()
    room_opening_start_username = room_opening_start_username or get_room_opening_start_username(db)
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.semester == semester,
        models.ExamPeriod.academic_year == academic_year,
        models.ExamPeriod.exam_type == exam_type,
    ).first()

    rows, slot_assignments, parse_log = _parse_pdf_snapshot(
        db=db,
        pdf_path=source_path,
        version_kind=version_kind,
        semester=semester,
        academic_year=academic_year,
        exam_type=exam_type,
        room_opening_start_username=room_opening_start_username,
    )

    existing = db.query(models.HistoricalScheduleBatch).filter(
        models.HistoricalScheduleBatch.semester == semester,
        models.HistoricalScheduleBatch.academic_year == academic_year,
        models.HistoricalScheduleBatch.exam_type == exam_type,
        models.HistoricalScheduleBatch.version_kind == version_kind,
        models.HistoricalScheduleBatch.source_checksum == checksum,
    ).first()
    if existing:
        db.delete(existing)
        db.flush()

    batch = models.HistoricalScheduleBatch(
        exam_period_id=period.id if period else None,
        semester=semester,
        academic_year=academic_year,
        exam_type=exam_type,
        version_kind=version_kind,
        source_label=source_label,
        source_filename=source_path.name,
        source_checksum=checksum,
        room_opening_start_username=room_opening_start_username,
        imported_by=imported_by,
        row_count=len(rows),
        manual_review_count=sum(1 for row in rows if row.parse_flags),
        parse_log=parse_log,
    )
    db.add(batch)
    db.flush()

    resolver = NameResolver(db)
    for row in rows:
        entry = models.HistoricalScheduleEntry(
            batch_id=batch.id,
            course_ref_id=row.course_ref_id,
            section_ref_id=row.section_ref_id,
            teacher_ref_id=row.teacher_ref_id,
            row_order=row.row_order,
            exam_date=row.exam_date,
            exam_time=row.exam_time,
            exam_time_start=row.exam_time_start,
            exam_time_end=row.exam_time_end,
            course_code=row.course_code,
            section_no=row.section_no,
            instructor_name=row.instructor_name,
            student_count=row.student_count,
            room_name=row.room_name,
            invigilators_raw=row.invigilators_raw,
            distribution_raw=row.distribution_raw,
            paper_distribution_staff_name=row.paper_distribution_staff_name,
            room_opening_staff_name=row.room_opening_staff_name,
            inherited_room=row.inherited_room,
            inherited_invigilators=row.inherited_invigilators,
            inherited_distribution=row.inherited_distribution,
            parse_flags=_serialize_flags(row.parse_flags),
        )
        db.add(entry)
        db.flush()

        for order_index, name in enumerate(_split_invigilator_names(row.invigilators_raw), start=1):
            classification = _classify_invigilator(name, row.instructor_name, resolver, instructor_user_id=row.teacher_ref_id)
            db.add(
                models.HistoricalScheduleInvigilator(
                    batch_id=batch.id,
                    entry_id=entry.id,
                    user_id=classification.user_id,
                    order_index=order_index,
                    display_name=classification.display_name,
                    normalized_name=classification.normalized_name,
                    role_kind=classification.role_kind,
                    counted=True,
                    notes=classification.notes,
                )
            )

    for slot in slot_assignments.values():
        db.add(
            models.HistoricalDistributionSlot(
                batch_id=batch.id,
                paper_distribution_user_id=slot.paper_distribution_user_id,
                room_opening_user_id=slot.room_opening_user_id,
                exam_date=slot.exam_date,
                exam_time=slot.exam_time,
                exam_time_start=slot.exam_time_start,
                exam_time_end=slot.exam_time_end,
                paper_distribution_staff_name=slot.paper_distribution_staff_name,
                room_opening_staff_name=slot.room_opening_staff_name,
                raw_value=slot.raw_value,
                source_mode=slot.source_mode,
                workload_count=1,
                counted=True,
                covered_courses=slot.covered_courses,
                covered_rooms=slot.covered_rooms,
                covered_row_count=slot.covered_row_count,
                notes=slot.notes,
            )
        )

    db.flush()
    return batch


def get_latest_batch(
    db: Session,
    version_kind: models.HistoricalScheduleVersion,
    semester: str = "2",
    academic_year: str = "2568",
    exam_type: str = "final",
) -> models.HistoricalScheduleBatch | None:
    return db.query(models.HistoricalScheduleBatch).filter(
        models.HistoricalScheduleBatch.semester == semester,
        models.HistoricalScheduleBatch.academic_year == academic_year,
        models.HistoricalScheduleBatch.exam_type == exam_type,
        models.HistoricalScheduleBatch.version_kind == version_kind,
    ).order_by(models.HistoricalScheduleBatch.imported_at.desc(), models.HistoricalScheduleBatch.id.desc()).first()


def serialize_batch_summary(batch: models.HistoricalScheduleBatch | None) -> dict[str, Any] | None:
    if not batch:
        return None
    return {
        "id": batch.id,
        "version_kind": batch.version_kind.value if batch.version_kind else None,
        "source_label": batch.source_label,
        "source_filename": batch.source_filename,
        "semester": batch.semester,
        "academic_year": batch.academic_year,
        "exam_type": batch.exam_type,
        "room_opening_start_username": batch.room_opening_start_username,
        "row_count": batch.row_count,
        "manual_review_count": batch.manual_review_count,
        "imported_at": batch.imported_at.isoformat() if batch.imported_at else None,
        "parse_log": batch.parse_log or [],
    }


def build_schedule_rows(batch: models.HistoricalScheduleBatch) -> list[dict[str, Any]]:
    rows = []
    for entry in sorted(batch.entries, key=lambda item: (item.exam_date, item.exam_time, item.row_order)):
        rows.append(
            {
                "id": entry.id,
                "exam_date": entry.exam_date.isoformat(),
                "exam_time": entry.exam_time,
                "course_code": entry.course_code,
                "section_no": entry.section_no,
                "instructor_name": entry.instructor_name,
                "student_count": entry.student_count,
                "room_name": entry.room_name,
                "invigilators_raw": entry.invigilators_raw,
                "distribution_raw": entry.distribution_raw,
                "paper_distribution_staff_name": entry.paper_distribution_staff_name,
                "room_opening_staff_name": entry.room_opening_staff_name,
                "parse_flags": entry.parse_flags or [],
                "invigilators": [
                    {
                        "display_name": inv.display_name,
                        "role_kind": inv.role_kind.value if inv.role_kind else None,
                        "user_id": inv.user_id,
                    }
                    for inv in entry.invigilators
                ],
            }
        )
    return rows


def build_distribution_rows(batch: models.HistoricalScheduleBatch) -> list[dict[str, Any]]:
    rows = []
    for slot in sorted(batch.distribution_slots, key=lambda item: (item.exam_date, item.exam_time)):
        rows.append(
            {
                "id": slot.id,
                "exam_date": slot.exam_date.isoformat(),
                "exam_time": slot.exam_time,
                "paper_distribution_staff_name": slot.paper_distribution_staff_name,
                "room_opening_staff_name": slot.room_opening_staff_name,
                "paper_distribution_user_id": slot.paper_distribution_user_id,
                "room_opening_user_id": slot.room_opening_user_id,
                "raw_value": slot.raw_value,
                "source_mode": slot.source_mode,
                "covered_courses": slot.covered_courses or [],
                "covered_rooms": slot.covered_rooms or [],
                "covered_row_count": slot.covered_row_count,
                "counted_or_not_counted": {
                    "paper_distribution": True,
                    "room_opening": False,
                },
                "notes": slot.notes,
            }
        )
    return rows


def build_workload_rows(batch: models.HistoricalScheduleBatch) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in batch.entries:
        for inv in entry.invigilators:
            rows.append(
                {
                    "person_name": inv.display_name,
                    "user_id": inv.user_id,
                    "duty_type": models.StaffDutyType.invigilation.value,
                    "date": entry.exam_date.isoformat(),
                    "time_slot": entry.exam_time,
                    "courses_covered": [f"{entry.course_code} Sec {entry.section_no}"],
                    "rooms": [entry.room_name] if entry.room_name else [],
                    "workload_count": 1,
                    "counted_or_not_counted": True,
                    "source_file": batch.source_filename,
                    "version_kind": batch.version_kind.value,
                    "role_kind": inv.role_kind.value if inv.role_kind else None,
                }
            )
    for slot in batch.distribution_slots:
        if slot.paper_distribution_staff_name:
            rows.append(
                {
                    "person_name": slot.paper_distribution_staff_name,
                    "user_id": slot.paper_distribution_user_id,
                    "duty_type": models.StaffDutyType.paper_distribution.value,
                    "date": slot.exam_date.isoformat(),
                    "time_slot": slot.exam_time,
                    "courses_covered": slot.covered_courses or [],
                    "rooms": slot.covered_rooms or [],
                    "workload_count": 1,
                    "counted_or_not_counted": True,
                    "source_file": batch.source_filename,
                    "version_kind": batch.version_kind.value,
                    "role_kind": "paper_distribution_staff",
                }
            )
        if slot.room_opening_staff_name:
            rows.append(
                {
                    "person_name": slot.room_opening_staff_name,
                    "user_id": slot.room_opening_user_id,
                    "duty_type": models.StaffDutyType.room_opening.value,
                    "date": slot.exam_date.isoformat(),
                    "time_slot": slot.exam_time,
                    "courses_covered": slot.covered_courses or [],
                    "rooms": slot.covered_rooms or [],
                    "workload_count": 0,
                    "counted_or_not_counted": False,
                    "source_file": batch.source_filename,
                    "version_kind": batch.version_kind.value,
                    "role_kind": "room_opening_staff",
                }
            )
    rows.sort(key=lambda item: (item["date"], item["time_slot"], item["person_name"], item["duty_type"]))
    return rows


def build_workload_summary(batch: models.HistoricalScheduleBatch) -> list[dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for row in build_workload_rows(batch):
        person = row["person_name"]
        record = summary.setdefault(
            person,
            {
                "person_name": person,
                "user_id": row["user_id"],
                "invigilation_count": 0,
                "paper_distribution_count": 0,
                "room_opening_count": 0,
                "total_counted_workload": 0,
                "assignments": [],
            },
        )
        if row["duty_type"] == models.StaffDutyType.invigilation.value:
            record["invigilation_count"] += 1
        elif row["duty_type"] == models.StaffDutyType.paper_distribution.value:
            record["paper_distribution_count"] += 1
        elif row["duty_type"] == models.StaffDutyType.room_opening.value:
            record["room_opening_count"] += 1
        if row["counted_or_not_counted"]:
            record["total_counted_workload"] += row["workload_count"]
        record["assignments"].append(row)
    return sorted(summary.values(), key=lambda item: (-item["total_counted_workload"], item["person_name"]))


def build_difference_rows(
    baseline_batch: models.HistoricalScheduleBatch | None,
    final_batch: models.HistoricalScheduleBatch | None,
) -> list[dict[str, Any]]:
    baseline_rows = _index_entries_for_comparison(baseline_batch.entries if baseline_batch else [])
    final_rows = _index_entries_for_comparison(final_batch.entries if final_batch else [])
    keys = sorted(set(baseline_rows) | set(final_rows))
    differences: list[dict[str, Any]] = []

    def _norm_text(value: str | None) -> str:
        return _compact_titles(value or "")

    for key in keys:
        baseline = baseline_rows.get(key)
        final = final_rows.get(key)
        key_string = "|".join([key[0], key[1], key[2], key[3], str(key[4])])
        if not baseline:
            differences.append(
                {
                    "key": key_string,
                    "status": "added_in_final",
                    "course_code": final.course_code if final else key[0],
                    "section_no": final.section_no if final else key[1],
                    "exam_date": key[2],
                    "exam_time": key[3],
                    "changes": ["added_course_row"],
                    "baseline": None,
                    "final": _serialize_entry_for_compare(final),
                }
            )
            continue
        if not final:
            differences.append(
                {
                    "key": key_string,
                    "status": "removed_in_final",
                    "course_code": baseline.course_code,
                    "section_no": baseline.section_no,
                    "exam_date": key[2],
                    "exam_time": key[3],
                    "changes": ["removed_course_row"],
                    "baseline": _serialize_entry_for_compare(baseline),
                    "final": None,
                }
            )
            continue
        changes: list[str] = []
        if baseline.student_count != final.student_count:
            changes.append("student_count_changed")
        if _norm_text(baseline.room_name) != _norm_text(final.room_name):
            changes.append("room_changed")
        if _norm_text(baseline.invigilators_raw) != _norm_text(final.invigilators_raw):
            changes.append("invigilator_changed")
        if _norm_text(baseline.paper_distribution_staff_name) != _norm_text(final.paper_distribution_staff_name):
            changes.append("paper_distribution_staff_changed")
        if _norm_text(baseline.room_opening_staff_name) != _norm_text(final.room_opening_staff_name):
            changes.append("room_opening_staff_changed")
        if _norm_text(baseline.instructor_name) != _norm_text(final.instructor_name):
            changes.append("instructor_changed")
        if changes:
            differences.append(
                {
                    "key": key_string,
                    "status": "changed",
                    "course_code": final.course_code,
                    "section_no": final.section_no,
                    "exam_date": key[2],
                    "exam_time": key[3],
                    "changes": changes,
                    "baseline": _serialize_entry_for_compare(baseline),
                    "final": _serialize_entry_for_compare(final),
                }
            )
    return differences


def _index_entries_for_comparison(entries: Iterable[models.HistoricalScheduleEntry]) -> dict[tuple[str, str, str, str, int], models.HistoricalScheduleEntry]:
    grouped: dict[tuple[str, str, str, str], list[models.HistoricalScheduleEntry]] = defaultdict(list)
    for entry in entries:
        grouped[(entry.course_code, entry.section_no, entry.exam_date.isoformat(), entry.exam_time)].append(entry)
    indexed: dict[tuple[str, str, str, str, int], models.HistoricalScheduleEntry] = {}
    for base_key, grouped_entries in grouped.items():
        for index, entry in enumerate(sorted(grouped_entries, key=lambda item: (item.row_order, item.room_name or "", item.student_count)), start=1):
            indexed[(*base_key, index)] = entry
    return indexed


def _serialize_entry_for_compare(entry: models.HistoricalScheduleEntry | None) -> dict[str, Any] | None:
    if not entry:
        return None
    return {
        "course_code": entry.course_code,
        "section_no": entry.section_no,
        "instructor_name": entry.instructor_name,
        "student_count": entry.student_count,
        "room_name": entry.room_name,
        "invigilators_raw": entry.invigilators_raw,
        "paper_distribution_staff_name": entry.paper_distribution_staff_name,
        "room_opening_staff_name": entry.room_opening_staff_name,
    }
