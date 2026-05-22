from pathlib import Path
import os
import sys

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.settings import settings

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    _env = getattr(settings, "environment", "development")
    if _env == "development":
        # Dev-only fallback — safe for local schema creation and unit tests
        backend_db_path = Path(__file__).resolve().parent / "ems.db"
        DATABASE_URL = f"sqlite:///{backend_db_path.as_posix()}"
        print(
            "WARNING: DATABASE_URL not set — SQLite fallback enabled (development only). "
            "Set DATABASE_URL to a PostgreSQL connection string for pilot or production.",
            file=sys.stderr,
        )
    else:
        raise RuntimeError(
            "FATAL: DATABASE_URL is set to an empty value. "
            "SQLite fallback is not permitted in environment '%s'. "
            "Set DATABASE_URL to a PostgreSQL connection string and restart." % _env
        )

is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "connect_args": {"check_same_thread": False} if is_sqlite else {},
}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
