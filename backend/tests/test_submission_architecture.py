"""
Targeted tests for the incremental submissions router extraction layer.
"""
import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from policies.submission_policy import (
    can_access_submission_messages,
    can_request_submission_download,
    can_teacher_access_section,
    is_submission_file_accessible,
    is_submission_readonly_actor,
    valid_print_staple_choices,
)
from repositories.submission_repository import SubmissionRepository
from services.exceptions import EMSNotFoundError, EMSPermissionError, EMSValidationError
from services.submission_service import (
    apply_snapshot_to_submission,
    assert_message_access,
    assert_request_access_allowed,
    build_access_watermark,
    build_submission_filename,
    get_access_log_action,
    get_or_create_submission,
    normalize_submission_list_inputs,
    validate_message_text,
    validate_print_staple_choice,
)


def _make_user(role: str, **kwargs):
    user = MagicMock()
    user.role = models.UserRole(role)
    user.view_as_role = kwargs.get("view_as_role")
    user._active_role = kwargs.get("_active_role", user.role)
    user.id = kwargs.get("id", 1)
    user.username = kwargs.get("username", role)
    user.full_name = kwargs.get("full_name", f"{role.title()} User")
    user.email = kwargs.get("email", f"{role}@example.com")
    return user


def _make_section():
    section = MagicMock()
    section.id = 101
    section.course = MagicMock()
    section.course.course_id = "GOV/101"
    section.course.course_name_th = "Governance"
    section.section_no = "1/1"
    return section


def _make_submission(status=models.SubmissionStatus.draft):
    submission = MagicMock()
    submission.id = 11
    submission.section_id = 101
    submission.section = _make_section()
    submission.status = status
    submission.date_confirmed = False
    submission.exam_type_choice = None
    submission.answer_formats = None
    submission.a4_pages_count = 0
    submission.no_cover_page_confirmed = False
    submission.is_shared_exam = False
    return submission


class TestSubmissionPolicyHelpers:
    def test_is_submission_readonly_actor_matches_view_all_roles(self):
        assert is_submission_readonly_actor(_make_user("esq_head")) is True
        assert is_submission_readonly_actor(_make_user("secretary")) is True
        assert is_submission_readonly_actor(_make_user("teacher")) is False

    def test_can_request_submission_download_allows_admin_and_teacher_only(self):
        assert can_request_submission_download(_make_user("admin")) is True
        assert can_request_submission_download(_make_user("teacher")) is True
        assert can_request_submission_download(_make_user("dept_supervisor")) is False

    def test_can_access_submission_messages_blocks_staff(self):
        assert can_access_submission_messages(_make_user("staff")) is False
        assert can_access_submission_messages(_make_user("admin")) is True

    def test_is_submission_file_accessible_requires_approved_state(self):
        assert is_submission_file_accessible(_make_submission(models.SubmissionStatus.approved)) is True
        assert is_submission_file_accessible(_make_submission(models.SubmissionStatus.released)) is True
        assert is_submission_file_accessible(_make_submission(models.SubmissionStatus.draft)) is False

    def test_valid_print_staple_choices_is_stable(self):
        assert valid_print_staple_choices() == frozenset({"none", "corner_left", "side_left", "custom"})

    def test_can_teacher_access_section_delegates_ownership_helper(self):
        with patch("exam_ownership.teacher_has_section_access", return_value=True) as mocked:
            allowed = can_teacher_access_section(MagicMock(), _make_user("teacher"), _make_section())
        assert allowed is True
        mocked.assert_called_once()


class TestSubmissionRepository:
    def test_get_by_section_id_uses_submission_query(self):
        db = MagicMock()
        expected = object()
        db.query.return_value.filter.return_value.first.return_value = expected

        repo = SubmissionRepository(db)

        assert repo.get_by_section_id(5) is expected
        db.query.assert_called_with(models.ExamSubmission)

    def test_list_messages_loads_sender_and_orders_by_created_at(self):
        db = MagicMock()
        expected = [MagicMock()]
        db.query.return_value.options.return_value.filter.return_value.order_by.return_value.all.return_value = expected

        repo = SubmissionRepository(db)

        assert repo.list_messages(9) == expected
        db.query.assert_called_with(models.ExamMessage)

    def test_get_access_token_filters_active_token(self):
        db = MagicMock()
        expected = MagicMock()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = expected

        repo = SubmissionRepository(db)

        assert repo.get_access_token("abc") is expected
        db.query.assert_called_with(models.ExamAccessToken)


