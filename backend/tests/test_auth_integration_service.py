"""
Tests for additive Laravel-style auth integration scaffolding.

Pure-function only; no DB required.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestAuthIntegrationService:
    def test_supports_callback_path_variants(self):
        from services.auth_integration_service import supports_callback_path

        assert supports_callback_path("/callback/authen") is True
        assert supports_callback_path("/api/auth/callback/authen") is True
        assert supports_callback_path("callback/authen") is True
        assert supports_callback_path("/auth/login") is False

    def test_normalize_external_identity_maps_common_fields(self):
        from services.auth_integration_service import normalize_external_identity

        identity = normalize_external_identity(
            {
                "provider": "laravel_gateway",
                "sub": "cmu:123",
                "cmuitaccount": "ems.user",
                "mail": "ems.user@example.edu",
                "display_name": "EMS User",
                "employee_id": "9001",
                "faculty_code": "SCI",
                "department_code": "GOV",
            }
        )

        assert identity.provider == "laravel_gateway"
        assert identity.subject == "cmu:123"
        assert identity.username == "ems.user"
        assert identity.email == "ems.user@example.edu"
        assert identity.full_name == "EMS User"
        assert identity.employee_id == "9001"
        assert identity.faculty_code == "SCI"
        assert identity.department_code == "GOV"

    def test_normalize_external_identity_requires_identifier(self):
        from services.auth_integration_service import normalize_external_identity

        with pytest.raises(ValueError):
            normalize_external_identity({"provider": "faculty_it", "name": "No Id"})

    def test_build_identity_lookup_candidates_preserves_priority(self):
        from services.auth_integration_service import (
            ExternalIdentity,
            build_identity_lookup_candidates,
        )

        identity = ExternalIdentity(
            provider="faculty_it",
            username="alpha",
            email="alpha@example.edu",
            employee_id="1001",
            student_id="6500001234",
            subject="upstream-1",
        )

        assert build_identity_lookup_candidates(identity) == [
            ("username", "alpha"),
            ("email", "alpha@example.edu"),
            ("employee_id", "1001"),
            ("student_id", "6500001234"),
            ("subject", "upstream-1"),
        ]

    def test_build_session_audit_metadata_omits_empty_fields(self):
        from services.auth_integration_service import (
            ExternalIdentity,
            build_session_audit_metadata,
        )

        metadata = build_session_audit_metadata(
            ExternalIdentity(provider="faculty_it", username="alpha"),
            channel="callback_authen",
        )

        assert metadata == {
            "auth_source": "faculty_it",
            "auth_channel": "callback_authen",
            "username": "alpha",
        }


class TestRepositoryHelpers:
    def test_normalize_lookup_value(self):
        from repositories.user_repository import normalize_lookup_value

        assert normalize_lookup_value("  admin  ") == "admin"
        assert normalize_lookup_value("   ") is None
        assert normalize_lookup_value(None) is None

    def test_normalize_employee_id(self):
        from repositories.user_repository import normalize_employee_id

        assert normalize_employee_id(" 42 ") == 42
        assert normalize_employee_id("ABC") is None
        assert normalize_employee_id(None) is None

    def test_normalize_student_id(self):
        from repositories.student_repository import normalize_student_id

        assert normalize_student_id(" 6500001234 ") == "6500001234"
        assert normalize_student_id("") is None
        assert normalize_student_id(None) is None
