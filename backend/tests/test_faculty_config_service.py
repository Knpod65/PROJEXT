"""Tests for D3.1 — faculty config domain foundation."""
import os
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.faculty_config import FacultyConfig, make_faculty_config
from repositories.faculty_config_repository import InMemoryFacultyConfigRepository
from services.faculty_config_service import (
    create_faculty_config,
    delete_faculty_config,
    get_faculty_config,
    get_faculty_config_by_code,
    get_faculty_name,
    list_active_faculty_configs,
    list_faculty_configs,
    update_faculty_config,
)
from policies.faculty_config_policy import (
    assert_faculty_config_write_allowed,
    can_create_faculty_config,
    can_delete_faculty_config,
    can_read_faculty_config,
    can_update_faculty_config,
)
from services.exceptions import EMSPermissionError


def _repo() -> InMemoryFacultyConfigRepository:
    return InMemoryFacultyConfigRepository()


def _pol_config(**kwargs) -> FacultyConfig:
    defaults = dict(
        faculty_id=1,
        code="POL",
        name_th="คณะรัฐศาสตร์และรัฐประศาสนศาสตร์",
        name_en="Faculty of Political Science and Public Administration",
        email_domain="polsci.cmu.ac.th",
    )
    defaults.update(kwargs)
    return make_faculty_config(**defaults)


# ── make_faculty_config ───────────────────────────────────────────────────────

def test_make_faculty_config_populates_all_fields():
    c = _pol_config()
    assert c.faculty_id == 1
    assert c.code == "POL"
    assert c.name_th == "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์"
    assert c.name_en == "Faculty of Political Science and Public Administration"
    assert c.email_domain == "polsci.cmu.ac.th"
    assert c.timezone == "Asia/Bangkok"
    assert c.academic_year_default == "2568"
    assert c.semester_default == "2"
    assert c.is_active is True
    assert isinstance(c.created_at, str) and "T" in c.created_at
    assert isinstance(c.updated_at, str) and "T" in c.updated_at
    assert c.metadata == {}


def test_make_faculty_config_auto_generates_timestamps():
    c = _pol_config()
    assert c.created_at == c.updated_at


def test_make_faculty_config_metadata_is_copy():
    meta = {"key": "val"}
    c = _pol_config(metadata=meta)
    meta["key"] = "mutated"
    assert c.metadata["key"] == "val"


def test_faculty_config_is_frozen():
    c = _pol_config()
    with pytest.raises(Exception):
        c.code = "MUTATED"  # type: ignore[misc]


# ── create / get ─────────────────────────────────────────────────────────────

def test_create_and_get_faculty_config():
    repo = _repo()
    c = _pol_config()
    created = create_faculty_config(c, repo)
    assert created.faculty_id == 1
    found = get_faculty_config(1, repo)
    assert found is not None
    assert found.code == "POL"


def test_create_raises_on_duplicate_faculty_id():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    with pytest.raises(ValueError, match="already exists"):
        create_faculty_config(_pol_config(), repo)


def test_create_raises_on_duplicate_code():
    repo = _repo()
    create_faculty_config(_pol_config(faculty_id=1, code="POL"), repo)
    with pytest.raises(ValueError, match="already exists"):
        create_faculty_config(_pol_config(faculty_id=2, code="POL"), repo)


def test_get_returns_none_for_unknown_id():
    assert get_faculty_config(999, _repo()) is None


def test_get_by_code_case_insensitive():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    assert get_faculty_config_by_code("pol", repo) is not None
    assert get_faculty_config_by_code("POL", repo) is not None
    assert get_faculty_config_by_code("Pol", repo) is not None


# ── list ─────────────────────────────────────────────────────────────────────

def test_list_active_filters_inactive():
    repo = _repo()
    active = make_faculty_config(1, "POL", "คณะ", "Faculty", is_active=True)
    inactive = make_faculty_config(2, "ENG", "วิศวะ", "Engineering", is_active=False)
    create_faculty_config(active, repo)
    create_faculty_config(inactive, repo)
    result = list_active_faculty_configs(repo)
    assert len(result) == 1
    assert result[0].code == "POL"


def test_list_configs_returns_all():
    repo = _repo()
    create_faculty_config(make_faculty_config(1, "POL", "คณะ", "Faculty"), repo)
    create_faculty_config(make_faculty_config(2, "ENG", "วิศวะ", "Engineering"), repo)
    assert len(list_faculty_configs(repo)) == 2


def test_list_configs_returns_copy():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    result = list_faculty_configs(repo)
    result.clear()
    assert len(list_faculty_configs(repo)) == 1


# ── update ────────────────────────────────────────────────────────────────────

def test_update_faculty_config_raises_if_not_found():
    with pytest.raises(ValueError, match="does not exist"):
        update_faculty_config(_pol_config(), _repo())


def test_update_preserves_created_at_updates_updated_at():
    repo = _repo()
    original = _pol_config()
    create_faculty_config(original, repo)
    time.sleep(0.01)
    updated_config = make_faculty_config(
        1, "POL", "คณะ (updated)", "Faculty (updated)"
    )
    result = update_faculty_config(updated_config, repo)
    assert result.created_at == original.created_at
    assert result.updated_at != original.updated_at
    assert result.name_th == "คณะ (updated)"


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_returns_true_on_success():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    assert delete_faculty_config(1, repo) is True


def test_delete_returns_false_if_not_found():
    assert delete_faculty_config(999, _repo()) is False


# ── get_faculty_name ─────────────────────────────────────────────────────────

def test_get_faculty_name_returns_thai_by_default():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    assert get_faculty_name(1, repo) == "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์"


def test_get_faculty_name_returns_english():
    repo = _repo()
    create_faculty_config(_pol_config(), repo)
    assert get_faculty_name(1, repo, lang="en") == (
        "Faculty of Political Science and Public Administration"
    )


def test_get_faculty_name_returns_fallback_for_none():
    fallback = "FALLBACK"
    assert get_faculty_name(None, _repo(), fallback=fallback) == "FALLBACK"


def test_get_faculty_name_returns_fallback_for_unknown():
    assert get_faculty_name(999, _repo(), fallback="UNKNOWN") == "UNKNOWN"


# ── policy ────────────────────────────────────────────────────────────────────

def test_can_create_only_for_admin():
    assert can_create_faculty_config("admin") is True
    assert can_create_faculty_config("esq_head") is False
    assert can_create_faculty_config("teacher") is False


def test_can_update_only_for_admin():
    assert can_update_faculty_config("admin") is True
    assert can_update_faculty_config("staff") is False


def test_can_delete_only_for_admin():
    assert can_delete_faculty_config("admin") is True


def test_can_read_for_any_role():
    for role in ("admin", "esq_head", "secretary", "teacher", "staff", "dept_supervisor"):
        assert can_read_faculty_config(role) is True


def test_assert_write_allowed_raises_for_non_admin():
    with pytest.raises(EMSPermissionError):
        assert_faculty_config_write_allowed("teacher")


def test_assert_write_allowed_no_op_for_admin():
    assert_faculty_config_write_allowed("admin")  # must not raise


# ── thread safety ─────────────────────────────────────────────────────────────

def test_concurrent_saves_do_not_corrupt():
    repo = InMemoryFacultyConfigRepository()
    results: list[FacultyConfig] = []
    errors: list[Exception] = []

    def save(fid: int) -> None:
        try:
            cfg = make_faculty_config(fid, f"F{fid}", "คณะ", "Faculty")
            results.append(repo.save(cfg))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=save, args=(i,)) for i in range(1, 11)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(repo.list_all()) == 10
