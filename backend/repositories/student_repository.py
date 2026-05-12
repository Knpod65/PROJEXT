"""Student repository scaffolding for future public/profile service extraction."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload, selectinload

import models


def normalize_student_id(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True)
class StudentScheduleBundle:
    student: models.Student | None
    enrollment_records: list[models.EnrollmentRecord]
    legacy_enrollments: list[models.Enrollment]


class StudentRepository:
    """Repository wrapper around student/profile schedule queries."""

    def __init__(self, db: Session):
        self.db = db

    def get_basic_info(self, student_id: object) -> models.Student | None:
        normalized = normalize_student_id(student_id)
        if not normalized:
            return None
        return (
            self.db.query(models.Student)
            .filter(models.Student.student_id == normalized)
            .first()
        )

    def get_enrollment_records(
        self,
        student_id: object,
        active_period: models.ExamPeriod | None = None,
    ) -> list[models.EnrollmentRecord]:
        normalized = normalize_student_id(student_id)
        if not normalized:
            return []

        query = self.db.query(models.EnrollmentRecord).filter(
            models.EnrollmentRecord.student_id == normalized
        )

        if active_period:
            query = query.join(
                models.Section,
                models.EnrollmentRecord.section_id == models.Section.id,
            ).filter(
                models.Section.semester == active_period.semester,
                models.Section.academic_year == active_period.academic_year,
            )

        return query.options(
            joinedload(models.EnrollmentRecord.section)
            .joinedload(models.Section.course),
            joinedload(models.EnrollmentRecord.section)
            .joinedload(models.Section.teacher),
            joinedload(models.EnrollmentRecord.section)
            .selectinload(models.Section.schedules)
            .joinedload(models.ExamSchedule.room),
        ).order_by(
            models.EnrollmentRecord.import_session_id.desc(),
            models.EnrollmentRecord.id.desc(),
        ).all()

    def get_legacy_enrollments(
        self,
        student_id: object,
        active_period: models.ExamPeriod | None = None,
    ) -> list[models.Enrollment]:
        normalized = normalize_student_id(student_id)
        if not normalized:
            return []

        query = self.db.query(models.Enrollment).filter(
            models.Enrollment.student_id == normalized
        )

        if active_period:
            query = query.join(
                models.Section,
                models.Enrollment.section_id == models.Section.id,
            ).filter(
                models.Section.semester == active_period.semester,
                models.Section.academic_year == active_period.academic_year,
            )

        return query.options(
            joinedload(models.Enrollment.section)
            .joinedload(models.Section.course),
            joinedload(models.Enrollment.section)
            .joinedload(models.Section.teacher),
            joinedload(models.Enrollment.section)
            .selectinload(models.Section.schedules)
            .joinedload(models.ExamSchedule.room),
            joinedload(models.Enrollment.student),
        ).order_by(models.Enrollment.id.desc()).all()

    def get_all_info(
        self,
        student_id: object,
        active_period: models.ExamPeriod | None = None,
    ) -> StudentScheduleBundle:
        normalized = normalize_student_id(student_id)
        if not normalized:
            return StudentScheduleBundle(
                student=None,
                enrollment_records=[],
                legacy_enrollments=[],
            )

        return StudentScheduleBundle(
            student=self.get_basic_info(normalized),
            enrollment_records=self.get_enrollment_records(normalized, active_period),
            legacy_enrollments=self.get_legacy_enrollments(normalized, active_period),
        )
