"""Tests for legacy dashboard service scoping."""
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
from database import Base
from services.dashboard_service import DashboardService


def test_dept_supervisor_dashboard_stats_are_group_scoped():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        supervisor = models.User(
            username="dept.gov",
            email="dept.gov@example.test",
            password_hash="x",
            role=models.UserRole.dept_supervisor,
            dept_code="GOV",
        )
        gov_teacher = models.User(
            username="teacher.gov",
            email="teacher.gov@example.test",
            password_hash="x",
            role=models.UserRole.teacher,
            dept_code="GOV",
            is_active=True,
        )
        pa_teacher = models.User(
            username="teacher.pa",
            email="teacher.pa@example.test",
            password_hash="x",
            role=models.UserRole.teacher,
            dept_code="PA",
            is_active=True,
        )
        gov_course = models.Course(course_id="127101", course_name_en="GOV")
        pa_course = models.Course(course_id="128101", course_name_en="PA")
        session.add_all([supervisor, gov_teacher, pa_teacher, gov_course, pa_course])
        session.flush()

        gov_section = models.Section(
            course_id=gov_course.id,
            section_no="1",
            teacher_id=gov_teacher.id,
            semester="2",
            academic_year="2568",
            num_students=20,
        )
        pa_section = models.Section(
            course_id=pa_course.id,
            section_no="1",
            teacher_id=pa_teacher.id,
            semester="2",
            academic_year="2568",
            num_students=50,
        )
        session.add_all([gov_section, pa_section])
        session.flush()

        session.add_all([
            models.ExamSchedule(section_id=gov_section.id, total_sheets=40, room_id=1),
            models.ExamSchedule(section_id=pa_section.id, total_sheets=100, room_id=2),
        ])
        session.commit()

        stats = DashboardService.get_dashboard_stats(session, "2", "2568", supervisor)

        assert stats["total_sections"] == 1
        assert stats["total_students"] == 20
        assert stats["scheduled_sections"] == 1
        assert stats["unscheduled_sections"] == 0
        assert stats["total_sheets"] == 190
        assert stats["rooms_in_use"] == 1
        assert stats["total_teachers"] == 1
        assert stats["recent_logs"] == []
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
