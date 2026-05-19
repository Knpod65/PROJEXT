"""TypedDict payload contracts for cross-system integration.

Pure logic. No DB. No ORM. Input is pre-loaded dicts.
"""
from __future__ import annotations

from typing import List
from typing_extensions import TypedDict


class IntegrationContract(TypedDict):
    system_code: str          # e.g. "sis", "hr", "lms", "finance", "cmu_sso", "docmgr"
    system_name: str
    integration_direction: str  # inbound | outbound | bidirectional
    data_domain: str          # student_registration | personnel | teaching_schedule | payment | auth
    auth_method: str          # jwt_bearer | api_key | oauth2 | certificate
    sync_mode: str            # realtime | batch_hourly | batch_daily | batch_weekly | manual
    pdpa_level: str           # public | internal | confidential | restricted
    owner_unit: str           # e.g. "Registrar", "HR", "IT Services"
    required_fields: List[str]
    optional_fields: List[str]
    refresh_frequency: str    # duration string, e.g. "24h"
    failure_policy: str       # retry_3 | dead_letter | alert_only | skip


# Five contracts registered per D4.8 specification:
INTEGRATION_CONTRACTS: List[IntegrationContract] = [
    {
        "system_code": "sis",
        "system_name": "Student Information System",
        "integration_direction": "inbound",
        "data_domain": "student_registration",
        "auth_method": "api_key",
        "sync_mode": "batch_daily",
        "pdpa_level": "confidential",
        "owner_unit": "Registrar",
        "required_fields": ["student_id", "full_name", "department"],
        "optional_fields": ["dept_code", "major", "academic_year"],
        "refresh_frequency": "24h",
        "failure_policy": "retry_3",
    },
    {
        "system_code": "hr",
        "system_name": "Human Resources / Personnel System",
        "integration_direction": "inbound",
        "data_domain": "personnel",
        "auth_method": "api_key",
        "sync_mode": "batch_hourly",
        "pdpa_level": "confidential",
        "owner_unit": "HR",
        "required_fields": ["employee_id", "full_name", "department", "dept_code"],
        "optional_fields": ["position", "hire_date", "supervisor_id"],
        "refresh_frequency": "1h",
        "failure_policy": "dead_letter",
    },
    {
        "system_code": "lms",
        "system_name": "Learning Management System / Teaching Schedule",
        "integration_direction": "bidirectional",
        "data_domain": "teaching_schedule",
        "auth_method": "oauth2",
        "sync_mode": "batch_daily",
        "pdpa_level": "internal",
        "owner_unit": "Academic Affairs",
        "required_fields": ["course_id", "section_id", "meeting_time", "room_id"],
        "optional_fields": ["instructor_id", "title", "credits"],
        "refresh_frequency": "24h",
        "failure_policy": "retry_3",
    },
    {
        "system_code": "finance",
        "system_name": "Finance / Workload Compensation System",
        "integration_direction": "outbound",
        "data_domain": "payment",
        "auth_method": "jwt_bearer",
        "sync_mode": "batch_monthly",
        "pdpa_level": "internal",
        "owner_unit": "Finance Office",
        "required_fields": ["workload_units", "rate", "total_cost"],
        "optional_fields": ["payment_date", "invoice_number"],
        "refresh_frequency": "30d",
        "failure_policy": "alert_only",
    },
    {
        "system_code": "cmu_sso",
        "system_name": "CMU Single Sign-On",
        "integration_direction": "inbound",
        "data_domain": "auth",
        "auth_method": "jwt_bearer",
        "sync_mode": "realtime",
        "pdpa_level": "public",
        "owner_unit": "IT Services",
        "required_fields": ["netid", "roles", "groups"],
        "optional_fields": ["employee_id", "student_id"],
        "refresh_frequency": "0s",  # realtime
        "failure_policy": "skip",  # already wired in cmu_sso.py
    },
]
