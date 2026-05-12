"""Submission repository for incremental router -> service extraction."""
from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

import models


class SubmissionRepository:
    """Reusable query layer for exam submission workflows."""

    def __init__(self, db: Session):
        self.db = db

    def get_section(self, section_id: int) -> models.Section | None:
        return self.db.query(models.Section).filter(models.Section.id == section_id).first()

    def get_by_section_id(self, section_id: int) -> models.ExamSubmission | None:
        return (
            self.db.query(models.ExamSubmission)
            .filter(models.ExamSubmission.section_id == section_id)
            .first()
        )

    def get_detail_by_section_id(self, section_id: int) -> models.ExamSubmission | None:
        return (
            self.db.query(models.ExamSubmission)
            .options(
                joinedload(models.ExamSubmission.section).joinedload(models.Section.course),
                joinedload(models.ExamSubmission.submitter),
                joinedload(models.ExamSubmission.versions),
            )
            .filter(models.ExamSubmission.section_id == section_id)
            .first()
        )

    def query_listing(self):
        return (
            self.db.query(models.ExamSubmission)
            .join(models.Section, models.ExamSubmission.section_id == models.Section.id)
            .options(
                joinedload(models.ExamSubmission.section).joinedload(models.Section.course),
                joinedload(models.ExamSubmission.submitter),
            )
        )

    def get_by_id(self, submission_id: int) -> models.ExamSubmission | None:
        return (
            self.db.query(models.ExamSubmission)
            .filter(models.ExamSubmission.id == submission_id)
            .first()
        )

    def get_with_section(self, submission_id: int) -> models.ExamSubmission | None:
        return (
            self.db.query(models.ExamSubmission)
            .options(joinedload(models.ExamSubmission.section))
            .filter(models.ExamSubmission.id == submission_id)
            .first()
        )

    def get_with_section_course(self, submission_id: int) -> models.ExamSubmission | None:
        return (
            self.db.query(models.ExamSubmission)
            .options(
                joinedload(models.ExamSubmission.section).joinedload(models.Section.course)
            )
            .filter(models.ExamSubmission.id == submission_id)
            .first()
        )

    def get_access_token(self, token: str) -> models.ExamAccessToken | None:
        return (
            self.db.query(models.ExamAccessToken)
            .options(
                joinedload(models.ExamAccessToken.submission)
                .joinedload(models.ExamSubmission.section)
                .joinedload(models.Section.course)
            )
            .filter(
                models.ExamAccessToken.token == token,
                models.ExamAccessToken.revoked.is_(False),
            )
            .first()
        )

    def list_versions(self, submission_id: int) -> list[models.ExamSubmissionVersion]:
        return (
            self.db.query(models.ExamSubmissionVersion)
            .filter(models.ExamSubmissionVersion.submission_id == submission_id)
            .order_by(models.ExamSubmissionVersion.version.desc())
            .all()
        )

    def get_version(self, submission_id: int, version: int) -> models.ExamSubmissionVersion | None:
        return (
            self.db.query(models.ExamSubmissionVersion)
            .filter(
                models.ExamSubmissionVersion.submission_id == submission_id,
                models.ExamSubmissionVersion.version == version,
            )
            .first()
        )

    def list_messages(self, submission_id: int) -> list[models.ExamMessage]:
        return (
            self.db.query(models.ExamMessage)
            .options(joinedload(models.ExamMessage.sender))
            .filter(models.ExamMessage.submission_id == submission_id)
            .order_by(models.ExamMessage.created_at)
            .all()
        )
