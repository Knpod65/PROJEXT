"""
schedule_policy.py — schedule scope helpers.
"""
from __future__ import annotations

import models
from academic_groups import build_course_group_clause
from auth_utils import get_dept_filter, get_effective_role


def apply_schedule_scope(query, db, current_user: models.User):
    effective = get_effective_role(current_user)
    dept_filter = get_dept_filter(current_user)

    if effective == models.UserRole.teacher:
        from exam_ownership import get_active_exam_period, get_teacher_owned_section_ids

        active_period = get_active_exam_period(db)
        query = query.join(models.Section)
        if active_period:
            owned_section_ids, _ = get_teacher_owned_section_ids(
                db,
                current_user.id,
                active_period.semester,
                active_period.academic_year,
            )
            if owned_section_ids is None:
                query = query.filter(models.Section.teacher_id == current_user.id)
            elif not owned_section_ids:
                query = query.filter(models.Section.id.in_([-1]))
            else:
                query = query.filter(models.Section.id.in_(owned_section_ids))
        else:
            query = query.filter(models.Section.teacher_id == current_user.id)
    elif dept_filter:
        group_clause = build_course_group_clause(models.Course.course_id, dept_filter)
        if group_clause is not None:
            query = query.join(models.Section).join(
                models.Course,
                models.Section.course_id == models.Course.id,
            ).filter(group_clause)
        else:
            query = query.filter(models.ExamSchedule.id.in_([-1]))

    return query
