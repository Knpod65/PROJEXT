from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from database import get_db
import models, schemas
from auth_utils import get_current_user, get_effective_role, require_admin

router = APIRouter()

@router.get("/", response_model=schemas.DashboardStats)
def get_dashboard(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sections = db.query(models.Section).filter(
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).all()

    scheduled_ids = db.query(models.ExamSchedule.section_id).subquery()
    scheduled_count = db.query(models.Section).filter(
        models.Section.id.in_(scheduled_ids),
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).count()

    total_students = sum(s.num_students for s in sections)
    total_sheets = db.query(func.sum(models.ExamSchedule.total_sheets)).scalar() or 0
    total_sheets += 150  # แบบฟอร์มทุจริต

    teachers_count = db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True
    ).count()

    rooms_in_use = db.query(
        func.count(func.distinct(models.ExamSchedule.room_id))
    ).scalar() or 0

    # Recent audit logs — only expose to admins
    recent_logs = []
    if get_effective_role(current_user) == models.UserRole.admin:
        logs = db.query(models.AuditLog).order_by(
            models.AuditLog.timestamp.desc()
        ).limit(20).all()
        recent_logs = [
            {
                "id": log.id,
                "action": log.action,
                "actor": log.actor.full_name if log.actor else "system",
                "table_name": log.table_name,
                "record_id": log.record_id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ]

    return schemas.DashboardStats(
        total_sections=len(sections),
        total_students=total_students,
        total_sheets=total_sheets,
        total_teachers=teachers_count,
        scheduled_sections=scheduled_count,
        unscheduled_sections=len(sections) - scheduled_count,
        rooms_in_use=rooms_in_use,
        copy_cost=total_sheets * 0.50,
        recent_logs=recent_logs,
    )


@router.get("/analytics")
def get_analytics(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Chart data for admin dashboard."""

    # ── 1. Submission status breakdown ───────────────────────
    sub_rows = db.query(
        models.ExamSubmission.status,
        func.count(models.ExamSubmission.id).label("cnt"),
    ).group_by(models.ExamSubmission.status).all()
    submission_status = {r.status: r.cnt for r in sub_rows}

    # ── 2. Teacher submission rate (per section) ──────────────
    sections = db.query(models.Section).filter(
        models.Section.semester == semester,
        models.Section.academic_year == academic_year,
    ).all()
    section_ids = [s.id for s in sections]
    submitted_section_ids = set(
        r[0] for r in db.query(models.ExamSubmission.section_id)
        .filter(models.ExamSubmission.section_id.in_(section_ids))
        .distinct().all()
    )
    teacher_stats = {
        "submitted": len(submitted_section_ids),
        "not_submitted": len(section_ids) - len(submitted_section_ids),
    }

    # ── 3. Supervision confirmation rate ──────────────────────
    sup_total = db.query(models.Supervision).count()
    sup_confirmed = db.query(models.Supervision).filter(
        models.Supervision.confirmed == True
    ).count()
    supervision_stats = {
        "confirmed": sup_confirmed,
        "pending": sup_total - sup_confirmed,
    }

    # ── 4. Swap request status ────────────────────────────────
    swap_rows = db.query(
        models.SwapRequest.status,
        func.count(models.SwapRequest.id).label("cnt"),
    ).group_by(models.SwapRequest.status).all()
    swap_status = {r.status: r.cnt for r in swap_rows}

    # ── 5. Copy cost per room (top 10) ────────────────────────
    room_rows = db.query(
        models.Room.name,
        func.sum(models.ExamSchedule.total_sheets).label("sheets"),
    ).join(models.ExamSchedule, models.ExamSchedule.room_id == models.Room.id)\
     .group_by(models.Room.id)\
     .order_by(func.sum(models.ExamSchedule.total_sheets).desc())\
     .limit(10).all()
    copy_per_room = [
        {"room": r.name, "sheets": int(r.sheets or 0), "cost": int(r.sheets or 0) * 0.50}
        for r in room_rows
    ]

    # ── 6. Check-in activity per exam date ────────────────────
    checkin_rows = db.query(
        models.ExamSchedule.exam_date,
        func.count(models.CheckinEvent.id).label("cnt"),
    ).join(models.CheckinEvent, models.CheckinEvent.schedule_id == models.ExamSchedule.id)\
     .group_by(models.ExamSchedule.exam_date)\
     .order_by(models.ExamSchedule.exam_date).all()
    checkin_by_date = [
        {"date": str(r.exam_date), "count": r.cnt}
        for r in checkin_rows
    ]

    return {
        "submission_status": submission_status,
        "teacher_stats": teacher_stats,
        "supervision_stats": supervision_stats,
        "swap_status": swap_status,
        "copy_per_room": copy_per_room,
        "checkin_by_date": checkin_by_date,
    }
