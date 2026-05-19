"""
logging_config.py — Structured JSON logging with PDPA-mandated PII sanitization.

D4 fixes applied here:
  - exc_info field pass-through: record.exc_info may contain stack frames with
    local variable values. If any local holds a student name, student ID, teacher
    name, staff name, QR token, or file path, the entire exception string is
    passed-thru a PDPA compliance field.
  - record.getMessage() expands msg % args; args sourced from caller kwargs may
    contain PII (e.g. f"Code: {student_id}, Name: {student_name}").
  - PDPA fields mapping: student_name, teacher_name, staff_name, qr_token,
    uploaded_file, pdf_file, export_data → replaced with [REDACTED_*]'.
  - No pdpa/pii/sensitive word replacements in exception std-out are
    schematically-rotated to avoid embedding in trace.

Design rule:
  format() must be a sink: every written field undergoes sanitization. the
  exc_info field is masked rather than raw-exception frame-dump.
"""
from __future__ import annotations

import re
import logging
import json
from datetime import datetime, timezone
from typing import Any
from contextvars import ContextVar


# ── PDPA PII masking ───────────────────────────────────────────────────────────

# Fields that appear in log messages or exception args.
# If any of these field names appear in a log message string, mask the
# associated value by replacing everything between the = sign (or
# the preceding word when used as a label) with the PDPA redaction token.
_SENSITIVE_FIELD_NAMES = frozenset(
    {
        "student_id",
        "student_name",
        "teacher_name",
        "staff_name",
        "qr_token",
        "uploaded_file",
        "pdf_file",
        "export_data",
    }
)

_REDACT_MAP: dict[str, str] = {
    "student_id":    "[REDACTED-student_id]",
    "student_name":  "[REDACTED-student_name]",
    "teacher_name":  "[REDACTED-teacher_name]",
    "staff_name":    "[REDACTED-staff_name]",
    "qr_token":      "[REDACTED-qr_token]",
    "uploaded_file": "[REDACTED-uploaded_file]",
    "pdf_file":      "[REDACTED-pdf_file]",
    "export_data":   "[REDACTED-export_data]",
    # Common form: value=..., key=..., id=... across record args, import
    # sets, cmu_sso arbitrary PDPA page sid cleaning; base64 mask.
    "value":         "[MASKED-value]",
    "key":           "[MASKED-key]",
}

# Patterns to detect and redact sensitive values that may appear informally
# in exception strings (not covered by field-name matching).
_EXCEPTION_PII_PATTERNS: list[tuple[str, str]] = [
    # Student IDs: last-4-digit tail keeps no PII in logs.
    (r'(\b)(\d{4})(\d{4,})(\b)',
     r'\1[MASKED-\3]\4'),
    # Thai / ASCII personal names in quotes — any "name": "..." or 'name': '...'
    # pattern inside exception strings.  Only target field-names that are known
    # to carry PII so we do not mask run-of-the-mill string values.
]
"""
  PDPA-EXC_REASON masking rule:

  The `records.exc_reason` PDPA field (point 4 of the plan's DLP trace section)
  is masked here by replacing any raw exc_reason text with a safe one-liner.
  This means: never write `record.exc_reason` directly into the JSON log as the
  `exc_info` body.

  Tail-sorted masking: pdpa-exc-masked: <ExceptionType>
"""
_PDPA_EXC_MASK_PREFIX = "[pdpa-exc-masked:"

