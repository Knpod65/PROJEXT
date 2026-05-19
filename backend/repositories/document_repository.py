"""Document data access helpers.

This repository keeps the router/service free from direct query logic where
practical. All methods are intentionally read-only and side-effect free.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

import models


def load_schedule(db: Session, schedule_id: int) -> models.ExamSchedule | None:
    return (
        db.query(models.ExamSchedule)
        .options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        )
        .filter(models.ExamSchedule.id == schedule_id)
        .first()
    )


def load_published_schedules(
    db: Session,
    *,
    semester: str,
    academic_year: str,
    exam_type: models.ExamType,
) -> list[models.ExamSchedule]:
    return (
        db.query(models.ExamSchedule)
        .options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        )
        .join(models.Section)
        .filter(
            and_(
                models.Section.semester == semester,
                models.Section.academic_year == academic_year,
                models.ExamSchedule.exam_type == exam_type,
                models.ExamSchedule.status == models.ScheduleStatus.published,
            )
        )
        .order_by(models.ExamSchedule.exam_date, models.ExamSchedule.exam_time)
        .all()
    )


def load_submission(db: Session, submission_id: int) -> models.ExamSubmission | None:
    return (
        db.query(models.ExamSubmission)
        .options(
            joinedload(models.ExamSubmission.section).joinedload(models.Section.course),
            joinedload(models.ExamSubmission.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSubmission.material_request),
        )
        .filter(models.ExamSubmission.id == submission_id)
        .first()
    )


def load_submission_schedule(db: Session, section_id: int) -> models.ExamSchedule | None:
    return (
        db.query(models.ExamSchedule)
        .options(
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        )
        .filter(models.ExamSchedule.section_id == section_id)
        .first()
    )


def load_enrollment_records(db: Session, section_id: int) -> list[models.EnrollmentRecord]:
    return (
        db.query(models.EnrollmentRecord)
        .filter(models.EnrollmentRecord.section_id == section_id)
        .order_by(models.EnrollmentRecord.student_id, models.EnrollmentRecord.student_name)
        .all()
    )


def load_legacy_enrollments(db: Session, section_id: int) -> list[models.Enrollment]:
    return (
        db.query(models.Enrollment)
        .join(models.Student, models.Student.student_id == models.Enrollment.student_id)
        .filter(models.Enrollment.section_id == section_id)
        .order_by(models.Enrollment.student_id)
        .all()
    )


def load_period(db: Session, *, academic_year: Optional[str] = None, semester: Optional[str] = None, exam_type: Optional[str] = None) -> models.ExamPeriod | None:
    if academic_year and semester and exam_type:
        return (
            db.query(models.ExamPeriod)
            .filter(
                models.ExamPeriod.academic_year == str(academic_year),
                models.ExamPeriod.semester == str(semester),
                models.ExamPeriod.exam_type == str(exam_type),
            )
            .first()
        )
    return db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()


def load_export_schedules(
    db: Session,
    *,
    period: models.ExamPeriod,
    course_id: Optional[str] = None,
    section_no: Optional[str] = None,
    room_id: Optional[int] = None,
) -> list[models.ExamSchedule]:
    exam_type_enum = models.ExamType(period.exam_type)
    query = (
        db.query(models.ExamSchedule)
        .options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        )
        .join(models.Section)
        .join(models.Course)
        .filter(
            models.Section.academic_year == period.academic_year,
            models.Section.semester == period.semester,
            models.ExamSchedule.exam_type == exam_type_enum,
        )
    )
    if course_id:
        query = query.filter(models.Course.course_id == course_id.strip())
    if section_no:
        query = query.filter(models.Section.section_no == section_no.strip())
    if room_id is not None:
        query = query.filter(models.ExamSchedule.room_id == room_id)
    return query.order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time,
        models.Course.course_id,
        models.Section.section_no,
    ).all()
