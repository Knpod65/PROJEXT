"""Non-breaking auth integration scaffolding for faculty callback/authen flows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


DEFAULT_AUTH_PROVIDER = "faculty_it"


@dataclass(frozen=True)
class ExternalIdentity:
    provider: str
    subject: str | None = None
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    employee_id: str | None = None
    student_id: str | None = None
    faculty_code: str | None = None
    department_code: str | None = None
    verified_at: datetime | None = None
    raw_claims: Mapping[str, Any] = field(default_factory=dict)


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    text = str(value).strip()
    return text or None


def supports_callback_path(path: str) -> bool:
    normalized = "/".join(segment for segment in str(path).split("/") if segment)
    return normalized.endswith("callback/authen")


def normalize_external_identity(
    payload: Mapping[str, Any],
    provider: str | None = None,
) -> ExternalIdentity:
    """Normalize faculty IT callback data into a stable EMS identity shape.

    This is intentionally pure and side-effect free. Existing login behavior is
    unchanged until a router chooses to call this service.
    """
    if not payload:
        raise ValueError("payload is required")

    identity = ExternalIdentity(
        provider=_clean_text(provider) or _clean_text(payload.get("provider")) or DEFAULT_AUTH_PROVIDER,
        subject=_clean_text(payload.get("subject") or payload.get("sub") or payload.get("cmu_subject")),
        username=_clean_text(
            payload.get("username")
            or payload.get("cmuitaccount")
            or payload.get("login")
            or payload.get("account")
        ),
        email=_clean_text(payload.get("email") or payload.get("mail")),
        full_name=_clean_text(payload.get("full_name") or payload.get("name") or payload.get("display_name")),
        employee_id=_clean_text(payload.get("employee_id") or payload.get("personnel_id")),
        student_id=_clean_text(payload.get("student_id")),
        faculty_code=_clean_text(payload.get("faculty_code") or payload.get("faculty")),
        department_code=_clean_text(payload.get("department_code") or payload.get("department")),
        verified_at=payload.get("verified_at") if isinstance(payload.get("verified_at"), datetime) else None,
        raw_claims=dict(payload),
    )

    if not any(
        (
            identity.subject,
            identity.username,
            identity.email,
            identity.employee_id,
            identity.student_id,
        )
    ):
        raise ValueError("external identity must contain at least one stable identifier")

    return identity


def build_identity_lookup_candidates(identity: ExternalIdentity) -> list[tuple[str, str]]:
    ordered = [
        ("username", identity.username),
        ("email", identity.email),
        ("employee_id", identity.employee_id),
        ("student_id", identity.student_id),
        ("subject", identity.subject),
    ]
    seen: set[tuple[str, str]] = set()
    results: list[tuple[str, str]] = []
    for key, value in ordered:
        if not value:
            continue
        pair = (key, value)
        if pair in seen:
            continue
        seen.add(pair)
        results.append(pair)
    return results


def build_session_audit_metadata(
    identity: ExternalIdentity,
    channel: str = "faculty_callback",
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "auth_source": identity.provider,
        "auth_channel": channel,
    }
    for key, value in (
        ("upstream_subject", identity.subject),
        ("username", identity.username),
        ("employee_id", identity.employee_id),
        ("student_id", identity.student_id),
        ("faculty_code", identity.faculty_code),
        ("department_code", identity.department_code),
    ):
        if value:
            metadata[key] = value
    return metadata
