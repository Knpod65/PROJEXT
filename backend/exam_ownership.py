from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Sequence

from sqlalchemy.orm import Session

import models

OWNER_SOURCE_AUTO = "auto"
OWNER_SOURCE_MANUAL = "manual"
OWNER_SOURCES = {OWNER_SOURCE_AUTO, OWNER_SOURCE_MANUAL}
SUPPORTED_EXAM_TYPES = ("midterm", "final")


def normalize_owner_exam_type(value: object) -> str:
    if isinstance(value, models.ExamType):
        return value.value

    text = str(value or "").strip().lower()
    if text not in SUPPORTED_EXAM_TYPES:
        raise ValueError(f"Unsupported exam type: {value!r}")
    return text


def get_active_exam_period(
    db: Session,
    semester: str | None = None,
    academic_year: str | None = None,
) -> models.ExamPeriod | None:
    query = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True)
    if semester:
        query = query.filter(models.ExamPeriod.semester == str(semester))
    if academic_year:
        query = query.filter(models.ExamPeriod.academic_year == str(academic_year))
    return query.order_by(models.ExamPeriod.id.desc()).first()


def get_active_exam_type(
    db: Session,
    semester: str | None = None,
    academic_year: str | None = None,
) -> str | None:
    period = get_active_exam_period(db, semester=semester, academic_year=academic_year)
    return period.exam_type if period else None


def get_assignment_status(owner: models.SectionExamManager | None) -> str:
    if not owner:
        return "needs_attention"
    if not owner.confirmed:
        return "pending"
    if (owner.assignment_source or OWNER_SOURCE_MANUAL) == OWNER_SOURCE_AUTO:
        return "auto_assigned"
    return "manual_assigned"


def build_owner_map(
    db: Session,
    sections: Sequence[models.Section],
    exam_types: Iterable[str],
    *,
    auto_create: bool = False,
    actor_id: int | None = None,
) -> tuple[dict[tuple[int, str], models.SectionExamManager], int]:
    section_ids = [section.id for section in sections]
    normalized_exam_types = [normalize_owner_exam_type(item) for item in exam_types]

    if not section_ids or not normalized_exam_types:
        return {}, 0

    owners = db.query(models.SectionExamManager).filter(
        models.SectionExamManager.section_id.in_(section_ids),
        models.SectionExamManager.exam_type.in_(normalized_exam_types),
    ).all()

    owner_map = {
        (owner.section_id, normalize_owner_exam_type(owner.exam_type)): owner
        for owner in owners
    }
    created = 0

    if auto_create:
        for section in sections:
            if not section.teacher_id:
                continue
            for exam_type in normalized_exam_types:
                key = (section.id, exam_type)
                if key in owner_map:
                    continue
                owner = models.SectionExamManager(
                    section_id=section.id,
                    exam_type=exam_type,
                    manager_id=section.teacher_id,
                    proposed_by=section.teacher_id,
                    confirmed=True,
                    confirmed_by=actor_id or section.teacher_id,
                    confirmed_at=datetime.now(timezone.utc),
                    note="Auto-assigned from imported teaching ownership.",
                    assignment_source=OWNER_SOURCE_AUTO,
                )
                db.add(owner)
                db.flush()
                owner_map[key] = owner
                created += 1

    return owner_map, created


def get_section_owner(
    db: Session,
    section: models.Section,
    exam_type: str,
    *,
    auto_create: bool = False,
    actor_id: int | None = None,
) -> models.SectionExamManager | None:
    owner_map, created = build_owner_map(
        db,
        [section],
        [exam_type],
        auto_create=auto_create,
        actor_id=actor_id,
    )
    if created:
        db.commit()
    return owner_map.get((section.id, normalize_owner_exam_type(exam_type)))


def get_teacher_owned_section_ids(
    db: Session,
    teacher_id: int,
    semester: str,
    academic_year: str,
) -> tuple[list[int] | None, str | None]:
    exam_type = get_active_exam_type(db, semester=semester, academic_year=academic_year)
    if not exam_type:
        return None, None

    sections = db.query(models.Section).filter(
        models.Section.semester == str(semester),
        models.Section.academic_year == str(academic_year),
    ).all()

    owner_map, created = build_owner_map(
        db,
        sections,
        [exam_type],
        auto_create=True,
        actor_id=teacher_id,
    )
    if created:
        db.commit()

    owned_ids = [
        section.id
        for section in sections
        if (owner := owner_map.get((section.id, exam_type)))
        and owner.confirmed
        and owner.manager_id == teacher_id
    ]
    return owned_ids, exam_type


def teacher_has_section_access(
    db: Session,
    teacher: models.User,
    section: models.Section | None,
) -> bool:
    if not section:
        return False

    exam_type = get_active_exam_type(
        db,
        semester=section.semester,
        academic_year=section.academic_year,
    )
    if not exam_type:
        return section.teacher_id == teacher.id

    owner = get_section_owner(
        db,
        section,
        exam_type,
        auto_create=True,
        actor_id=teacher.id,
    )
    return bool(owner and owner.confirmed and owner.manager_id == teacher.id)


def upsert_section_owner(
    db: Session,
    *,
    section: models.Section,
    exam_type: str,
    manager_id: int | None,
    actor_id: int,
    note: str | None = None,
    assignment_source: str = OWNER_SOURCE_MANUAL,
) -> models.SectionExamManager | None:
    normalized_exam_type = normalize_owner_exam_type(exam_type)
    normalized_source = assignment_source if assignment_source in OWNER_SOURCES else OWNER_SOURCE_MANUAL
    existing = db.query(models.SectionExamManager).filter(
        models.SectionExamManager.section_id == section.id,
        models.SectionExamManager.exam_type == normalized_exam_type,
    ).first()

    if manager_id is None:
        if existing:
            db.delete(existing)
        return None

    if existing:
        existing.manager_id = manager_id
        existing.proposed_by = actor_id
        existing.confirmed = True
        existing.confirmed_by = actor_id
        existing.confirmed_at = datetime.now(timezone.utc)
        existing.note = note
        existing.assignment_source = normalized_source
        return existing

    owner = models.SectionExamManager(
        section_id=section.id,
        exam_type=normalized_exam_type,
        manager_id=manager_id,
        proposed_by=actor_id,
        confirmed=True,
        confirmed_by=actor_id,
        confirmed_at=datetime.now(timezone.utc),
        note=note,
        assignment_source=normalized_source,
    )
    db.add(owner)
    db.flush()
    return owner
