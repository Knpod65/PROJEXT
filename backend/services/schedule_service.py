"""
schedule_service.py — service layer for schedule business logic.

Thin wrapper around existing schedule_query_service and schedule_repository.
All methods are pure or delegate to side-effect-free helpers.
Zero ORM, zero DB session creation, zero auth — receives db + current_user from router.
"""
import models
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from typing import Optional


def _get_schedule(section, exam_type=None):
    """Helper: ดึง ExamSchedule จาก section.schedules (list)"""
    if not section.schedules:
        return None
    if exam_type is None:
        return section.schedules[0] if section.schedules else None
    for s in section.schedules:
        if s.exam_type == exam_type or s.exam_type.value == exam_type:
            return s
    return None


def _normalize_schedule_time_fields(exam_time: Optional[str]) -> dict:
    from time_ranges import parse_time_range
    start, end = parse_time_range(exam_time)
    return {"exam_time_start": start, "exam_time_end": end}


def _exam_type_value(data) -> str:
    return data.exam_type.value if hasattr(data.exam_type, "value") else str(data.exam_type)


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
        from validators.schedule_validator import (
            normalize_date_params,
            validate_pagination_clamp,
            validate_status,
        )

        normalized_date = normalize_date_params(None, exam_date)
        page, limit = validate_pagination_clamp(page, limit)
        normalized_status = validate_status(status)

        from services.schedule_query_service import build_schedule_query, serialize_schedule

        query = build_schedule_query(
            db=db,
            current_user=current_user,
            exam_date=normalized_date,
            room_id=room_id,
            status=normalized_status,
        )

        offset = (page - 1) * limit
        rows = query.order_by(
            models.ExamSchedule.exam_date,
            models.ExamSchedule.exam_time
        ).offset(offset).limit(limit).all()

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

    @staticmethod
    def create_schedule(
        db,
        current_user,
        data,
        request,
    ):
        """Create a new exam schedule."""
        from term_lifecycle import require_period_editable_for_values

        exists = db.query(models.ExamSchedule).filter(
            models.ExamSchedule.section_id == data.section_id
        ).first()
        if exists:
            raise HTTPException(400, "Section นี้มีตารางสอบแล้ว")

        section = db.query(models.Section).filter(
            models.Section.id == data.section_id
        ).first()
        if not section:
            raise HTTPException(404, "ไม่พบ section")

        require_period_editable_for_values(
            db,
            section.academic_year,
            section.semester,
            _exam_type_value(data),
        )

        total_sheets = section.num_students * data.num_pages
        sch = models.ExamSchedule(
            **data.model_dump(),
            **_normalize_schedule_time_fields(data.exam_time),
            total_sheets=total_sheets,
        )
        db.add(sch)
        db.commit()
        db.refresh(sch)

        from auth_utils import log_action
        log_action(db, current_user, "CREATE_SCHEDULE", "exam_schedules", sch.id,
                   new_values=data.model_dump(), request=request)

        return db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions),
        ).filter(models.ExamSchedule.id == sch.id).first()

    @staticmethod
    def update_schedule(
        db,
        current_user,
        sid: int,
        data,
        request,
    ):
        """Update an existing exam schedule."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import is_view_all_role, log_action

        if is_view_all_role(current_user):
            raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")

        sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
        if not sch:
            raise HTTPException(404, "ไม่พบตารางสอบ")

        section = sch.section or db.query(models.Section).filter(
            models.Section.id == sch.section_id
        ).first()
        if section:
            require_period_editable_for_values(
                db,
                section.academic_year,
                section.semester,
                _exam_type_value(sch),
            )

        for k, v in data.model_dump(exclude_none=True).items():
            setattr(sch, k, v)
        if data.exam_time is not None:
            time_fields = _normalize_schedule_time_fields(data.exam_time)
            sch.exam_time_start = time_fields["exam_time_start"]
            sch.exam_time_end = time_fields["exam_time_end"]

        if data.num_pages is not None:
            section = db.query(models.Section).filter(
                models.Section.id == sch.section_id
            ).first()
            if section:
                sch.total_sheets = section.num_students * sch.num_pages

        db.commit()
        db.refresh(sch)
        log_action(db, current_user, "UPDATE_SCHEDULE", "exam_schedules", sid, request=request)

        return db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.room),
            joinedload(models.ExamSchedule.supervisions),
        ).filter(models.ExamSchedule.id == sid).first()

    @staticmethod
    def delete_schedule(
        db,
        current_user,
        sid: int,
        request,
    ):
        """Delete an exam schedule."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import log_action, require_admin

        sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
        if not sch:
            raise HTTPException(404, "ไม่พบตารางสอบ")

        section = sch.section or db.query(models.Section).filter(
            models.Section.id == sch.section_id
        ).first()
        if section:
            require_period_editable_for_values(
                db,
                section.academic_year,
                section.semester,
                _exam_type_value(sch),
            )

        db.delete(sch)
        db.commit()
        log_action(db, current_user, "DELETE_SCHEDULE", "exam_schedules", sid, request=request)
        return {"success": True}

    @staticmethod
    def assign_supervision(
        db,
        current_user,
        sid: int,
        user_id: int,
        slot_order: int,
        request,
    ):
        """Assign a supervisor to a schedule."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import log_action

        sch = db.query(models.ExamSchedule).filter(models.ExamSchedule.id == sid).first()
        if not sch:
            raise HTTPException(404, "ไม่พบตารางสอบ")

        section = sch.section or db.query(models.Section).filter(
            models.Section.id == sch.section_id
        ).first()
        if section:
            require_period_editable_for_values(
                db,
                section.academic_year,
                section.semester,
                _exam_type_value(sch),
            )

        existing = db.query(models.Supervision).filter(
            models.Supervision.schedule_id == sid,
            models.Supervision.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(400, "อาจารย์ท่านนี้อยู่ในตารางนี้แล้ว")

        sup = models.Supervision(
            schedule_id=sid,
            user_id=user_id,
            slot_order=slot_order,
            compensation=300.0 if slot_order == 1 else 200.0,
        )
        db.add(sup)
        db.commit()
        log_action(db, current_user, "ASSIGN_SUPERVISION", "supervisions", sup.id, request=request)
        return {"success": True, "supervision_id": sup.id}

    @staticmethod
    def remove_supervision(
        db,
        current_user,
        sid: int,
        sup_id: int,
        request,
    ):
        """Remove a supervisor from a schedule."""
        from term_lifecycle import require_period_editable_for_values
        from auth_utils import log_action

        sup = db.query(models.Supervision).filter(
            models.Supervision.id == sup_id,
            models.Supervision.schedule_id == sid
        ).first()
        if not sup:
            raise HTTPException(404, "ไม่พบข้อมูลกรรมการ")

        schedule = sup.schedule or db.query(models.ExamSchedule).filter(
            models.ExamSchedule.id == sid
        ).first()
        section = schedule.section if schedule else None
        if section:
            require_period_editable_for_values(
                db,
                section.academic_year,
                section.semester,
                _exam_type_value(schedule),
            )

        db.delete(sup)
        db.commit()
        log_action(db, current_user, "DELETE_SUPERVISION", "supervisions", sup_id, request=request)
        return {"success": True}

    @staticmethod
    def copy_count_summary(
        db,
        semester: str = "2",
        academic_year: str = "2568",
    ):
        """Generate copy count summary for a semester."""
        from sqlalchemy.orm import joinedload

        schedules = db.query(models.ExamSchedule).join(models.Section).options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.room),
        ).filter(
            models.Section.semester == semester,
            models.Section.academic_year == academic_year,
        ).all()

        section_ids = [schedule.section_id for schedule in schedules]
        submission_map = {}
        if section_ids:
            submissions = db.query(models.ExamSubmission).options(
                joinedload(models.ExamSubmission.material_request),
            ).filter(models.ExamSubmission.section_id.in_(section_ids)).all()
            submission_map = {submission.section_id: submission for submission in submissions}

        rows = []
        total = 0
        for s in schedules:
            sec = s.section
            course = sec.course if sec else None
            submission = submission_map.get(sec.id if sec else -1)
            material_request = submission.material_request if submission else None
            rows.append({
                "course_id": course.course_id if course else "",
                "course_name_th": course.course_name_th if course else "",
                "section_no": sec.section_no if sec else "",
                "num_students": sec.num_students if sec else 0,
                "num_pages": s.num_pages,
                "total_sheets": s.total_sheets,
                "exam_date": s.exam_date,
                "exam_time": s.exam_time,
                "room": s.room.room_name if s.room else "",
                "print_duplex": bool(submission.print_duplex) if submission else False,
                "print_staple": submission.print_staple if submission and submission.print_staple else "none",
                "print_staple_page": submission.print_staple_page if submission else None,
                "print_note": submission.print_note if submission else None,
                "a4_pages_count": submission.a4_pages_count if submission else 0,
                "answer_formats": submission.answer_formats if submission else [],
                "answer_paper_sheets": material_request.answer_paper_sheets if material_request else 0,
                "answer_paper_staple": material_request.answer_paper_staple if material_request else False,
                "answer_booklet_count": material_request.answer_booklet_count if material_request else 0,
                "omr_sheet_count": material_request.omr_sheet_count if material_request else 0,
                "scratch_paper_sheets": material_request.scratch_paper_sheets if material_request else 0,
                "special_note": material_request.special_note if material_request else None,
            })
            total += s.total_sheets

        fraud_forms = 150
        grand_total = total + fraud_forms
        return {
            "rows": rows,
            "subtotal_exam": total,
            "fraud_forms": fraud_forms,
            "grand_total": grand_total,
            "cost": grand_total * 0.50,
            "sections_count": len(rows),
        }