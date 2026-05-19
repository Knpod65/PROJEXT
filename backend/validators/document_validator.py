"""Document request validators.

These models supplement existing schemas and centralize normalization for the
document-generation endpoints.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from operational_documents import normalize_document_type


class DocumentTypeRequest(BaseModel):
    document_type: str = Field(default="all")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        return normalize_document_type(value)


class DocumentBatchRequest(BaseModel):
    semester: str = Field(default="2")
    academic_year: str = Field(default="2568")
    exam_type: str = Field(default="final")
    document_type: str = Field(default="all")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        return normalize_document_type(value)


class OperationalDocumentExportRequest(BaseModel):
    schedule_id: Optional[int] = None
    course_id: Optional[str] = None
    section_no: Optional[str] = None
    room_id: Optional[int] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    exam_type: Optional[str] = None
    document_type: str = Field(default="all")

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        return normalize_document_type(value)

