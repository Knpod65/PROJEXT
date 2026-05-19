"""Faculty config service — CRUD + lookup over FacultyConfigRepository.

All functions are pure logic (no HTTP, no ORM calls directly).
"""
from __future__ import annotations

from datetime import datetime, timezone

from config_models.faculty_config import FacultyConfig, make_faculty_config
from repositories.faculty_config_repository import FacultyConfigRepository


_DEFAULT_FACULTY_NAME_FALLBACK = (
    "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่"
)


def create_faculty_config(
    config: FacultyConfig,
    repo: FacultyConfigRepository,
) -> FacultyConfig:
    """Save a new faculty config. Raises ValueError on duplicate faculty_id or code."""
    if repo.get_by_id(config.faculty_id) is not None:
        raise ValueError(f"Faculty config with id={config.faculty_id} already exists.")
    if repo.get_by_code(config.code) is not None:
        raise ValueError(f"Faculty config with code={config.code!r} already exists.")
    return repo.save(config)


def get_faculty_config(
    faculty_id: int,
    repo: FacultyConfigRepository,
) -> FacultyConfig | None:
    return repo.get_by_id(faculty_id)


def get_faculty_config_by_code(
    code: str,
    repo: FacultyConfigRepository,
) -> FacultyConfig | None:
    return repo.get_by_code(code)


def list_faculty_configs(repo: FacultyConfigRepository) -> list[FacultyConfig]:
    return list(repo.list_all())


def list_active_faculty_configs(repo: FacultyConfigRepository) -> list[FacultyConfig]:
    return list(repo.list_active())


def update_faculty_config(
    config: FacultyConfig,
    repo: FacultyConfigRepository,
) -> FacultyConfig:
    """Replace an existing faculty config. Raises ValueError if not found.

    Auto-updates updated_at to UTC now; preserves original created_at.
    """
    existing = repo.get_by_id(config.faculty_id)
    if existing is None:
        raise ValueError(f"Faculty config with id={config.faculty_id} does not exist.")
    now = datetime.now(timezone.utc).isoformat()
    updated = FacultyConfig(
        faculty_id=config.faculty_id,
        code=config.code,
        name_th=config.name_th,
        name_en=config.name_en,
        email_domain=config.email_domain,
        timezone=config.timezone,
        academic_year_default=config.academic_year_default,
        semester_default=config.semester_default,
        is_active=config.is_active,
        created_at=existing.created_at,
        updated_at=now,
        metadata=config.metadata,
    )
    return repo.save(updated)


def delete_faculty_config(
    faculty_id: int,
    repo: FacultyConfigRepository,
) -> bool:
    """Delete faculty config by id. Returns True if deleted, False if not found."""
    return repo.delete(faculty_id)


def get_faculty_name(
    faculty_id: int | None,
    repo: FacultyConfigRepository,
    *,
    lang: str = "th",
    fallback: str = _DEFAULT_FACULTY_NAME_FALLBACK,
) -> str:
    """Return the faculty display name in the requested language.

    Safe replacement for the hardcoded FACULTY_NAME constant in operational_documents.py.
    Returns `fallback` when faculty_id is None or not found.
    """
    if faculty_id is None:
        return fallback
    config = repo.get_by_id(faculty_id)
    if config is None:
        return fallback
    return config.name_th if lang == "th" else config.name_en
