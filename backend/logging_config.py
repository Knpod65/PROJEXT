"""
logging_config.py — Structured JSON logging + Request correlation
"""
import logging, json, time, uuid, hashlib
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """JSON log formatter สำหรับ production"""
    def format(self, record):
        log_obj = {
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "level":      record.levelname,
            "logger":     record.name,
            "message":    record.getMessage(),
        }
        # เพิ่ม extra fields
        for key in ("request_id", "user_id", "action", "duration_ms",
                    "status_code", "path", "method"):
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", json_logs: bool = True):
    """ตั้งค่า logging ทั้งระบบ"""
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

    # ลด noise จาก libraries
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# Request context (thread-local style via contextvars)
from contextvars import ContextVar
_request_id_var: ContextVar[str] = ContextVar("request_id", default="")
_user_id_var:    ContextVar[int] = ContextVar("user_id",    default=0)

def get_request_id() -> str:
    return _request_id_var.get()

def get_request_logger(name: str = "ems") -> logging.Logger:
    logger = logging.getLogger(name)
    # สร้าง adapter ที่แนบ request_id ไปด้วย
    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            kwargs.setdefault("extra", {})
            kwargs["extra"]["request_id"] = get_request_id()
            kwargs["extra"]["user_id"]    = _user_id_var.get()
            return msg, kwargs
    return ContextAdapter(logger, {})

app_log = get_request_logger("ems")
