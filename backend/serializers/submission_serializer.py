"""
submission_serializer.py — submission list/detail serialization.
"""
from typing import Any


class SubmissionSerializer:
    """Serializes exam submission responses."""

    @staticmethod
    def serialize_submission(sub: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": sub.get("id"),
            "section_id": sub.get("section_id"),
            "status": sub.get("status"),
            "submitted_at": sub.get("submitted_at"),
            "has_uploaded_pdf": sub.get("has_uploaded_pdf", False),
            "print_spec_confirmed": sub.get("print_spec_confirmed", False),
        }

    @staticmethod
    def serialize_submission_detail(sub: dict[str, Any]) -> dict[str, Any]:
        base = SubmissionSerializer.serialize_submission(sub)
        base.update({
            "exam_type_choice": sub.get("exam_type_choice"),
            "material_request": sub.get("material_request"),
            "submitter": sub.get("submitter"),
        })
        return base
