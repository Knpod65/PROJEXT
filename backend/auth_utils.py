"""
Auth utilities
- Password hashing (bcrypt)
- JWT token (HS256)
- Admin "view-as" impersonation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models, os, hashlib

_raw_secret = os.getenv("SECRET_KEY", "")
if not _raw_secret:
    import sys
    # Dev mode: warn แต่ไม่ crash (production ต้องตั้ง SECRET_KEY)
    _dev_secret = "ems_dev_only_DO_NOT_USE_IN_PRODUCTION_2025_change_me"
    print("⚠  WARNING: SECRET_KEY not set — using insecure dev default. Set SECRET_KEY env var in production!", file=sys.stderr)
    SECRET_KEY = _dev_secret
else:
    SECRET_KEY = _raw_secret

ALGORITHM          = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "12"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# Used to normalize login timing when the username does not exist.
DUMMY_PASSWORD_HASH = hash_password("ems_dummy_password")

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def revoke_token(token: str, db: Session) -> None:
    """เพิ่ม token เข้า blacklist"""
    th = _token_hash(token)
    existing = db.query(models.RevokedToken).filter(
        models.RevokedToken.token_hash == th
    ).first()
    if not existing:
        db.add(models.RevokedToken(token_hash=th))
        db.commit()


def is_token_revoked(token: str, db: Session) -> bool:
    th = _token_hash(token)
    return db.query(models.RevokedToken).filter(
        models.RevokedToken.token_hash == th
    ).first() is not None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ไม่ถูกต้องหรือหมดอายุ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    # ตรวจ blacklist
    if is_token_revoked(token, db):
        raise credentials_exc

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise credentials_exc
    return user


def get_effective_role(user: models.User) -> models.UserRole:
    """role ที่ใช้งานจริง — ถ้า admin impersonate ใช้ view_as_role"""
    if user.role == models.UserRole.admin and user.view_as_role:
        return user.view_as_role
    return user.role


def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ admin")
    return user

def require_staff_or_admin(user: models.User = Depends(get_current_user)):
    if user.role not in (models.UserRole.admin, models.UserRole.staff):
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ staff หรือ admin")
    return user



# ── Role helpers ─────────────────────────────────────────────

def is_view_all_role(user: "models.User") -> bool:
    """esq_head + secretary เห็นทุกอย่าง แต่ edit ไม่ได้"""
    return user.role in (models.UserRole.esq_head, models.UserRole.secretary)

def is_signer(user: "models.User") -> bool:
    """admin + esq_head + secretary ลงนามได้"""
    return user.role in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    )

def require_view_all(user: "models.User" = Depends(get_current_user)):
    """เฉพาะ admin / esq_head / secretary"""
    if user.role not in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "ต้องการสิทธิ์ระดับ admin หรือผู้มีอำนาจอนุมัติ")
    return user

def require_dept_or_admin(user: "models.User" = Depends(get_current_user)):
    """admin / dept_supervisor / esq_head / secretary"""
    if user.role not in (
        models.UserRole.admin,
        models.UserRole.dept_supervisor,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "ต้องการสิทธิ์ระดับแผนกหรือสูงกว่า")
    return user

def get_dept_filter(user: "models.User"):
    """
    คืน dept_code ที่ user เห็นได้:
    - admin / esq_head / secretary → None (เห็นทุก dept)
    - dept_supervisor              → dept_code ตัวเอง
    - teacher                      → dept_code ตัวเอง
    - staff                        → None (เห็นเฉพาะ schedule)
    """
    if user.role in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        return None   # ไม่ filter
    if user.role in (models.UserRole.dept_supervisor, models.UserRole.teacher):
        return user.dept_code
    return None



def require_read_only(user: "models.User" = Depends(get_current_user)):
    """
    esq_head + secretary อ่านได้อย่างเดียว
    ใช้ใน endpoints ที่ต้องการ block การแก้ไข
    """
    if user.role in (models.UserRole.esq_head, models.UserRole.secretary):
        raise HTTPException(403,
            "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว — ไม่สามารถแก้ไขได้")
    return user


def require_can_edit(user: "models.User" = Depends(get_current_user)):
    """
    แก้ไขได้: admin + teacher + dept_supervisor
    ไม่ได้: esq_head, secretary (read-only), staff (ไม่มี edit rights)
    """
    if user.role in (models.UserRole.esq_head, models.UserRole.secretary):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    if user.role not in (
        models.UserRole.admin,
        models.UserRole.teacher,
        models.UserRole.dept_supervisor,
    ):
        raise HTTPException(403, "ไม่มีสิทธิ์แก้ไข")
    return user


def is_eligible_supervisor(user: "models.User") -> bool:
    """
    staff ที่คุมสอบได้:
      - role = staff
      - ไม่ใช่หัวหน้างาน (_HEAD / "(หัวหน้างาน)")
      - ไม่ใช่เลขาคณะ (Faculty_Secretary)
      - ไม่ใช่ room_keeper (ธีราภัณฑ์ + ชนะชล — เปิด/ปิดห้อง)
    """
    if user.role != models.UserRole.staff:
        return False
    if user.division == "Faculty_Secretary":
        return False
    if user.unit and user.unit.upper().endswith("_HEAD"):
        return False
    if user.full_name and "(หัวหน้างาน)" in user.full_name:
        return False
    # room_keeper ไม่คุม ไม่กระจาย
    if getattr(user, "special_role", None) == "room_keeper":
        return False
    return True


def is_eligible_distributor(user: "models.User") -> bool:
    """
    staff ที่กระจายข้อสอบได้:
    - supervisor ปกติทุกคน
    - room_keeper (ธีราภัณฑ์+ชนะชล) — ถูก assign เป็น distributor slot สุดท้าย
      หน้าที่จริงคือเปิด/ปิดห้อง แต่ให้นับเป็น distributor เพื่อ stat
    - ไม่รวม: หัวหน้างาน, เลขา, esq_head (นภาภรณ์)
    """
    if getattr(user, "special_role", None) == "room_keeper":
        return True   # room_keeper = distributor slot สุดท้าย
    return is_eligible_supervisor(user)


def show_in_fairness_stat(user: "models.User") -> bool:
    """
    แสดงใน fairness stat แต่ไม่นับ load:
    - นภาภรณ์ (esq_head role) — เห็นใน stat แต่ load = 0
    ใช้ใน UI แสดงว่า "ยกเว้น" ไม่ใช่ไม่มีตัวตน
    """
    return user.role == models.UserRole.esq_head


def is_room_keeper(user: "models.User") -> bool:
    """ธีราภัณฑ์ + ชนะชล — เปิด/ปิดห้อง"""
    return getattr(user, "special_role", None) == "room_keeper"


def is_esq_staff(user: "models.User") -> bool:
    """
    Legacy: อารยา + สัพพัญญู ไม่ได้เป็น esq_staff พิเศษอีกต่อไป
    ทั้งสองคนเป็น staff ปกติ eligible_supervisor ปกติ
    ฟังก์ชันนี้ยังคงไว้เพื่อ backward compat แต่ไม่มีใครมี special_role=esq_staff
    """
    return getattr(user, "special_role", None) == "esq_staff"  # จะ return False เสมอ


def assert_dept_access(user: "models.User", dept_code: str):
    """
    ตรวจว่า user มีสิทธิ์ดู/แก้ไขข้อมูลของ dept_code นี้
    Raises 403 ถ้าไม่มีสิทธิ์
    """
    if user.role in (models.UserRole.admin,
                     models.UserRole.esq_head,
                     models.UserRole.secretary):
        return   # เห็นทุก dept
    if user.role == models.UserRole.dept_supervisor:
        if user.dept_code != dept_code:
            raise HTTPException(403,
                f"คุณมีสิทธิ์เข้าถึงเฉพาะภาควิชา {user.dept_code} เท่านั้น")
        return
    # teacher — เห็นเฉพาะ dept ตัวเอง
    if user.role == models.UserRole.teacher:
        if user.dept_code and user.dept_code != dept_code:
            raise HTTPException(403,
                f"คุณมีสิทธิ์เข้าถึงเฉพาะภาควิชา {user.dept_code} เท่านั้น")
        return
    raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึงข้อมูลนี้")

# SIGN_ORDER — ใช้ร่วมกับ optimize_workflow
SIGN_ORDER_USERNAMES = ["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]

def log_action(
    db: Session,
    actor: models.User,
    action: str,
    table_name: str = None,
    record_id: int = None,
    old_values: dict = None,
    new_values: dict = None,
    request=None,
    duration_ms: int = None,
    http_status: int = None,
):
    ip_hash = None
    user_agent_hash = None
    request_id = None

    if request:
        ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        ua = request.headers.get("user-agent", "")
        if ua:
            user_agent_hash = hashlib.sha256(ua.encode()).hexdigest()[:32]
        request_id = request.headers.get("x-request-id")

    # ดึง request_id จาก context ถ้าไม่มีใน header
    if not request_id:
        try:
            from logging_config import get_request_id
            request_id = get_request_id() or None
        except ImportError:
            pass

    log = models.AuditLog(
        actor_id        = actor.id,
        action          = action,
        table_name      = table_name,
        record_id       = record_id,
        old_values      = old_values,
        new_values      = new_values,
        ip_hash         = ip_hash,
        user_agent_hash = user_agent_hash,
        request_id      = request_id,
        duration_ms     = duration_ms,
        http_status     = http_status,
    )
    db.add(log)
    db.commit()

    # structured log
    try:
        from logging_config import app_log
        app_log.info(
            f"AUDIT: {action}",
            extra={"action": action, "table": table_name,
                   "record_id": record_id, "actor": actor.username}
        )
    except ImportError:
        pass
