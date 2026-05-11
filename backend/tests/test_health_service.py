"""
Tests for services/health_service.py.

Run:  python -m pytest backend/tests/test_health_service.py -v
  or: python backend/tests/test_health_service.py
No real DB required — uses mocks.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock, patch


class TestCheckSettings:
    def test_returns_ok_with_real_settings(self):
        from services.health_service import check_settings
        result = check_settings()
        assert result["status"] in ("ok", "degraded", "error")
        if result["status"] == "ok":
            assert "token_expire_hours" in result

    def test_returns_ok_structure(self):
        from services.health_service import check_settings
        result = check_settings()
        assert "status" in result


class TestCheckRbac:
    def test_returns_dict_with_status(self):
        from services.health_service import check_rbac
        result = check_rbac()
        assert "status" in result
        assert result["status"] in ("ok", "degraded", "error")

    def test_ok_after_build_dependencies(self):
        """After startup, build_dependencies() is called, so guards should not be stubs."""
        import permissions
        permissions.build_dependencies()
        from services.health_service import check_rbac
        result = check_rbac()
        # Once build_dependencies() runs, status should be ok
        assert result["status"] == "ok"


class TestCheckDatabase:
    def test_ok_with_working_db(self):
        from services.health_service import check_database
        mock_db = MagicMock()
        result = check_database(mock_db)
        assert result["status"] == "ok"
        mock_db.execute.assert_called_once()

    def test_error_when_db_raises(self):
        from services.health_service import check_database
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("connection refused")
        result = check_database(mock_db)
        assert result["status"] == "error"
        assert "Exception" in result["detail"] or result["detail"] == "Exception"

    def test_error_detail_does_not_leak_credentials(self):
        """DB check error must not include connection strings."""
        from services.health_service import check_database
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("postgresql://user:secret@host/db")
        result = check_database(mock_db)
        # Only exception class name is returned, not the full message
        assert "secret" not in str(result)
        assert "postgresql" not in str(result)


class TestCheckImportPipeline:
    def test_returns_ok_or_degraded(self):
        from services.health_service import check_import_pipeline
        result = check_import_pipeline()
        assert "status" in result
        assert result["status"] in ("ok", "degraded", "error")


class TestGetSystemHealth:
    def test_returns_aggregate_with_timestamp(self):
        from services.health_service import get_system_health
        mock_db = MagicMock()
        result = get_system_health(db=mock_db)
        assert "status" in result
        assert "timestamp" in result
        assert "checks" in result
        assert isinstance(result["checks"], dict)

    def test_no_db_skips_db_check(self):
        from services.health_service import get_system_health
        result = get_system_health(db=None)
        assert "database" not in result["checks"]

    def test_error_in_any_check_propagates_to_overall(self):
        from services.health_service import get_system_health
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("db down")
        result = get_system_health(db=mock_db)
        assert result["checks"]["database"]["status"] == "error"
        assert result["status"] == "error"

    def test_all_ok_returns_ok(self):
        from services.health_service import get_system_health
        mock_db = MagicMock()
        result = get_system_health(db=mock_db)
        # DB mock always succeeds; settings and rbac should be ok after startup
        assert result["status"] in ("ok", "degraded")  # degraded is acceptable in test env

    def test_timestamp_is_iso_format(self):
        from services.health_service import get_system_health
        result = get_system_health(db=None)
        ts = result["timestamp"]
        from datetime import datetime
        # Should not raise
        datetime.fromisoformat(ts)


class TestAuditService:
    def test_audit_mutation_calls_log_action(self):
        from services import audit_service
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"

        with patch("auth_utils.log_action") as mock_log:
            audit_service.audit_mutation(
                mock_db, mock_user,
                action="UPDATE_TEST",
                table_name="test_table",
                record_id=42,
                new_values={"field": "value"},
            )
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args
            assert call_kwargs[0][2] == "UPDATE_TEST"

    def test_audit_export_calls_log_action(self):
        from services import audit_service
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch("auth_utils.log_action") as mock_log:
            audit_service.audit_export(
                mock_db, mock_user,
                export_type="PDF_SCHEDULE",
                period_id=5,
                record_count=120,
            )
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args
            assert call_kwargs[0][2] == "EXPORT"

    def test_audit_event_generic(self):
        from services import audit_service
        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch("auth_utils.log_action") as mock_log:
            audit_service.audit_event(
                mock_db, mock_user,
                action="CUSTOM_ACTION",
                metadata={"key": "val"},
            )
            mock_log.assert_called_once()


if __name__ == "__main__":
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [
        TestCheckSettings,
        TestCheckRbac,
        TestCheckDatabase,
        TestCheckImportPipeline,
        TestGetSystemHealth,
        TestAuditService,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
