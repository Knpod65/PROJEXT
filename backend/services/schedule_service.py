"""
schedule_service.py — service layer for schedule business logic.

Thin wrapper around existing schedule_query_service and schedule_repository.
All methods are pure or delegate to side-effect-free helpers.
Zero ORM, zero DB session creation, zero auth — receives db + current_user from router.
"""


class ScheduleService:
    """Stateless service for schedule-related operations."""

    @staticmethod
    def list_schedules(
        db,
        current_user,
        exam_date: str | None = None,
        room_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 200,
    ) -> list:
        """Delegate to schedule_query_service with validated params."""
        # Delegate validation to validator layer
        from validators.schedule_validator import (
            normalize_date_params,
            validate_pagination_clamp,
            validate_status,
        )

        normalized_date = normalize_date_params(None, exam_date)  # date param not used in list_schedules? keep as-is
        page, limit = validate_pagination_clamp(page, limit)
        normalized_status = validate_status(status)

        from services.schedule_query_service import build_schedule_query, serialize_schedule

        # Build base query with policy scoping
        query = build_schedule_query(
            db=db,
            current_user=current_user,
            exam_date=normalized_date,
            room_id=room_id,
            status=normalized_status,
        )

        # Execute with pagination
        offset = (page - 1) * limit
        rows = query.order_by(
            models.ExamSchedule.exam_date,
            models.ExamSchedule.exam_time
        ).offset(offset).limit(limit).all()

        # Serialize
        return [serialize_schedule(row) for row in rows]

    @staticmethod
    def get_schedule_grouped(
        db,
        current_user,
    ) -> list[dict]:
        """Delegate grouped schedule fetch."""
        from services.schedule_query_service import build_schedule_query, group_schedules_by_date

        query = build_schedule_query(
            db=db,
            current_user=current_user,
            exam_date=None,
            room_id=None,
            status=None,
        )

        schedules = query.order_by(
            models.ExamSchedule.exam_date,
            models.ExamSchedule.exam_time
        ).all()

        return group_schedules_by_date(schedules)