"""
Tests for config/settings.py Settings singleton.

Run:  python -m pytest backend/tests/test_settings.py -v
  or: python backend/tests/test_settings.py
No DB required.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestSettingsSingleton:
    def test_settings_importable(self):
        from config.settings import settings
        assert settings is not None

    def test_get_settings_returns_same_singleton(self):
        from config.settings import settings, get_settings
        assert get_settings() is settings

    def test_required_fields_exist(self):
        from config.settings import settings
        assert hasattr(settings, "token_expire_hours")
        assert hasattr(settings, "login_rate_max")
        assert hasattr(settings, "login_rate_window")
        assert hasattr(settings, "allowed_origins")
        assert hasattr(settings, "print_priority_high_threshold")
        assert hasattr(settings, "print_priority_medium_threshold")
        assert hasattr(settings, "print_priority_normal_threshold")
        assert hasattr(settings, "pdf_token_expire_hours")
        assert hasattr(settings, "printshop_token_expire_hours")
        assert hasattr(settings, "submission_access_token_expire_hours")
        assert hasattr(settings, "workflow_lock_ttl_seconds")

    def test_print_thresholds_are_ordered(self):
        from config.settings import settings
        assert settings.print_priority_high_threshold > settings.print_priority_medium_threshold
        assert settings.print_priority_medium_threshold > settings.print_priority_normal_threshold

    def test_token_expire_hours_positive(self):
        from config.settings import settings
        assert settings.token_expire_hours > 0

    def test_allowed_origins_is_tuple(self):
        from config.settings import settings
        assert isinstance(settings.allowed_origins, tuple)
        assert len(settings.allowed_origins) > 0

    def test_sign_order_usernames_is_tuple(self):
        from config.settings import settings
        assert isinstance(settings.sign_order_usernames, tuple)
        assert len(settings.sign_order_usernames) > 0

    def test_paper_distribution_excluded_is_frozenset(self):
        from config.settings import settings
        assert isinstance(settings.paper_distribution_excluded_usernames, frozenset)

    def test_feature_flags_are_bool(self):
        from config.settings import settings
        assert isinstance(settings.multi_faculty_enabled, bool)
        assert isinstance(settings.retention_cleanup_enabled, bool)

    def test_retention_cleanup_disabled_by_default(self):
        """Retention must stay disabled until admin sign-off."""
        from config.settings import settings
        # In dev/test environment without env override this must be False
        if os.getenv("RETENTION_CLEANUP_ENABLED", "false").lower() != "true":
            assert settings.retention_cleanup_enabled is False

    def test_settings_is_frozen(self):
        """Settings dataclass must be immutable."""
        from config.settings import settings
        with pytest.raises((AttributeError, TypeError)):
            settings.token_expire_hours = 9999  # type: ignore[misc]

    def test_qr_prefixes_are_strings(self):
        from config.settings import settings
        assert isinstance(settings.qr_pickup_prefix, str)
        assert isinstance(settings.qr_regulation_prefix, str)
        assert settings.qr_pickup_prefix.startswith("EMS-")
        assert settings.qr_regulation_prefix.startswith("EMS-")

    def test_token_and_lock_windows_are_positive(self):
        from config.settings import settings
        assert settings.pdf_token_expire_hours > 0
        assert settings.printshop_token_expire_hours > 0
        assert settings.submission_access_token_expire_hours > 0
        assert settings.workflow_lock_ttl_seconds > 0


class TestPolicyReExports:
    """config/policy.py must re-export the same values from settings."""

    def test_sign_order_usernames_consistent(self):
        from config.policy import SIGN_ORDER_USERNAMES
        from config.settings import settings
        assert tuple(SIGN_ORDER_USERNAMES) == settings.sign_order_usernames

    def test_token_expire_hours_consistent(self):
        from config.policy import TOKEN_EXPIRE_HOURS
        from config.settings import settings
        assert TOKEN_EXPIRE_HOURS == settings.token_expire_hours

    def test_login_rate_max_consistent(self):
        from config.policy import LOGIN_RATE_MAX
        from config.settings import settings
        assert LOGIN_RATE_MAX == settings.login_rate_max

    def test_printshop_token_expire_hours_consistent(self):
        from config.policy import PRINTSHOP_TOKEN_EXPIRE_HOURS
        from config.settings import settings
        assert PRINTSHOP_TOKEN_EXPIRE_HOURS == settings.printshop_token_expire_hours

    def test_submission_access_token_expire_hours_consistent(self):
        from config.policy import SUBMISSION_ACCESS_TOKEN_EXPIRE_HOURS
        from config.settings import settings
        assert SUBMISSION_ACCESS_TOKEN_EXPIRE_HOURS == settings.submission_access_token_expire_hours

    def test_workflow_lock_ttl_consistent(self):
        from config.policy import WORKFLOW_LOCK_TTL_SECONDS
        from config.settings import settings
        assert WORKFLOW_LOCK_TTL_SECONDS == settings.workflow_lock_ttl_seconds


if __name__ == "__main__":
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestSettingsSingleton, TestPolicyReExports]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
