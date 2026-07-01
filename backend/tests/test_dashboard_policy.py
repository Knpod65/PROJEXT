"""Tests for legacy dashboard access policy."""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
from policies.dashboard_policy import DashboardPolicy


def _user(role):
    return SimpleNamespace(role=role)


def test_dept_supervisor_can_view_legacy_dashboard():
    assert DashboardPolicy.can_view_dashboard(_user(models.UserRole.dept_supervisor)) is True


def test_print_shop_cannot_view_legacy_dashboard():
    assert DashboardPolicy.can_view_dashboard(_user(models.UserRole.print_shop)) is False
