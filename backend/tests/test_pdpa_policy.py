"""
Tests for centralized PDPA policy helpers.

Pure-function only; no DB required.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPdpaPolicy:
    def test_student_id_policy_is_sensitive_and_masked(self):
        from policies.pdpa_policy import DataSensitivity, get_field_policy

        policy = get_field_policy("student_id")
        assert policy.sensitivity == DataSensitivity.sensitive
        assert policy.mask_in_logs is True
        assert policy.owner_access_allowed is True

    def test_unknown_fields_default_to_conservative_policy(self):
        from policies.pdpa_policy import DataSensitivity, get_field_policy

        policy = get_field_policy("unmapped_field")
        assert policy.sensitivity == DataSensitivity.role_restricted
        assert policy.mask_in_logs is True

    def test_can_view_student_personal_data_owner(self):
        from policies.pdpa_policy import can_view_student_personal_data

        assert can_view_student_personal_data("student", is_owner=True) is True
        assert can_view_student_personal_data("teacher", is_owner=False) is False

    def test_can_export_sensitive_schedule_data(self):
        from policies.pdpa_policy import can_export_sensitive_schedule_data

        assert can_export_sensitive_schedule_data("admin") is True
        assert can_export_sensitive_schedule_data("staff") is False

    def test_mask_student_id(self):
        from policies.pdpa_policy import mask_student_id

        assert mask_student_id("6500123456") == "******3456"
        assert mask_student_id("1234") == "****"

    def test_redact_for_audit(self):
        from policies.pdpa_policy import redact_for_audit

        assert redact_for_audit("qr_token", "EMS-PICKUP:abc") == "[REDACTED_QR_TOKEN]"
        assert redact_for_audit("student_name", "Alice Example") == "[REDACTED_NAME]"
        assert redact_for_audit("teacher_name", "Dr. Smith") == "Dr. Smith"
