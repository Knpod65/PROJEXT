from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models, schemas
from auth_utils import get_current_user

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

    # Recent audit logs
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
