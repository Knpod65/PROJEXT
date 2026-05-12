from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from auth_utils import require_print_shop
from database import get_db
import models
from services.audit_service import audit_mutation

router = APIRouter()


class PrintJobNotesUpdate(BaseModel):
    notes: str | None = None
    delivery_note: str | None = None


def _serialize_job(job: models.PrintQueueJob) -> dict:
    submission = job.submission
    section = submission.section if submission else None
    course = section.course if section and section.course else None
    schedule = section.schedules[0] if section and section.schedules else None
    room = schedule.room if schedule and schedule.room else None

    specs: list[str] = []
    if submission:
        specs.append("Double-sided" if submission.print_duplex else "Single-sided")
        if submission.print_staple and submission.print_staple != "none":
            specs.append(f"Staple: {submission.print_staple}")
        if submission.answer_formats:
            specs.extend([str(item).replace("_", " ") for item in submission.answer_formats])

    students = section.num_students if section else 0
    pages = 0
    if submission and submission.a4_pages_count:
        pages = submission.a4_pages_count
    elif schedule and schedule.num_pages:
        pages = schedule.num_pages

    total_sheets = schedule.total_sheets if schedule and schedule.total_sheets else students * max(pages, 1)

    return {
        "id": job.id,
        "submission_id": submission.id if submission else None,
        "course_code": course.course_id if course else "",
        "subject_name": course.course_name_th if course else "",
        "section": section.section_no if section else "",
        "room": room.room_name if room else "",
        "exam_date": schedule.exam_date.isoformat() if schedule and schedule.exam_date else None,
        "exam_time": schedule.exam_time if schedule else None,
        "students": students,
        "pages": pages,
        "total_sheets": total_sheets,
        "priority": job.priority,
        "status": job.status.value if isinstance(job.status, models.PrintJobStatus) else str(job.status),
        "specs": specs,
        "notes": job.notes,
        "delivery_note": job.delivery_note,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "dispatched_at": job.dispatched_at.isoformat() if job.dispatched_at else None,
        "delivered_at": job.delivered_at.isoformat() if job.delivered_at else None,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "assigned_to": job.assignee.full_name if job.assignee else None,
    }


def _get_job(db: Session, job_id: int) -> models.PrintQueueJob:
    job = db.query(models.PrintQueueJob).options(
        joinedload(models.PrintQueueJob.assignee),
        joinedload(models.PrintQueueJob.submission)
        .joinedload(models.ExamSubmission.section)
        .joinedload(models.Section.course),
        joinedload(models.PrintQueueJob.submission)
        .joinedload(models.ExamSubmission.section)
        .joinedload(models.Section.schedules)
        .joinedload(models.ExamSchedule.room),
    ).filter(models.PrintQueueJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")
    return job


def _transition_job(
    db: Session,
    job: models.PrintQueueJob,
    current_user: models.User,
    request: Request,
    *,
    expected_status: models.PrintJobStatus,
    next_status: models.PrintJobStatus,
    action: str,
    timestamp_field: str,
):
    if job.status != expected_status:
        raise HTTPException(status_code=400, detail=f"Job must be {expected_status.value} before {action.lower()}.")

    previous_status = job.status.value if isinstance(job.status, models.PrintJobStatus) else str(job.status)
    job.status = next_status
    setattr(job, timestamp_field, datetime.now(timezone.utc))
    if next_status == models.PrintJobStatus.processing:
        job.assigned_to = current_user.id

    db.commit()
    db.refresh(job)
    audit_mutation(
        db,
        current_user,
        action,
        "print_queue_jobs",
        record_id=job.id,
        old_values={"status": previous_status},
        new_values={"status": next_status.value},
        request=request,
    )
    return _serialize_job(job)


@router.get("/queue")
def list_print_queue(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    jobs = db.query(models.PrintQueueJob).options(
        joinedload(models.PrintQueueJob.assignee),
        joinedload(models.PrintQueueJob.submission)
        .joinedload(models.ExamSubmission.section)
        .joinedload(models.Section.course),
        joinedload(models.PrintQueueJob.submission)
        .joinedload(models.ExamSubmission.section)
        .joinedload(models.Section.schedules)
        .joinedload(models.ExamSchedule.room),
    ).order_by(
        models.PrintQueueJob.created_at.asc(),
        models.PrintQueueJob.id.asc(),
    ).all()

    return [_serialize_job(job) for job in jobs]


@router.get("/queue/{job_id}")
def get_print_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    return _serialize_job(_get_job(db, job_id))


@router.post("/queue/{job_id}/start")
def start_print_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    job = _get_job(db, job_id)
    return _transition_job(
        db,
        job,
        current_user,
        request,
        expected_status=models.PrintJobStatus.queued,
        next_status=models.PrintJobStatus.processing,
        action="PRINT_JOB_START",
        timestamp_field="started_at",
    )


@router.post("/queue/{job_id}/complete")
def complete_print_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    job = _get_job(db, job_id)
    return _transition_job(
        db,
        job,
        current_user,
        request,
        expected_status=models.PrintJobStatus.processing,
        next_status=models.PrintJobStatus.completed,
        action="PRINT_JOB_COMPLETE",
        timestamp_field="completed_at",
    )


@router.post("/queue/{job_id}/dispatch")
def dispatch_print_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    job = _get_job(db, job_id)
    return _transition_job(
        db,
        job,
        current_user,
        request,
        expected_status=models.PrintJobStatus.completed,
        next_status=models.PrintJobStatus.dispatched,
        action="PRINT_JOB_DISPATCH",
        timestamp_field="dispatched_at",
    )


@router.post("/queue/{job_id}/deliver")
def deliver_print_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    job = _get_job(db, job_id)
    return _transition_job(
        db,
        job,
        current_user,
        request,
        expected_status=models.PrintJobStatus.dispatched,
        next_status=models.PrintJobStatus.delivered,
        action="PRINT_JOB_DELIVER",
        timestamp_field="delivered_at",
    )


@router.put("/queue/{job_id}/notes")
def update_print_job_notes(
    job_id: int,
    data: PrintJobNotesUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_print_shop),
):
    job = _get_job(db, job_id)
    old_values = {
        "notes_present": bool((job.notes or "").strip()),
        "delivery_note_present": bool((job.delivery_note or "").strip()),
    }
    job.notes = data.notes
    job.delivery_note = data.delivery_note
    db.commit()
    db.refresh(job)
    audit_mutation(
        db,
        current_user,
        "PRINT_JOB_NOTES_UPDATE",
        "print_queue_jobs",
        record_id=job.id,
        old_values=old_values,
        new_values={
            "notes_present": bool((data.notes or "").strip()),
            "notes_length": len((data.notes or "").strip()),
            "delivery_note_present": bool((data.delivery_note or "").strip()),
            "delivery_note_length": len((data.delivery_note or "").strip()),
        },
        request=request,
    )
    return _serialize_job(job)
