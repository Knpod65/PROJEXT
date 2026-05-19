import pytest
from services.pdpa_runtime_guard_service import (
    validate_analytics_not_exposing_pii,
    validate_export_payload,
    validate_config_for_secrets,
    validate_trace_for_unsafe_fields,
    is_production_environment,
    assert_production_secrets,
    RESTRICTED_FIELDS,
)


class TestPdpaRuntimeGuard:
    def test_analytics_ok_no_restricted(self):
        assert validate_analytics_not_exposing_pii({"score": 85, "count": 10}) is True

    def test_analytics_rejects_student_name(self):
        assert validate_analytics_not_exposing_pii({"score": 85, "student_name": "John"}) is False

    def test_analytics_rejects_gpa(self):
        assert validate_analytics_not_exposing_pii({"gpa": 3.5}) is False

    def test_export_ok(self):
        assert validate_export_payload({"course": "CS101", "exam_date": "2026-01-01"}) is True

    def test_export_rejects_email(self):
        assert validate_export_payload({"email": "test@example.com"}) is False

    def test_config_ok_no_secrets(self):
        assert validate_config_for_secrets({"faculty": "science", "timeout": 30}) is True

    def test_config_rejects_api_key(self):
        assert validate_config_for_secrets({"api_key": "abc123"}) is False

    def test_trace_validation_uses_same_rules(self):
        assert validate_trace_for_unsafe_fields({"score": 50}) is True
        assert validate_trace_for_unsafe_fields({"student_name": "Doe"}) is False