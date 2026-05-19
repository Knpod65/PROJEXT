"""
export_service.py — orchestration for export operations.

Owns:
- schedule export orchestration
- workload export orchestration
- paper distribution export orchestration
- filename generation
- delegates to repositories for data access
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
import models
from repositories.export_repository import ExportRepository
from config.periods import resolve_export_period
import io


class ExportService:
    """Orchestration for export operations."""

    @staticmethod
    def get_schedule_export_data(
        db: Session,
        semester: str,
        academic_year: str,
        exam_type: str,
    ) -> list:
        """Get schedule data for export."""
        return ExportRepository.get_schedule_data(db, semester, academic_year, exam_type)

    @staticmethod
    def get_workload_export_data(
        db: Session,
        period,
    ) -> dict:
        """Get workload data for export."""
        return ExportRepository.get_workload_data(db, period)

    @staticmethod
    def get_paper_distribution_export_data(
        db: Session,
        period,
    ) -> Tuple[list, list]:
        """Get paper distribution data for export."""
        assignments = ExportRepository.get_paper_distribution_assignments(db, period)
        schedules = ExportRepository.get_schedules_for_context(db, period)
        return assignments, schedules

    @staticmethod
    def generate_schedule_filename(semester: str, academic_year: str, exam_type: str) -> str:
        """Generate stable filename for schedule export."""
        return f"exam_schedule_{semester}_{academic_year}_{exam_type}.pdf"

    @staticmethod
    def generate_workload_filename(semester: str, academic_year: str, exam_type: str) -> str:
        """Generate stable filename for workload export."""
        return f"EMS_workload_summary_{semester}_{academic_year}_{exam_type}.pdf"

    @staticmethod
    def generate_paper_distribution_filename(semester: str, academic_year: str, exam_type: str) -> str:
        """Generate stable filename for paper distribution export."""
        return f"EMS_paper_distribution_{semester}_{academic_year}_{exam_type}.pdf"

    @staticmethod
    def get_compensation_data(db: Session, semester: str, academic_year: str, exam_type: str) -> dict:
        """Get compensation data for export."""
        return ExportRepository.get_compensation_data(db, semester, academic_year, exam_type)

    @staticmethod
    def get_submissions_data(db: Session, semester: str, academic_year: str) -> list:
        """Get submissions data for export."""
        return ExportRepository.get_submissions_data(db, semester, academic_year)

    @staticmethod
    def get_period_workload_snapshot(db: Session, period) -> dict:
        """Get workload snapshot for period."""
        from staff_workloads import get_period_workload_snapshot
        return get_period_workload_snapshot(db, period)

    @staticmethod
    def get_paper_distribution_data(db: Session, period) -> Tuple[list, list]:
        """Get paper distribution data for export."""
        return ExportRepository.get_paper_distribution_data(db, period)

    @staticmethod
    def get_audit_logs(db: Session, filters: dict) -> dict:
        """Get paginated audit logs."""
        return ExportRepository.get_audit_logs(db, filters)