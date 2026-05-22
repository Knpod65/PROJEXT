"""Tests for SECRET_KEY enforcement in production vs development."""

import os
import pytest
from config.settings import _get_secret_key


def test_production_missing_secret_key_raises(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        _get_secret_key()


def test_production_short_secret_key_raises(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "shortkey123")

    with pytest.raises(RuntimeError, match="at least 50 characters"):
        _get_secret_key()


def test_production_valid_secret_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    long_key = "a" * 60
    monkeypatch.setenv("SECRET_KEY", long_key)

    assert _get_secret_key() == long_key


def test_development_missing_secret_key_warns_and_falls_back(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.warns(UserWarning, match="insecure development fallback"):
        key = _get_secret_key()

    assert "DO_NOT_USE_IN_PRODUCTION" in key


def test_development_with_secret_key_uses_it(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SECRET_KEY", "my-custom-dev-key-1234567890")

    assert _get_secret_key() == "my-custom-dev-key-1234567890"
