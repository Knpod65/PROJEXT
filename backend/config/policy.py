from __future__ import annotations

import os
from zoneinfo import ZoneInfo


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "12"))
LOGIN_RATE_MAX = int(os.getenv("LOGIN_RATE_MAX", "10"))
LOGIN_RATE_WINDOW = int(os.getenv("LOGIN_RATE_WINDOW", "300"))
ALLOWED_ORIGINS = _csv_env("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")

PRINT_PRIORITY_HIGH_THRESHOLD = int(os.getenv("PRINT_PRIORITY_HIGH_THRESHOLD", "120"))
PRINT_PRIORITY_MEDIUM_THRESHOLD = int(os.getenv("PRINT_PRIORITY_MEDIUM_THRESHOLD", "70"))
PRINT_PRIORITY_NORMAL_THRESHOLD = int(os.getenv("PRINT_PRIORITY_NORMAL_THRESHOLD", "15"))

PICKUP_QR_OPEN_MINUTES_BEFORE = int(os.getenv("PICKUP_QR_OPEN_MINUTES_BEFORE", "120"))
EMS_LOCAL_TIMEZONE = ZoneInfo(os.getenv("EMS_LOCAL_TIMEZONE", "Asia/Bangkok"))
QR_PICKUP_PREFIX = "EMS-PICKUP:"
QR_REGULATION_PREFIX = "EMS-REGULATION:"
PDF_TOKEN_EXPIRE_HOURS = 1

SIGN_ORDER_USERNAMES = ["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]

PAPER_DISTRIBUTION_DIVISION = "Education_Student_Quality"
PAPER_DISTRIBUTION_EXCLUDED_USERNAMES = {"araya.fa", "sapanyu.wong"}
PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS = ("อารยา", "สัพพัญญู")
