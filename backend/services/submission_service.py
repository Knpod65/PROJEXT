"""
services/submission_service.py — Exam Submission domain logic
=============================================================
Pure service functions: no FastAPI imports, no Depends(), no HTTPException.
Callers (routers) translate EMSDomainError → HTTP responses.
All DB writes use db.flush(); commit belongs in the router.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

import models
from academic_groups import build_course_group_clause
from auth_utils import get_dept_filter, get_effective_role
from config.settings import settings
from exam_ownership import get_active_exam_period, get_teacher_owned_section_ids
from policies.submission_policy import (
    can_access_submission_messages,
    can_request_submission_download,
    can_teacher_access_section,
    is_submission_file_accessible,
    valid_print_staple_choices,
)
from repositories.submission_repository import SubmissionRepository
from services.exceptions import EMSNotFoundError, EMSPermissionError, EMSValidationError


# ── Snapshot ──────────────────────────────────────────────────────────────────

def snapshot_submission(sub: models.ExamSubmission) -> dict:
    """Return a plain-dict snapshot of all submission fields (for version history)."""
    return {
        "date_confirmed": sub.date_confirmed,
        "exam_type_choice": sub.exam_type_choice,
        "answer_formats": sub.answer_formats,
        "a4_pages_count": sub.a4_pages_count,
        "has_uploaded_pdf": sub.has_uploaded_pdf,
        "no_cover_page_confirmed": sub.no_cover_page_confirmed,
        "is_shared_exam": sub.is_shared_exam,
        "shared_with_sections": sub.shared_with_sections,
        "print_duplex": sub.print_duplex,
        "print_staple": sub.print_staple,
        "print_staple_page": sub.print_staple_page,
        "print_note": sub.print_note,
        "print_spec_confirmed": sub.print_spec_confirmed,
        "status": sub.status,
    }


# ── Version tracking ──────────────────────────────────────────────────────────

def save_version(
    db: Session,
    sub: models.ExamSubmission,
    user: models.User,
    reason: str = "",
) -> models.ExamSubmissionVersion:
    """Append a version record to submission history. Uses db.flush() only."""
    version_num = (
        db.query(models.ExamSubmissionVersion)
        .filter(models.ExamSubmissionVersion.submission_id == sub.id)
        .count()
    ) + 1
    ver = models.ExamSubmissionVersion(
        submission_id=sub.id,
        version=version_num,
        snapshot=snapshot_submission(sub),
        changed_by=user.id,
        change_reason=reason,
    )
    db.add(ver)
    sub.version = version_num
    return ver


# ── Print priority ────────────────────────────────────────────────────────────

def get_print_priority(submission: models.ExamSubmission) -> str:
    """
    Classify a submission as "high", "medium", or "standard".
    Thresholds driven by config.settings so they are environment-overridable.
    """
    section = submission.section
    students = section.num_students if section else 0
    pages = 0
    if submission.print_duplex and submission.a4_pages_count:
        pages = submission.a4_pages_count
    elif section and section.schedules:
        pages = max((schedule.num_pages or 0) for schedule in section.schedules)

    high = settings.print_priority_high_threshold    # default 120 students / 15 pages
    medium = settings.print_priority_medium_threshold  # default 70 students / 10 pages
    normal = settings.print_priority_normal_threshold  # default 15 pages (page gate)

    if students >= high or pages >= normal:
        return "high"
    if students >= medium or pages >= (normal * 2 // 3):
        return "medium"
    return "standard"


# ── Print queue ───────────────────────────────────────────────────────────────

def upsert_print_queue_job(
    db: Session,
    submission: models.ExamSubmission,
    created_by: models.User,
    release_token: str,
) -> models.PrintQueueJob:
    """
    Create or update the PrintQueueJob for a submission.
    Re-queues a delivered job (admin re-release workflow).
    Uses db.flush() only — commit is the router's responsibility.
    """
    job = (
        db.query(models.PrintQueueJob)
        .filter(models.PrintQueueJob.submission_id == submission.id)
        .first()
    )

    if not job:
        job = models.PrintQueueJob(
            submission_id=submission.id,
            created_by=created_by.id,
        )
        db.add(job)

    job.release_token = release_token
    job.priority = get_print_priority(submission)

    if job.status == models.PrintJobStatus.delivered:
        job.status = models.PrintJobStatus.queued
        job.started_at = None
        job.completed_at = None
        job.dispatched_at = None
        job.delivered_at = None
        job.delivery_note = None

    return job


def normalize_submission_list_inputs(page: int, limit: int) -> tuple[int, int]:
    """Clamp legacy list parameters while preserving current response behavior."""
    if limit > 200:
        limit = 200
    if page < 1:
        page = 1
    return page, limit


def get_or_create_submission(
    db: Session,
    repo: SubmissionRepository,
    section_id: int,
    user: models.User,
    create_if_missing: bool = True,
) -> models.ExamSubmission | None:
    """Return a submission for the section, optionally creating the draft row."""
    sub = repo.get_by_section_id(section_id)
    if sub or not create_if_missing:
        return sub

    section = repo.get_section(section_id)
    if not section:
        raise EMSNotFoundError("section")

    if get_effective_role(user) == models.UserRole.teacher and not can_teacher_access_section(db, user, section):
        raise EMSPermissionError("เธเธธเธ“เนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเธเธฑเธ”เธเธฒเธฃ section เธเธตเน")

    sub = models.ExamSubmission(
        section_id=section_id,
        submitted_by=user.id,
        status=models.SubmissionStatus.draft,
    )
    db.add(sub)
    db.flush()
    return sub


def serialize_submission_detail(sub: models.ExamSubmission | None, section_id: int) -> dict:
    if not sub:
        return {"exists": False, "section_id": section_id}

    return {
        "exists": True,
        "id": sub.id,
        "section_id": sub.section_id,
        "status": sub.status,
        "version": sub.version,
        "date_confirmed": sub.date_confirmed,
        "exam_type_choice": sub.exam_type_choice,
        "answer_formats": sub.answer_formats,
        "a4_pages_count": sub.a4_pages_count,
        "has_uploaded_pdf": sub.has_uploaded_pdf,
        "no_cover_page_confirmed": sub.no_cover_page_confirmed,
        "is_shared_exam": sub.is_shared_exam,
        "shared_with_sections": sub.shared_with_sections,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "approved_at": sub.approved_at.isoformat() if sub.approved_at else None,
        "rejected_reason": sub.rejected_reason,
        "admin_note": sub.admin_note,
        "course_name": sub.section.course.course_name_th if sub.section and sub.section.course else None,
        "versions": [
            {
                "version": version.version,
                "created_at": version.created_at.isoformat(),
                "reason": version.change_reason,
            }
            for version in (sub.versions or [])
        ],
    }


def get_submission_detail_for_section(
    db: Session,
    repo: SubmissionRepository,
    section_id: int,
    current_user: models.User,
) -> dict:
    sub = repo.get_detail_by_section_id(section_id)
    if not sub:
        return {"exists": False, "section_id": section_id}

    if get_effective_role(current_user) == models.UserRole.teacher:
        section = sub.section
        if section and not can_teacher_access_section(db, current_user, section):
            raise EMSPermissionError("เนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเธ”เธน submission เธเธตเน")

    return serialize_submission_detail(sub, section_id)


def serialize_submission_summary(sub: models.ExamSubmission) -> dict:
    return {
        "id": sub.id,
        "section_id": sub.section_id,
        "course_id": sub.section.course.course_id if sub.section and sub.section.course else None,
        "course_name": sub.section.course.course_name_th if sub.section and sub.section.course else None,
        "section_no": sub.section.section_no if sub.section else None,
        "status": sub.status,
        "version": sub.version,
        "exam_type_choice": sub.exam_type_choice,
        "has_uploaded_pdf": sub.has_uploaded_pdf,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "submitter": sub.submitter.full_name if sub.submitter else None,
    }


def list_submissions_overview(
    db: Session,
    repo: SubmissionRepository,
    current_user: models.User,
    status: str | None = None,
    page: int = 1,
    limit: int = 50,
) -> list[dict]:
    normalize_submission_list_inputs(page, limit)
    effective = get_effective_role(current_user)
    dept_filter = get_dept_filter(current_user)
    query = repo.query_listing()

    if effective == models.UserRole.teacher:
        active_period = get_active_exam_period(db)
        if active_period:
            owned_section_ids, _ = get_teacher_owned_section_ids(
                db,
                current_user.id,
                active_period.semester,
                active_period.academic_year,
            )
            if owned_section_ids is None:
                query = query.filter(models.Section.teacher_id == current_user.id)
            elif not owned_section_ids:
                return []
            else:
                query = query.filter(models.Section.id.in_(owned_section_ids))
        else:
            query = query.filter(models.Section.teacher_id == current_user.id)
    elif effective == models.UserRole.dept_supervisor:
        group_clause = build_course_group_clause(models.Course.course_id, dept_filter)
        if group_clause is None:
            return []
        query = query.join(models.Course, models.Section.course_id == models.Course.id).filter(group_clause)

    if status:
        query = query.filter(models.ExamSubmission.status == status)

    subs = query.order_by(models.ExamSubmission.updated_at.desc()).all()
    return [serialize_submission_summary(sub) for sub in subs]


def validate_message_text(message: str) -> str:
    cleaned_message = (message or "").strip()
    if not cleaned_message:
        raise EMSValidationError("เธเนเธญเธเธงเธฒเธกเนเธกเนเธเธงเธฃเธงเนเธฒเธ", field="message")
    if len(cleaned_message) > 2000:
        raise EMSValidationError("เธเนเธญเธเธงเธฒเธกเธขเธฒเธงเน€เธเธดเธ 2000 เธ•เธฑเธงเธญเธฑเธเธฉเธฃ", field="message")
    return cleaned_message


def assert_message_access(
    db: Session,
    repo: SubmissionRepository,
    submission_id: int,
    user: models.User,
) -> models.ExamSubmission:
    sub = repo.get_with_section(submission_id)
    if not sub:
        raise EMSNotFoundError("submission")

    effective = get_effective_role(user)
    if effective == models.UserRole.teacher:
        section = sub.section
        if not section or not can_teacher_access_section(db, user, section):
            raise EMSPermissionError("เนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเน€เธเนเธฒเธ–เธถเธ submission เธเธตเน")
    elif not can_access_submission_messages(user):
        raise EMSPermissionError("role เธเธตเนเนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเธ”เธน messages")
    return sub


def serialize_messages(messages: list[models.ExamMessage]) -> list[dict]:
    return [
        {
            "id": message.id,
            "sender": message.sender.full_name if message.sender else "โ€”",
            "sender_role": message.sender.role if message.sender else None,
            "message": message.message,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]


def validate_print_staple_choice(print_staple: str) -> str:
    valid_choices = valid_print_staple_choices()
    if print_staple not in valid_choices:
        raise EMSValidationError(f"print_staple เธ•เนเธญเธเน€เธเนเธ {set(valid_choices)}", field="print_staple")
    return print_staple


def assert_request_access_allowed(
    db: Session,
    repo: SubmissionRepository,
    submission_id: int,
    purpose: models.TokenPurpose,
    current_user: models.User,
) -> models.ExamSubmission:
    sub = repo.get_with_section(submission_id)
    if not sub:
        raise EMSNotFoundError("submission")

    effective = get_effective_role(current_user)
    if effective == models.UserRole.teacher and not can_teacher_access_section(db, current_user, sub.section):
        raise EMSPermissionError("เนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเน€เธเนเธฒเธ–เธถเธเนเธเธฅเนเธเธตเน")

    if purpose == models.TokenPurpose.download and not can_request_submission_download(current_user):
        raise EMSPermissionError("role เธเธตเนเนเธกเนเธชเธฒเธกเธฒเธฃเธ– download เนเธ”เน")

    if not is_submission_file_accessible(sub):
        raise EMSValidationError("เนเธเธฅเนเธขเธฑเธเนเธกเนเนเธ”เนเธฃเธฑเธเธเธฒเธฃเธญเธเธธเธกเธฑเธ•เธด")

    return sub


def build_submission_filename(submission: models.ExamSubmission) -> str:
    section = submission.section
    course = section.course if section else None
    course_code = (
        course.course_id if course and course.course_id else f"submission-{submission.id}"
    ).replace("/", "-")
    section_no = (section.section_no if section and section.section_no else "unknown").replace("/", "-")
    return f"{course_code}_section-{section_no}.pdf"


def build_access_watermark(
    current_user: models.User,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(timezone.utc)
    return (
        f"{current_user.full_name or current_user.username} | "
        f"{current_user.email} | "
        f"{issued_at.strftime('%Y-%m-%d %H:%M')}"
    )


def get_access_log_action(purpose: models.TokenPurpose) -> str:
    return {
        models.TokenPurpose.view: "viewed",
        models.TokenPurpose.download: "downloaded",
        models.TokenPurpose.print: "printed",
    }.get(purpose, "viewed")


def serialize_submission_versions(versions: list[models.ExamSubmissionVersion]) -> list[dict]:
    return [
        {
            "version": version.version,
            "snapshot": version.snapshot,
            "changed_by": version.changer.full_name if version.changer else None,
            "change_reason": version.change_reason,
            "created_at": version.created_at.isoformat(),
        }
        for version in versions
    ]


def apply_snapshot_to_submission(
    submission: models.ExamSubmission,
    snapshot: dict,
) -> models.ExamSubmission:
    submission.date_confirmed = snapshot.get("date_confirmed", False)
    submission.exam_type_choice = snapshot.get("exam_type_choice")
    submission.answer_formats = snapshot.get("answer_formats")
    submission.a4_pages_count = snapshot.get("a4_pages_count", 0)
    submission.no_cover_page_confirmed = snapshot.get("no_cover_page_confirmed", False)
    submission.is_shared_exam = snapshot.get("is_shared_exam", False)
    submission.status = models.SubmissionStatus.draft
    return submission
