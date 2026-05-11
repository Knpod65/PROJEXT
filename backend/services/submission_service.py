"""
services/submission_service.py — Exam Submission domain logic
=============================================================
Pure service functions: no FastAPI imports, no Depends(), no HTTPException.
Callers (routers) translate EMSDomainError → HTTP responses.
All DB writes use db.flush(); commit belongs in the router.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

import models
from config.settings import settings
from services.exceptions import EMSNotFoundError, EMSPermissionError


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
