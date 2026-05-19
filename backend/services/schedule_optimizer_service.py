"""
schedule_optimizer_service.py — optimizer orchestration boundary.

Thin layer that:
- Normalizes optimizer request inputs
- Loads prerequisite data (sections, rooms, teachers, unavailability)
- Sets up trace context
- Delegates to legacy solver adapters in schedule.py

Solver bodies (_greedy_optimizer, _cpsat_optimizer) remain in router.
"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
import models
from schemas import OptimizerRequest, OptimizerResult
from repositories.schedule_repository import load_unavailability_maps as _load_unavailability_maps_repo


class ScheduleOptimizerService:
    """Orchestration boundary for schedule optimization."""

    @staticmethod
    def prepare_optimization_inputs(db: Session, data: OptimizerRequest):
        """Normalize request and load prerequisite data."""
        from time_ranges import normalize_time_range

        sections = db.query(models.Section).filter(
            models.Section.semester == data.semester,
            models.Section.academic_year == data.academic_year,
        ).options(
            joinedload(models.Section.course),
            joinedload(models.Section.teacher),
        ).all()

        rooms = db.query(models.Room).filter(models.Room.is_active == True).all()

        teachers = db.query(models.User).filter(
            models.User.role == models.UserRole.teacher,
            models.User.is_active == True
        ).all()

        unavail_map, room_unavail_map = _load_unavailability_maps_repo(db, data)

        if not sections:
            raise ValueError("ไม่พบ sections ในเทอมที่ระบุ")
        if not rooms:
            raise ValueError("ไม่พบห้องสอบ")

        return sections, rooms, teachers, unavail_map, room_unavail_map

    @staticmethod
    def get_default_time_slots() -> list:
        """Return static time slots for optimization."""
        return [
            ("2569-03-19", "15.30-18.30"),
            ("2569-03-20", "15.30-18.30"),
            ("2569-03-23", "09.00-12.00"),
            ("2569-03-23", "12.00-15.00"),
            ("2569-03-23", "15.30-18.30"),
            ("2569-03-24", "08.00-11.00"),
            ("2569-03-24", "12.00-15.00"),
            ("2569-03-24", "15.30-18.30"),
            ("2569-03-25", "09.00-12.00"),
            ("2569-03-25", "12.00-15.00"),
            ("2569-03-26", "09.00-12.00"),
            ("2569-03-26", "12.00-15.00"),
            ("2569-03-26", "15.30-18.30"),
            ("2569-03-27", "09.00-12.00"),
            ("2569-03-27", "12.00-15.00"),
            ("2569-03-27", "15.30-18.30"),
            ("2569-03-28", "09.00-12.00"),
            ("2569-03-28", "12.00-15.00"),
            ("2569-03-28", "15.30-18.30"),
        ]

    @staticmethod
    def check_ortools_available() -> bool:
        """Check if OR-Tools is installed."""
        try:
            from ortools.sat.python import cp_model
            return True
        except ImportError:
            return False

    @staticmethod
    def build_optimizer_result(
        success: bool,
        sections_assigned: int,
        sections_total: int,
        fairness_score: float,
        violations: list,
        details: list,
        paper_distribution_assigned: int,
        paper_distribution_slots: int,
        paper_distribution_unfilled: int,
        paper_distribution_warnings: list,
        esq_staff_excluded: list,
        esq_in_stat: list,
        room_keepers_assigned: list,
        reminder: Optional[str],
        native_trace_summary: dict,
        native_trace_events: list,
        traceability_completeness_score: float,
        trace_source_breakdown: dict,
    ) -> OptimizerResult:
        """Build OptimizerResult with consistent schema."""
        return OptimizerResult(
            success=success,
            sections_assigned=sections_assigned,
            sections_total=sections_total,
            fairness_score=fairness_score,
            violations=violations,
            details=details,
            paper_distribution_assigned=paper_distribution_assigned,
            paper_distribution_slots=paper_distribution_slots,
            paper_distribution_unfilled=paper_distribution_unfilled,
            paper_distribution_warnings=paper_distribution_warnings,
            esq_staff_excluded=esq_staff_excluded,
            esq_in_stat=esq_in_stat,
            room_keepers_assigned=room_keepers_assigned,
            reminder=reminder,
            native_trace_summary=native_trace_summary,
            native_trace_events=native_trace_events,
            traceability_completeness_score=traceability_completeness_score,
            trace_source_breakdown=trace_source_breakdown,
        )