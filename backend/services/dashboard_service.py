"""
dashboard_service.py — orchestration for dashboard operations.

Owns:
- dashboard summary shaping
- operational KPI shaping
- role/faculty visibility filtering
- aggregate-safe response shaping
"""
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import models


class DashboardService:
    """Orchestration for dashboard operations."""

    @staticmethod
    def get_dashboard_stats(
        db: Session,
        semester: str,
        academic_year: str,
        current_user: models.User,
    ) -> dict[str, Any]:
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
            models.User.is_active == True,
        ).count()

        rooms_in_use = db.query(
            func.count(func.distinct(models.ExamSchedule.room_id))
        ).scalar() or 0

        recent_logs = []
        from auth_utils import get_effective_role
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

        return {
            "total_sections": len(sections),
            "total_students": total_students,
            "total_sheets": total_sheets,
            "total_teachers": teachers_count,
            "scheduled_sections": scheduled_count,
            "unscheduled_sections": len(sections) - scheduled_count,
            "rooms_in_use": rooms_in_use,
            "copy_cost": total_sheets * 0.50,
            "recent_logs": recent_logs,
        }

    @staticmethod
    def get_analytics(
        db: Session,
        semester: str,
        academic_year: str,
    ) -> dict[str, Any]:
        sub_rows = db.query(
            models.ExamSubmission.status,
            func.count(models.ExamSubmission.id).label("cnt"),
        ).group_by(models.ExamSubmission.status).all()
        submission_status = {r.status: r.cnt for r in sub_rows}

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

        sup_total = db.query(models.Supervision).count()
        sup_confirmed = db.query(models.Supervision).filter(
            models.Supervision.confirmed == True
        ).count()
        supervision_stats = {
            "confirmed": sup_confirmed,
            "pending": sup_total - sup_confirmed,
        }

        swap_rows = db.query(
            models.SwapRequest.status,
            func.count(models.SwapRequest.id).label("cnt"),
        ).group_by(models.SwapRequest.status).all()
        swap_status = {r.status: r.cnt for r in swap_rows}

        room_rows = db.query(
            models.Room.room_name,
            func.sum(models.ExamSchedule.total_sheets).label("sheets"),
        ).join(models.ExamSchedule, models.ExamSchedule.room_id == models.Room.id)\
         .group_by(models.Room.id)\
         .order_by(func.sum(models.ExamSchedule.total_sheets).desc())\
         .limit(10).all()
        copy_per_room = [
            {"room": r.room_name, "sheets": int(r.sheets or 0), "cost": int(r.sheets or 0) * 0.50}
            for r in room_rows
        ]

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
