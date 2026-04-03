from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, sys

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    # Dev fallback — warn loudly
    print("⚠  DATABASE_URL not set — using SQLite (dev only)", file=sys.stderr)
    DATABASE_URL = "sqlite:///./ems.db"

is_sqlite = DATABASE_URL.startswith("sqlite")

# Connection pool tuning
engine_kwargs = {
    "connect_args": {"check_same_thread": False} if is_sqlite else {},
}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size":         int(os.getenv("DB_POOL_SIZE",    "10")),
        "max_overflow":      int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout":      int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle":      1800,   # recycle connections ทุก 30 นาที
        "pool_pre_ping":     True,   # ตรวจ connection ก่อนใช้
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")   # better concurrent access
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Database session dependency.
    - commit ต้องทำใน endpoint เอง
    - ถ้าเกิด exception: rollback อัตโนมัติ ป้องกัน partial write
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()   # rollback อัตโนมัติถ้า endpoint raise exception
        raise
    finally:
        db.close()
