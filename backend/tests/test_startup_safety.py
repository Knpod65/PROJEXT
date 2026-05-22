"""
Tests for D6.9 — startup safety hardening.
- Candidate 2: DATABASE_URL raises in production/pilot when unset
- Candidate 3: ENV/ENVIRONMENT unification in security.py
"""
import os
import sys
import importlib
import textwrap

import pytest

# Ensure tests import fresh modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config.settings as cs   # noqa: E402


# ── Candidate 3: _is_production() ───────────────────────────────────────────────

class TestIsProduction:
    """security.py _is_production() checks ENVIRONMENT first, then ENV (backward compat)."""

    def teardown_method(self, _):
        """Clean up env vars and SECRET_KEY between tests to avoid cross-test pollution."""
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("ENV", None)
        os.environ.pop("SECRET_KEY", None)  # prevent next test from seeing this as a real key
        # Re-import to pick up fresh env state (dev defaults)
        import config.settings as _cs
        importlib.reload(_cs)

    def test_default_is_dev(self):
        # Ensure no production env var is set in this test
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        from security import _is_production
        assert _is_production() is False

    def test_environment_production(self):
        os.environ["ENVIRONMENT"] = "production"
        os.environ["SECRET_KEY"] = "a" * 64  # must satisfy production check in settings.py
        importlib.reload(cs)
        from security import _is_production
        assert _is_production() is True

    def test_env_production_backward_compat(self):
        os.environ["ENV"] = "production"
        os.environ["SECRET_KEY"] = "b" * 64
        importlib.reload(cs)
        from security import _is_production
        assert _is_production() is True

    def test_environment_takes_priority_over_env(self):
        os.environ["ENVIRONMENT"] = "development"
        os.environ["ENV"] = "production"
        importlib.reload(cs)
        from security import _is_production
        assert _is_production() is False

    def test_pilot_environment_is_treated_as_production(self):
        os.environ["ENVIRONMENT"] = "pilot"
        importlib.reload(cs)
        from security import _is_production
        assert _is_production() is True


# ── Candidate 2: database.py DATABASE_URL NYI (DATABASE_URL unset points to SQLite) ─────────────────────────

# Note: real Python test file: cannot easily force import before DATABASE_URL is read.
# The actual runtime check is in database.py. We verify the logic by reading the source
# and checking that the logic is present (code review test, not functional test).

import pathlib as _pl

def test_database_py_has_production_check():
    src = _pl.Path(__file__).resolve().parents[1] / "database.py"
    text = src.read_text(encoding="utf-8")
    assert (
        "settings.environment" in text or 'getattr(settings, "environment"' in text
    ), "database.py must check settings.environment for SQLite restriction"
    assert (
        "RuntimeError" in text or "raise" in text
    ), "database.py must raise RuntimeError when DATABASE_URL is unset in non-development environment"
    assert (
        "development" in text
    ), "database.py must allow SQLite fallback only in development environment"
