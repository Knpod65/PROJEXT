"""
Data Retention Policy Configuration
ตั้งค่านโยบายการเก็บรักษาข้อมูล PDPA
"""

from datetime import timedelta
from typing import Dict

# ─── Retention Periods ────────────────────────────────────────
# Define how long to retain each data type after the exam period ends

RETENTION_POLICY: Dict[str, Dict] = {
    # Student enrollment & schedule data
    "student_schedules": {
        "description": "นักศึกษา enrollments, exam schedules, attendance",
        "retention_days": 365,  # 1 year per PDPA + institutional record
        "event": "exam_period_end",  # Trigger: end of exam period
        "notes": "Required by regulatory compliance + institutional archive",
    },

    # QR check-in logs
    "qr_check_in_logs": {
        "description": "QR token scans, paper pickup logs, exam check-ins",
        "retention_days": 365,  # 1 year
        "event": "exam_period_end",
        "table": "exam_pickup_checkins",
        "notes": "Support incident investigation, audit trail",
    },

    # Audit logs
    "audit_logs": {
        "description": "User actions, data access, system changes",
        "retention_days": 730,  # 2 years per PDPA requirement
        "event": "log_date",  # Trigger: log timestamp
        "table": "audit_logs",
        "notes": "Compliance with data protection, incident forensics",
    },

    # Revoked tokens (JWT blacklist)
    "revoked_tokens": {
        "description": "Logged-out JWT tokens",
        "retention_days": 1,  # 1 day (short-lived, no regulatory need)
        "event": "created_at",
        "table": "revoked_tokens",
        "notes": "Token lifetime is 12 hours; can delete after expiry",
    },

    # Exam submission versions (history)
    "exam_submission_versions": {
        "description": "Version history of exam submissions",
        "retention_days": 730,  # 2 years (part of exam record audit trail)
        "event": "exam_period_end",
        "table": "exam_submission_versions",
        "notes": "Maintains change history for transparency/dispute resolution",
    },

    # Access logs (exam file downloads, prints)
    "exam_access_logs": {
        "description": "Who accessed/printed/downloaded exam files",
        "retention_days": 730,  # 2 years
        "event": "timestamp",
        "table": "exam_access_logs",
        "notes": "Security audit trail for exam file access",
    },

    # Swap request history
    "swap_requests": {
        "description": "Staff invigilator swap requests & history",
        "retention_days": 180,  # 6 months (operational use only)
        "event": "exam_period_end",
        "table": "swap_requests",
        "notes": "Operational record, limited sensitivity",
    },

    # Historical schedule snapshots
    "historical_schedules": {
        "description": "Snapshot of optimization baseline vs final results",
        "retention_days": None,  # PERMANENT (institutional record)
        "event": "never",
        "table": "historical_schedules",
        "notes": "Permanent institutional record of exam planning process",
    },

    # Import session records
    "import_sessions": {
        "description": "Data import history (enrollments, courses)",
        "retention_days": 365,  # 1 year
        "event": "exam_period_end",
        "table": "import_sessions",
        "notes": "Audit trail for data imports",
    },
}

# ─── Retention Configuration ───────────────────────────────────

# Default retention policy if not explicitly set
DEFAULT_RETENTION_DAYS = 365  # 1 year

# Enable/disable automatic cleanup (cron jobs)
RETENTION_CLEANUP_ENABLED = False  # Will be True in production after testing

# Cleanup job schedule (cron-like, used with APScheduler)
CLEANUP_JOB_CONFIG = {
    "trigger": "cron",
    "hour": 2,  # 2 AM local time
    "minute": 0,
    "day_of_week": 0,  # Sunday
    "timezone": "Asia/Bangkok",
}

# Excluded tables (should never be auto-deleted)
AUTO_DELETE_EXCLUDED_TABLES = {
    "historical_schedules",  # Permanent institutional record
    "import_sessions",  # Keep for audit
    "courses",  # Master data
    "users",  # Master data
    "rooms",  # Master data
}

# ─── Helper Functions ─────────────────────────────────────────


def get_retention_days(data_type: str) -> int | None:
    """Get retention period in days for a data type.
    Returns None for permanent retention."""
    policy = RETENTION_POLICY.get(data_type, {})
    return policy.get("retention_days", DEFAULT_RETENTION_DAYS)


def should_be_deleted(data_type: str, days_since_event: int) -> bool:
    """Check if data should be deleted based on retention policy."""
    retention_days = get_retention_days(data_type)
    if retention_days is None:
        return False  # Permanent retention
    return days_since_event >= retention_days


def get_cleanup_query_sql(table_name: str, date_column: str, days: int) -> str:
    """Generate SQL to identify records older than retention period.

    Args:
        table_name: Table to clean
        date_column: Column with date/timestamp
        days: Retention period in days

    Returns:
        SQL WHERE clause
    """
    return f"{date_column} < NOW() - INTERVAL '{days} days'"


# ─── Future: APScheduler Configuration ───────────────────────

# This will be used for automatic cleanup jobs in production
CLEANUP_JOBS = {
    "cleanup_qr_logs": {
        "table": "exam_pickup_checkins",
        "date_column": "timestamp",
        "retention_days": RETENTION_POLICY["qr_check_in_logs"]["retention_days"],
    },
    "cleanup_old_tokens": {
        "table": "revoked_tokens",
        "date_column": "created_at",
        "retention_days": RETENTION_POLICY["revoked_tokens"]["retention_days"],
    },
    "cleanup_audit_logs": {
        "table": "audit_logs",
        "date_column": "timestamp",
        "retention_days": RETENTION_POLICY["audit_logs"]["retention_days"],
    },
}


# ─── Dry-run Report ───────────────────────────────────────────

def generate_dry_run_report(db) -> dict:
    """Return row counts that WOULD be deleted under the current retention policy.

    Read-only — never deletes anything.
    Tables in AUTO_DELETE_EXCLUDED_TABLES are always reported as 0 (protected).
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import text

    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cleanup_enabled": RETENTION_CLEANUP_ENABLED,
        "tables": {},
    }

    jobs = [
        {"key": "qr_check_in_logs",      "table": "exam_pickup_checkins", "date_col": "timestamp"},
        {"key": "audit_logs",             "table": "audit_logs",           "date_col": "timestamp"},
        {"key": "exam_access_logs",       "table": "exam_access_logs",     "date_col": "created_at"},
        {"key": "exam_submission_versions","table": "exam_submission_versions","date_col": "created_at"},
        {"key": "revoked_tokens",         "table": "revoked_tokens",        "date_col": "created_at"},
        {"key": "swap_requests",          "table": "swap_requests",         "date_col": "created_at"},
        {"key": "import_sessions",        "table": "import_sessions",       "date_col": "created_at"},
    ]

    for job in jobs:
        table = job["table"]
        if table in AUTO_DELETE_EXCLUDED_TABLES:
            report["tables"][table] = {"protected": True, "would_delete": 0}
            continue

        days = get_retention_days(job["key"])
        if days is None:
            report["tables"][table] = {"permanent": True, "would_delete": 0}
            continue

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        try:
            result = db.execute(
                text(f"SELECT COUNT(*) FROM {table} WHERE {job['date_col']} < :cutoff"),
                {"cutoff": cutoff},
            ).scalar()
            report["tables"][table] = {
                "retention_days": days,
                "cutoff_date": cutoff.date().isoformat(),
                "would_delete": int(result or 0),
            }
        except Exception as exc:
            report["tables"][table] = {"error": str(exc), "would_delete": -1}

    return report
