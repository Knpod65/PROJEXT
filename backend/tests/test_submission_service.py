"""
Tests for services/submission_service.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock, patch


def _make_submission(**kwargs):
    sub = MagicMock()
    sub.id = kwargs.get("id", 1)
    sub.date_confirmed = kwargs.get("date_confirmed", None)
    sub.exam_type_choice = kwargs.get("exam_type_choice", None)
    sub.answer_formats = kwargs.get("answer_formats", None)
    sub.a4_pages_count = kwargs.get("a4_pages_count", 0)
    sub.has_uploaded_pdf = kwargs.get("has_uploaded_pdf", False)
    sub.no_cover_page_confirmed = kwargs.get("no_cover_page_confirmed", False)
    sub.is_shared_exam = kwargs.get("is_shared_exam", False)
    sub.shared_with_sections = kwargs.get("shared_with_sections", None)
    sub.print_duplex = kwargs.get("print_duplex", False)
    sub.print_staple = kwargs.get("print_staple", False)
    sub.print_staple_page = kwargs.get("print_staple_page", None)
    sub.print_note = kwargs.get("print_note", None)
    sub.print_spec_confirmed = kwargs.get("print_spec_confirmed", False)
    sub.status = kwargs.get("status", "draft")
    sub.version = kwargs.get("version", 1)
    sub.section = kwargs.get("section", None)
    return sub


def _make_section(num_students=0, schedules=None):
    sec = MagicMock()
    sec.num_students = num_students
    sec.schedules = schedules or []
    return sec


class TestSnapshotSubmission:
    def test_returns_dict_with_all_fields(self):
        from services.submission_service import snapshot_submission
        sub = _make_submission(date_confirmed="2026-01-01", status="draft")
        snap = snapshot_submission(sub)
        assert isinstance(snap, dict)
        assert snap["date_confirmed"] == "2026-01-01"
        assert snap["status"] == "draft"

    def test_snapshot_keys_are_complete(self):
        from services.submission_service import snapshot_submission
        sub = _make_submission()
        snap = snapshot_submission(sub)
        expected_keys = {
            "date_confirmed", "exam_type_choice", "answer_formats",
            "a4_pages_count", "has_uploaded_pdf", "no_cover_page_confirmed",
            "is_shared_exam", "shared_with_sections", "print_duplex",
            "print_staple", "print_staple_page", "print_note",
            "print_spec_confirmed", "status",
        }
        assert expected_keys == set(snap.keys())

    def test_snapshot_is_not_the_model_object(self):
        from services.submission_service import snapshot_submission
        sub = _make_submission()
        snap = snapshot_submission(sub)
        assert snap is not sub


class TestSaveVersion:
    def _make_db_with_count(self, count):
        db = MagicMock()
        query_chain = db.query.return_value.filter.return_value
        query_chain.count.return_value = count
        return db

    def test_creates_version_record(self):
        from services.submission_service import save_version
        db = self._make_db_with_count(2)
        sub = _make_submission(id=5)
        user = MagicMock()
        user.id = 99
        ver = save_version(db, sub, user, reason="test")
        db.add.assert_called_once()
        assert sub.version == 3

    def test_version_number_increments(self):
        from services.submission_service import save_version
        db = self._make_db_with_count(0)
        sub = _make_submission(id=1)
        user = MagicMock()
        user.id = 1
        save_version(db, sub, user)
        assert sub.version == 1

    def test_no_db_commit(self):
        from services.submission_service import save_version
        db = self._make_db_with_count(0)
        sub = _make_submission(id=1)
        user = MagicMock()
        user.id = 1
        save_version(db, sub, user)
        db.commit.assert_not_called()


class TestGetPrintPriority:
    def test_high_by_student_count(self):
        from services.submission_service import get_print_priority
        sub = _make_submission(section=_make_section(num_students=150))
        assert get_print_priority(sub) == "high"

    def test_medium_by_student_count(self):
        from services.submission_service import get_print_priority
        sub = _make_submission(section=_make_section(num_students=80))
        assert get_print_priority(sub) == "medium"

    def test_standard_by_student_count(self):
        from services.submission_service import get_print_priority
        sub = _make_submission(section=_make_section(num_students=10))
        assert get_print_priority(sub) == "standard"

    def test_no_section_gives_standard(self):
        from services.submission_service import get_print_priority
        sub = _make_submission(section=None)
        assert get_print_priority(sub) == "standard"

    def test_high_by_pages_duplex(self):
        from services.submission_service import get_print_priority
        sub = _make_submission(
            print_duplex=True, a4_pages_count=20,
            section=_make_section(num_students=5),
        )
        assert get_print_priority(sub) == "high"

    def test_thresholds_use_settings(self):
        from config.settings import settings
        from services.submission_service import get_print_priority
        sub = _make_submission(section=_make_section(num_students=settings.print_priority_high_threshold))
        assert get_print_priority(sub) == "high"


class TestUpsertPrintQueueJob:
    def _make_db_no_existing_job(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        return db

    def _make_db_existing_job(self, status="queued"):
        import models as m
        db = MagicMock()
        job = MagicMock()
        job.status = m.PrintJobStatus.queued if status == "queued" else m.PrintJobStatus.delivered
        db.query.return_value.filter.return_value.first.return_value = job
        return db, job

    def test_creates_new_job_if_none(self):
        from services.submission_service import upsert_print_queue_job
        db = self._make_db_no_existing_job()
        sub = _make_submission(section=_make_section(num_students=5))
        user = MagicMock()
        user.id = 1
        job = upsert_print_queue_job(db, sub, user, "token123")
        db.add.assert_called_once()
        assert job.release_token == "token123"

    def test_no_db_commit(self):
        from services.submission_service import upsert_print_queue_job
        db = self._make_db_no_existing_job()
        sub = _make_submission(section=_make_section(num_students=5))
        user = MagicMock()
        user.id = 1
        upsert_print_queue_job(db, sub, user, "token")
        db.commit.assert_not_called()

    def test_requeues_delivered_job(self):
        import models as m
        from services.submission_service import upsert_print_queue_job
        db, job = self._make_db_existing_job(status="delivered")
        sub = _make_submission(section=_make_section(num_students=5))
        user = MagicMock()
        user.id = 1
        upsert_print_queue_job(db, sub, user, "newtoken")
        assert job.status == m.PrintJobStatus.queued
        assert job.release_token == "newtoken"
