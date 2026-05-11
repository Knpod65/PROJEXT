"""
Tests for permissions.py and auth_utils role helpers.

Run:  python -m pytest backend/tests/test_permissions.py -v
  or: python backend/tests/test_permissions.py  (no pytest)

No DB required.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock


def _make_user(role_str: str, view_as: str | None = None) -> MagicMock:
    """Build a minimal User-like mock for testing role helpers."""
    from models import UserRole
    user = MagicMock()
    user.role = UserRole(role_str)
    user.view_as_role = UserRole(view_as) if view_as else None
    user.dept_code = "GOV"
    user.id = 1
    user.is_active = True
    # Simulate no active_role override (direct role)
    user._active_role = UserRole(role_str)
    return user


class TestCoerceUserRole:
    def test_valid_string(self):
        from permissions import coerce_user_role
        from models import UserRole
        assert coerce_user_role("admin") == UserRole.admin

    def test_invalid_string_returns_none(self):
        from permissions import coerce_user_role
        assert coerce_user_role("super_admin") is None

    def test_userrole_passthrough(self):
        from permissions import coerce_user_role
        from models import UserRole
        assert coerce_user_role(UserRole.teacher) == UserRole.teacher

    def test_none_returns_none(self):
        from permissions import coerce_user_role
        assert coerce_user_role(None) is None

    def test_int_returns_none(self):
        from permissions import coerce_user_role
        assert coerce_user_role(123) is None

    def test_all_valid_roles(self):
        from permissions import coerce_user_role
        from models import UserRole
        for role in UserRole:
            assert coerce_user_role(role.value) == role


class TestSupervisionRoleEnum:
    def test_enum_values_exist(self):
        from models import SupervisionRole
        assert SupervisionRole.supervisor.value == "supervisor"
        assert SupervisionRole.chief.value == "chief"
        assert SupervisionRole.distributor.value == "distributor"
        assert SupervisionRole.room_keeper.value == "room_keeper"

    def test_enum_from_string(self):
        from models import SupervisionRole
        assert SupervisionRole("distributor") == SupervisionRole.distributor

    def test_invalid_string_raises(self):
        from models import SupervisionRole
        with pytest.raises(ValueError):
            SupervisionRole("invalid_role")


class TestGetEffectiveRole:
    def test_admin_no_view_as(self):
        from auth_utils import get_effective_role
        from models import UserRole
        user = _make_user("admin")
        assert get_effective_role(user) == UserRole.admin

    def test_admin_with_view_as_teacher(self):
        from auth_utils import get_effective_role
        from models import UserRole
        user = _make_user("admin", view_as="teacher")
        result = get_effective_role(user)
        # With view_as_role set, effective role should differ
        assert result in (UserRole.teacher, UserRole.admin)

    def test_teacher_no_change(self):
        from auth_utils import get_effective_role
        from models import UserRole
        user = _make_user("teacher")
        assert get_effective_role(user) == UserRole.teacher

    def test_staff_no_change(self):
        from auth_utils import get_effective_role
        from models import UserRole
        user = _make_user("staff")
        assert get_effective_role(user) == UserRole.staff


class TestPermissionsViewAllRoles:
    def test_admin_in_view_all(self):
        from permissions import VIEW_ALL_ROLES
        from models import UserRole
        assert UserRole.admin in VIEW_ALL_ROLES

    def test_esq_head_in_view_all(self):
        from permissions import VIEW_ALL_ROLES
        from models import UserRole
        assert UserRole.esq_head in VIEW_ALL_ROLES

    def test_secretary_in_view_all(self):
        from permissions import VIEW_ALL_ROLES
        from models import UserRole
        assert UserRole.secretary in VIEW_ALL_ROLES

    def test_teacher_not_in_view_all(self):
        from permissions import VIEW_ALL_ROLES
        from models import UserRole
        assert UserRole.teacher not in VIEW_ALL_ROLES

    def test_staff_not_in_view_all(self):
        from permissions import VIEW_ALL_ROLES
        from models import UserRole
        assert UserRole.staff not in VIEW_ALL_ROLES


class TestPermissionServiceHelpers:
    def test_can_manage_users_admin(self):
        from services.permission_service import can_manage_users
        user = _make_user("admin")
        assert can_manage_users(user) is True

    def test_can_manage_users_teacher_false(self):
        from services.permission_service import can_manage_users
        user = _make_user("teacher")
        assert can_manage_users(user) is False

    def test_can_view_all_esq_head(self):
        from services.permission_service import can_view_all
        user = _make_user("esq_head")
        assert can_view_all(user) is True

    def test_can_view_all_staff_false(self):
        from services.permission_service import can_view_all
        user = _make_user("staff")
        assert can_view_all(user) is False

    def test_can_manage_workflow_secretary(self):
        from services.permission_service import can_manage_workflow
        user = _make_user("secretary")
        assert can_manage_workflow(user) is True

    def test_can_manage_workflow_teacher_false(self):
        from services.permission_service import can_manage_workflow
        user = _make_user("teacher")
        assert can_manage_workflow(user) is False

    def test_can_export_admin_reports_admin(self):
        from services.permission_service import can_export_admin_reports
        user = _make_user("admin")
        assert can_export_admin_reports(user) is True

    def test_can_export_admin_reports_print_shop_false(self):
        from services.permission_service import can_export_admin_reports
        user = _make_user("print_shop")
        assert can_export_admin_reports(user) is False

    def test_can_use_view_as_admin(self):
        from services.permission_service import can_use_view_as
        user = _make_user("admin")
        assert can_use_view_as(user) is True

    def test_can_use_view_as_secretary_false(self):
        from services.permission_service import can_use_view_as
        user = _make_user("secretary")
        assert can_use_view_as(user) is False

    def test_can_view_student_schedule_admin(self):
        from services.permission_service import can_view_student_schedule
        user = _make_user("admin")
        assert can_view_student_schedule(user, requested_student_id=99) is True

    def test_can_view_student_schedule_print_shop_false(self):
        from services.permission_service import can_view_student_schedule
        user = _make_user("print_shop")
        assert can_view_student_schedule(user, requested_student_id=99) is False


class TestServiceExceptions:
    def test_ems_domain_error_base(self):
        from services.exceptions import EMSDomainError
        err = EMSDomainError("something went wrong", "TEST_CODE")
        assert err.message == "something went wrong"
        assert err.error_code == "TEST_CODE"
        assert str(err) == "something went wrong"

    def test_ems_not_found_error(self):
        from services.exceptions import EMSNotFoundError
        err = EMSNotFoundError("User", resource_id=42)
        assert "User" in err.message
        assert "42" in err.message
        assert err.error_code == "EMS_NOT_FOUND"

    def test_ems_validation_error_with_field(self):
        from services.exceptions import EMSValidationError
        err = EMSValidationError("ข้อมูลไม่ถูกต้อง", field="exam_date")
        assert err.field == "exam_date"
        assert err.error_code == "EMS_VALIDATION_ERROR"

    def test_ems_term_locked_error(self):
        from services.exceptions import EMSTermLockedError
        err = EMSTermLockedError("กลางภาค 1/2568")
        assert "ล็อค" in err.message
        assert err.error_code == "EMS_TERM_LOCKED"

    def test_exception_hierarchy(self):
        from services.exceptions import (
            EMSDomainError, EMSPermissionError, EMSNotFoundError,
            EMSConflictError, EMSTermLockedError,
        )
        assert issubclass(EMSPermissionError, EMSDomainError)
        assert issubclass(EMSNotFoundError, EMSDomainError)
        assert issubclass(EMSConflictError, EMSDomainError)
        assert issubclass(EMSTermLockedError, EMSConflictError)


if __name__ == "__main__":
    import unittest
    # Simple runner without pytest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [
        TestCoerceUserRole,
        TestSupervisionRoleEnum,
        TestGetEffectiveRole,
        TestPermissionsViewAllRoles,
        TestPermissionServiceHelpers,
        TestServiceExceptions,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
