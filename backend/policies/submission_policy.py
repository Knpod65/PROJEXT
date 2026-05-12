"""Submission-specific permission and state policies."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import models


_PRINT_STAPLE_CHOICES = frozenset({"none", "corner_left", "side_left", "custom"})


def _effective_role(user: "models.User"):
    from auth_utils import get_effective_role

    return get_effective_role(user)


def is_submission_readonly_actor(user: "models.User") -> bool:
    from auth_utils import is_view_all_role

    return is_view_all_role(user)


def can_teacher_access_section(db, user: "models.User", section: "models.Section | None") -> bool:
    from exam_ownership import teacher_has_section_access

    return bool(section) and teacher_has_section_access(db, user, section)


def can_request_submission_download(user: "models.User") -> bool:
    from models import UserRole

    return _effective_role(user) in (UserRole.admin, UserRole.teacher)


def can_access_submission_messages(user: "models.User") -> bool:
    from models import UserRole

    return _effective_role(user) != UserRole.staff


def is_submission_file_accessible(submission: "models.ExamSubmission") -> bool:
    from models import SubmissionStatus

    return submission.status in (
        SubmissionStatus.approved,
        SubmissionStatus.released,
    )


def valid_print_staple_choices() -> frozenset[str]:
    return _PRINT_STAPLE_CHOICES
