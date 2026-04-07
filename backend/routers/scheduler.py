"""
scheduler.py - cron-style background jobs
"""
from datetime import date, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from auth_utils import require_admin
from database import SessionLocal, get_db
import models

router = APIRouter()
CRON_SECRET = __import__("os").getenv("CRON_SECRET", "")


def _check_cron(secret: str = ""):
    # SECURITY: require a non-empty CRON_SECRET to be set; reject empty/missing tokens.
    # Old code: `if CRON_SECRET and secret != CRON_SECRET` silently bypassed the check
    # when CRON_SECRET was empty (falsy short-circuit).
    if not CRON_SECRET:
        raise HTTPException(503, "CRON_SECRET not configured — scheduler endpoints disabled")
    if secret != CRON_SECRET:
        raise HTTPException(403, "Invalid cron secret")


def _queue_db_job(background_tasks: BackgroundTasks, job):
    def _runner():
        db = SessionLocal()
        try:
            job(db)
        finally:
            db.close()

    background_tasks.add_task(_runner)


@router.post("/daily-digest")
async def run_daily_digest(
    background_tasks: BackgroundTasks,
    secret: str = "",
):
    _check_cron(secret)

    def _job(db: Session):
        from email_notifications import send_daily_digest
        count = send_daily_digest(db)
        import logging
        logging.getLogger("ems").info(f"Daily digest: {count} emails sent")

    _queue_db_job(background_tasks, _job)
    return {"status": "queued", "job": "daily_digest"}


@router.post("/exam-reminder")
async def run_exam_reminder(
    background_tasks: BackgroundTasks,
    target_date: str | None = None,
    secret: str = "",
):
    _check_cron(secret)
    parsed_date = None
    if target_date:
        try:
            parsed_date = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(400, "target_date must be YYYY-MM-DD")

    def _job(db: Session):
        from email_notifications import send_exam_reminders
        run_date = parsed_date or (date.today() + timedelta(days=1))
        count = send_exam_reminders(db, run_date)
        import logging
        logging.getLogger("ems").info(f"Exam reminders: {count} emails for {run_date}")

    _queue_db_job(background_tasks, _job)
    return {
        "status": "queued",
        "job": "exam_reminder",
        "target_date": str(parsed_date or "tomorrow"),
    }


@router.post("/run-all")
async def run_all_jobs(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(require_admin),
):
    def _job(db: Session):
        from email_notifications import send_daily_digest, send_exam_reminders
        digest_count = send_daily_digest(db)
        reminder_count = send_exam_reminders(db, date.today() + timedelta(days=1))
        import logging
        logging.getLogger("ems").info(
            f"run-all: digest={digest_count}, reminders={reminder_count}"
        )

    _queue_db_job(background_tasks, _job)
    return {"status": "queued", "jobs": ["daily_digest", "exam_reminder"]}


@router.get("/status")
def scheduler_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    tomorrow = date.today() + timedelta(days=1)

    teachers_with_pending = db.query(models.User).join(
        models.Section, models.Section.teacher_id == models.User.id
    ).join(
        models.ExamSubmission, models.ExamSubmission.section_id == models.Section.id
    ).filter(
        models.User.role == models.UserRole.teacher,
        models.User.email.isnot(None),
        models.ExamSubmission.status.in_(["draft", "rejected"]),
    ).distinct().count()

    staff_with_swap = db.query(models.User).join(
        models.SwapRequest, models.SwapRequest.target_id == models.User.id
    ).filter(
        models.User.role == models.UserRole.staff,
        models.User.email.isnot(None),
        models.SwapRequest.status == "pending",
    ).distinct().count()

    tomorrow_count = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.exam_date == tomorrow
    ).count()

    return {
        "today": str(date.today()),
        "tomorrow": str(tomorrow),
        "email_enabled": bool(__import__("os").getenv("SMTP_HOST")),
        "digest_recipients": {
            "teachers_with_pending": teachers_with_pending,
            "staff_with_pending_swap": staff_with_swap,
        },
        "reminder_tomorrow_exams": tomorrow_count,
    }
