"""
export_repository.py — repository for export data operations.

Owns:
- schedule data queries
- workload data queries
- paper distribution data queries
- export context building
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from typing import Optional
import models


class ExportRepository:
    """Repository for export data operations."""

    @staticmethod
    def get_schedule_data(db: Session, semester: str, academic_year: str, exam_type: str) -> list:
        """Get schedule data with all relationships."""
        return db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.section)
                .joinedload(models.Section.course),
            joinedload(models.ExamSchedule.section)
                .joinedload(models.Section.teacher),
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions)
                .joinedload(models.Supervision.user),
        ).join(models.Section).filter(
            models.Section.semester == semester,
            models.Section.academic_year == academic_year,
        ).order_by(
            models.ExamSchedule.exam_date,
            models.ExamSchedule.exam_time,
        ).all()

    @staticmethod
    def get_workload_data(db: Session, period) -> dict:
        """Get workload snapshot for period."""
        from staff_workloads import get_period_workload_snapshot
        return get_period_workload_snapshot(db, period)

    @staticmethod
    def get_paper_distribution_assignments(db: Session, period) -> list:
        """Get paper distribution assignments for period."""
        return db.query(models.PaperDistributionAssignment).options(
            joinedload(models.PaperDistributionAssignment.user)
        ).filter(
            models.PaperDistributionAssignment.exam_period_id == period.id
        ).order_by(
            models.PaperDistributionAssignment.exam_date,
            models.PaperDistributionAssignment.exam_time,
            models.PaperDistributionAssignment.slot_order,
        ).all()

    @staticmethod
    def get_schedules_for_context(db: Session, period) -> list:
        """Get schedules for context mapping."""
        return db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.room),
        ).join(models.Section).filter(
            models.Section.academic_year == period.academic_year,
            models.Section.semester == period.semester,
            models.ExamSchedule.exam_type == period.exam_type,
        ).all()

    @staticmethod
    def get_compensation_data(db: Session, semester: str, academic_year: str, exam_type: str) -> dict:
        """Get compensation data for export."""
        sups = db.query(models.Supervision).options(
            joinedload(models.Supervision.user),
            joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.section)
                .joinedload(models.Section.course),
            joinedload(models.Supervision.schedule).joinedload(models.ExamSchedule.room),
        ).join(models.ExamSchedule).join(models.Section).filter(
            models.Section.semester == semester,
            models.Section.academic_year == academic_year,
            models.ExamSchedule.exam_type == exam_type,
        ).all()

        settings = {s.key: s.value for s in db.query(models.SystemSetting).all()}
        rate_internal = float(settings.get("compensation_rate_internal", "200"))
        rate_external = float(settings.get("compensation_rate_external", "300"))

        return {
            "supervisions": sups,
            "rate_internal": rate_internal,
            "rate_external": rate_external,
        }

    @staticmethod
    def get_submissions_data(db: Session, semester: str, academic_year: str) -> list:
        """Get submissions data for export."""
        return db.query(models.ExamSubmission).options(
            joinedload(models.ExamSubmission.section).joinedload(models.Section.course),
            joinedload(models.ExamSubmission.section).joinedload(models.Section.teacher),
            joinedload(models.ExamSubmission.submitter),
            joinedload(models.ExamSubmission.material_request),
        ).join(models.Section).filter(
            models.Section.semester == semester,
            models.Section.academic_year == academic_year,
        ).all()

    @staticmethod
    def get_audit_logs(db: Session, filters: dict) -> dict:
        """Get paginated audit logs."""
        q = db.query(models.AuditLog)
        if filters.get("table_name"):
            q = q.filter(models.AuditLog.table_name == filters["table_name"])
        if filters.get("record_id"):
            q = q.filter(models.AuditLog.record_id == filters["record_id"])
        if filters.get("actor_id"):
            q = q.filter(models.AuditLog.actor_id == filters["actor_id"])
        if filters.get("action"):
            q = q.filter(models.AuditLog.action.ilike(f"%{filters['action']}%"))
        if filters.get("request_id"):
            q = q.filter(models.AuditLog.request_id == filters["request_id"])

        page = filters.get("page", 1)
        limit = min(filters.get("limit", 50), 200)

        total = q.count()
        logs = q.order_by(models.AuditLog.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()

        return {"total": total, "page": page, "limit": limit, "logs": logs}