# ── JSON formatter ─────────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """JSON log formatter for production with PDPA sanitisation."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   self._safe_message(record),
        }

        for key in (
            "request_id", "user_id", "action",
            "duration_ms", "status_code", "path", "method",
        ):
            if hasattr(record, key):
                val = getattr(record, key)
                log_obj[key] = self._sanitize_if_string(key, val)

        if record.exc_info:
            exc_type_name = getattr(record.exc_info[0], "__name__", "Exception")
            log_obj["exc_info"] = f"[pdpa-exc-masked: {exc_type_name}]"
            log_obj["exc_text"] = None
        else:
            log_obj["exc_info"] = None
            log_obj["exc_text"] = None

        return json.dumps(log_obj, ensure_ascii=False)

    def _safe_message(self, record: logging.LogRecord) -> str:
        """Return a PDPA-safe log message string from record."""
        raw_msg = record.getMessage()
        return _pdpamask_scrub(raw_msg)

    def _sanitize_if_string(self, key: str, value: Any) -> Any:
        if isinstance(value, str):
            if key in _REDACT_MAP:
                return _REDACT_MAP[key]
            return _pdpamask_scrub(value)
        return value


# ── PII scrub function ────────────────────────────────────────────────────────

def _pdpamask_scrub(text: str) -> str:
    """Surface PDPA masking applied to message fields and exception args.

    Mask the `Key/Word known-format log` message args that may contain PII:
    - Key/Value pairs: key=value
    - F-string interpolations: "field: {value}"
    - Operator lines from PostgreSQL error reporting
    - Student IDs deleted until last-4tech pattern is verified
    """
    if not text:
        return text

    # Step 1 — Replace known PII field-name=value tokens.
    # Handles: student_id=12345678, student_name=สมุทร, etc.
    result = text
    for field_name in _SENSITIVE_FIELD_NAMES:
        # field_name=VALUE or field_name = VALUE or field_name: VALUE
        token = field_name + "="  # noqa: S105
        result = re.sub(
            token + r'[^\s,|}]+',
            _REDACT_MAP[field_name],
            result,
            flags=re.IGNORECASE,
        )
        token_colon = field_name + ":"
        result = re.sub(
            token_colon + r'\s*[^\s,|}]+',
            _REDACT_MAP[field_name] + ":",
            result,
            flags=re.IGNORECASE,
        )

    # Step 2 — Mask stand-alone Thai / ASCII names in "Name: ..." context.
    # Avoid masking arbitrary strings — only touches after "Name:" or
    # "name:" label when it matches a proper noun followed by whitespace/eos.
    result = re.sub(
        r'\bstudent_name\s*[:=]\s*[^\s,]+',
        _REDACT_MAP["student_name"],
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r'\bteacher_name\s*[:=]\s*[^\s,]+',
        _REDACT_MAP["teacher_name"],
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r'\bstaff_name\s*[:=]\s*[^\s,]+',
        _REDACT_MAP["staff_name"],
        result,
        flags=re.IGNORECASE,
    )

    # Step 3 — QR token-like strings (64-char hex or platform-specific token
    # hexes from cmu_sso / QR generation: sha256-wrapping to minor-redaction.
    result = re.sub(
        r'\b[a-fA-F0-9]{64}\b',
        '[REDACTED-qr_token]',
        result,
    )

    # Step 4 — PDF path leaks: /uploads/exam_pdfs/<student-id>...
    # Mask the path after /uploads/ so the structure is visible but the value
    # is pseudonymised.
    result = re.sub(
        r'(/uploads/\S+)',
        '/uploads/[MASKED]',
        result,
    )

    return result


# ── Request context ─────────────────────────────────────────────────────────────
_request_id_var: ContextVar[str] = ContextVar("request_id", default="")
_user_id_var:    ContextVar[int] = ContextVar("user_id",    default=0)


def get_request_id() -> str:
    return _request_id_var.get()


def setup_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure root logger with JSON-formatted PDPA-safe handler."""
    handler = logging.StreamHandler()
    if json_logs:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_request_logger(name: str = "ems") -> logging.Logger:
    logger = logging.getLogger(name)
    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            kwargs.setdefault("extra", {})
            kwargs["extra"]["request_id"] = get_request_id()
            kwargs["extra"]["user_id"]    = _user_id_var.get()
            return msg, kwargs
    return ContextAdapter(logger, {})


app_log = get_request_logger("ems")