class TestSubmissionServiceHelpers:
    def test_normalize_submission_list_inputs_clamps_legacy_values(self):
        assert normalize_submission_list_inputs(page=0, limit=500) == (1, 200)
        assert normalize_submission_list_inputs(page=2, limit=50) == (2, 50)

    def test_get_or_create_submission_returns_existing_submission(self):
        repo = MagicMock()
        db = MagicMock()
        existing = _make_submission()
        repo.get_by_section_id.return_value = existing

        assert get_or_create_submission(db, repo, 101, _make_user("admin")) is existing
        db.add.assert_not_called()

    def test_get_or_create_submission_raises_for_missing_section(self):
        repo = MagicMock()
        db = MagicMock()
        repo.get_by_section_id.return_value = None
        repo.get_section.return_value = None

        with pytest.raises(EMSNotFoundError):
            get_or_create_submission(db, repo, 404, _make_user("admin"))

    def test_get_or_create_submission_blocks_teacher_without_access(self):
        repo = MagicMock()
        db = MagicMock()
        repo.get_by_section_id.return_value = None
        repo.get_section.return_value = _make_section()

        with patch("services.submission_service.can_teacher_access_section", return_value=False):
            with pytest.raises(EMSPermissionError):
                get_or_create_submission(db, repo, 101, _make_user("teacher"))

    def test_get_or_create_submission_creates_draft_when_allowed(self):
        repo = MagicMock()
        db = MagicMock()
        repo.get_by_section_id.return_value = None
        repo.get_section.return_value = _make_section()

        submission = get_or_create_submission(db, repo, 101, _make_user("admin", id=55))

        assert submission.section_id == 101
        assert submission.submitted_by == 55
        assert submission.status == models.SubmissionStatus.draft
        db.add.assert_called_once()
        db.flush.assert_called_once()

    def test_validate_message_text_trims_and_rejects_invalid_values(self):
        assert validate_message_text("  hello  ") == "hello"
        with pytest.raises(EMSValidationError):
            validate_message_text("   ")
        with pytest.raises(EMSValidationError):
            validate_message_text("x" * 2001)

    def test_validate_print_staple_choice_accepts_known_values(self):
        assert validate_print_staple_choice("custom") == "custom"
        with pytest.raises(EMSValidationError):
            validate_print_staple_choice("invalid")

    def test_build_submission_filename_sanitizes_slashes(self):
        filename = build_submission_filename(_make_submission())
        assert filename == "GOV-101_section-1-1.pdf"

    def test_build_access_watermark_uses_actor_identity_and_time(self):
        watermark = build_access_watermark(
            _make_user("teacher", full_name="Jane Teacher", username="jane", email="jane@example.com"),
            now=datetime(2026, 5, 12, 8, 30, tzinfo=timezone.utc),
        )
        assert watermark == "Jane Teacher | jane@example.com | 2026-05-12 08:30"

    def test_get_access_log_action_maps_token_purpose(self):
        assert get_access_log_action(models.TokenPurpose.view) == "viewed"
        assert get_access_log_action(models.TokenPurpose.download) == "downloaded"
        assert get_access_log_action(models.TokenPurpose.print) == "printed"

    def test_apply_snapshot_to_submission_restores_expected_fields(self):
        submission = _make_submission(models.SubmissionStatus.approved)
        snapshot = {
            "date_confirmed": True,
            "exam_type_choice": models.ExamTypeChoice.onsite,
            "answer_formats": ["pdf"],
            "a4_pages_count": 12,
            "no_cover_page_confirmed": True,
            "is_shared_exam": True,
        }

        apply_snapshot_to_submission(submission, snapshot)

        assert submission.date_confirmed is True
        assert submission.exam_type_choice == models.ExamTypeChoice.onsite
        assert submission.answer_formats == ["pdf"]
        assert submission.a4_pages_count == 12
        assert submission.no_cover_page_confirmed is True
        assert submission.is_shared_exam is True
        assert submission.status == models.SubmissionStatus.draft

    def test_assert_message_access_blocks_staff(self):
        repo = MagicMock()
        repo.get_with_section.return_value = _make_submission()

        with pytest.raises(EMSPermissionError):
            assert_message_access(MagicMock(), repo, 11, _make_user("staff"))

    def test_assert_message_access_checks_teacher_ownership(self):
        repo = MagicMock()
        repo.get_with_section.return_value = _make_submission()

        with patch("services.submission_service.can_teacher_access_section", return_value=False):
            with pytest.raises(EMSPermissionError):
                assert_message_access(MagicMock(), repo, 11, _make_user("teacher"))

    def test_assert_request_access_allowed_requires_accessible_submission_state(self):
        repo = MagicMock()
        repo.get_with_section.return_value = _make_submission(models.SubmissionStatus.draft)

        with pytest.raises(EMSValidationError):
            assert_request_access_allowed(
                MagicMock(),
                repo,
                11,
                models.TokenPurpose.view,
                _make_user("admin"),
            )

    def test_assert_request_access_allowed_blocks_download_for_non_download_role(self):
        repo = MagicMock()
        repo.get_with_section.return_value = _make_submission(models.SubmissionStatus.approved)

        with pytest.raises(EMSPermissionError):
            assert_request_access_allowed(
                MagicMock(),
                repo,
                11,
                models.TokenPurpose.download,
                _make_user("dept_supervisor"),
            )
