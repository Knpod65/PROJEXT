"""Central PDPA policy helpers for consistent data-sensitivity decisions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DataSensitivity(str, Enum):
    public = "public"
    authenticated = "authenticated"
    role_restricted = "role_restricted"
    sensitive = "sensitive"
    critical = "critical"


@dataclass(frozen=True)
class DataFieldPolicy:
    field_name: str
    sensitivity: DataSensitivity
    default_exposure: str
    mask_in_logs: bool
    owner_access_allowed: bool = False
    notes: str = ""


_DEFAULT_POLICY = DataFieldPolicy(
    field_name="unknown",
    sensitivity=DataSensitivity.role_restricted,
    default_exposure="deny-by-default",
    mask_in_logs=True,
    owner_access_allowed=False,
    notes="Unclassified field; treat conservatively until mapped.",
)

_FIELD_POLICIES: dict[str, DataFieldPolicy] = {
    "student_id": DataFieldPolicy(
        field_name="student_id",
        sensitivity=DataSensitivity.sensitive,
        default_exposure="authenticated-owner-or-privileged-staff",
        mask_in_logs=True,
        owner_access_allowed=True,
        notes="Stable student identifier; mask in logs and exports unless required.",
    ),
    "student_name": DataFieldPolicy(
        field_name="student_name",
        sensitivity=DataSensitivity.sensitive,
        default_exposure="authenticated-owner-or-privileged-staff",
        mask_in_logs=True,
        owner_access_allowed=True,
        notes="Direct student PII.",
    ),
    "teacher_name": DataFieldPolicy(
        field_name="teacher_name",
        sensitivity=DataSensitivity.role_restricted,
        default_exposure="authenticated-role-restricted",
        mask_in_logs=False,
        owner_access_allowed=False,
        notes="Operationally useful but still personally identifying.",
    ),
    "staff_name": DataFieldPolicy(
        field_name="staff_name",
        sensitivity=DataSensitivity.role_restricted,
        default_exposure="authenticated-role-restricted",
        mask_in_logs=False,
        owner_access_allowed=False,
        notes="Operational staff identity for room and print workflows.",
    ),
    "exam_room": DataFieldPolicy(
        field_name="exam_room",
        sensitivity=DataSensitivity.role_restricted,
        default_exposure="authenticated-role-restricted",
        mask_in_logs=False,
        owner_access_allowed=True,
        notes="Safe for owners; restrict broad public exposure with schedule context.",
    ),
    "exam_schedule": DataFieldPolicy(
        field_name="exam_schedule",
        sensitivity=DataSensitivity.sensitive,
        default_exposure="authenticated-owner-or-privileged-staff",
        mask_in_logs=False,
        owner_access_allowed=True,
        notes="Schedule timing becomes sensitive when joined with identity data.",
    ),
    "uploaded_file": DataFieldPolicy(
        field_name="uploaded_file",
        sensitivity=DataSensitivity.critical,
        default_exposure="role-restricted-with-audit",
        mask_in_logs=True,
        owner_access_allowed=False,
        notes="Uploaded exam content must never leak through raw logs.",
    ),
    "pdf_file": DataFieldPolicy(
        field_name="pdf_file",
        sensitivity=DataSensitivity.critical,
        default_exposure="role-restricted-with-audit",
        mask_in_logs=True,
        owner_access_allowed=False,
        notes="Generated exam PDFs are critical content.",
    ),
    "qr_token": DataFieldPolicy(
        field_name="qr_token",
        sensitivity=DataSensitivity.critical,
        default_exposure="never-public",
        mask_in_logs=True,
        owner_access_allowed=False,
        notes="Bearer-like pickup token; always redact in audit and error paths.",
    ),
    "export_data": DataFieldPolicy(
        field_name="export_data",
        sensitivity=DataSensitivity.critical,
        default_exposure="role-restricted-with-audit",
        mask_in_logs=True,
        owner_access_allowed=False,
        notes="Exports can aggregate large PII sets and require audit traceability.",
    ),
}


def _role_value(role: object) -> str | None:
    if role is None:
        return None
    value = getattr(role, "value", role)
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def get_field_policy(field_name: str) -> DataFieldPolicy:
    return _FIELD_POLICIES.get(field_name, _DEFAULT_POLICY)


def should_mask_in_logs(field_name: str) -> bool:
    return get_field_policy(field_name).mask_in_logs


def can_view_student_personal_data(role: object, is_owner: bool = False) -> bool:
    if is_owner:
        return True
    return _role_value(role) in {"admin", "esq_head", "secretary", "staff"}


def can_export_sensitive_schedule_data(role: object) -> bool:
    return _role_value(role) in {"admin", "esq_head", "secretary"}


def mask_student_id(student_id: str | None) -> str | None:
    if student_id is None:
        return None
    cleaned = student_id.strip()
    if not cleaned:
        return ""
    if len(cleaned) <= 4:
        return "*" * len(cleaned)
    return f"{'*' * (len(cleaned) - 4)}{cleaned[-4:]}"


def redact_for_audit(field_name: str, value: object) -> object:
    if value is None:
        return None
    if not should_mask_in_logs(field_name):
        return value
    if field_name == "student_id":
        return mask_student_id(str(value))
    if field_name in {"student_name", "teacher_name", "staff_name"}:
        return "[REDACTED_NAME]"
    if field_name == "qr_token":
        return "[REDACTED_QR_TOKEN]"
    if field_name in {"uploaded_file", "pdf_file", "export_data"}:
        return "[REDACTED_CONTENT]"
    return "[REDACTED]"
