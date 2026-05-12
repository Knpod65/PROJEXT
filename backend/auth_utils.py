"""
Auth utilities
- Password hashing (bcrypt)
- JWT token (HS256)
- Admin "view-as" impersonation
- Dual-mode token extraction: HttpOnly cookie (preferred) + Bearer header (legacy)
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models, os, hashlib
from academic_groups import can_access_academic_group, normalize_academic_group_code
from config.policy import SIGN_ORDER_USERNAMES, TOKEN_EXPIRE_HOURS

_raw_secret = os.getenv("SECRET_KEY", "")
if not _raw_secret:
    import sys
    _dev_secret = "ems_dev_only_DO_NOT_USE_IN_PRODUCTION_2025_change_me"
    print("⚠  WARNING: SECRET_KEY not set — using insecure dev default.", file=sys.stderr)
    SECRET_KEY = _dev_secret
else:
    SECRET_KEY = _raw_secret

ALGORITHM          = "HS256"

# Keep OAuth2PasswordBearer for OpenAPI docs / legacy Bearer clients
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
GOVERNANCE_ROLE_KEY = "governance"
WORKSPACE_REJECTION_MESSAGE = "You are not assigned to this workspace. Please check your role and try again."


@dataclass
class RequestAuthState:
    token: Optional[str]
    user: Optional["models.User"]
    invalid_token: bool = False


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


def get_available_roles(user: models.User) -> list[models.UserRole]:
    return [user.role]


def build_workspace_rejection_detail(
    user: models.User,
    selected_role: str,
) -> dict[str, object]:
    return {
        "code": "workspace_not_assigned",
        "message": WORKSPACE_REJECTION_MESSAGE,
        "selected_role": selected_role,
        "assigned_roles": [role.value for role in get_available_roles(user)],
    }


def _coerce_user_role(value: object) -> models.UserRole | None:
    from permissions import coerce_user_role

    return coerce_user_role(value)


def resolve_active_role(user: models.User, selected_role: str) -> models.UserRole:
    available_roles = get_available_roles(user)
    requested = (selected_role or "").strip()

    if not requested:
        raise HTTPException(status_code=400, detail="selected_role is required")

    if requested == GOVERNANCE_ROLE_KEY:
        if user.role in (models.UserRole.esq_head, models.UserRole.secretary):
            return user.role
        raise HTTPException(
            status_code=403,
            detail=build_workspace_rejection_detail(user, requested),
        )

    requested_role = _coerce_user_role(requested)
    if not requested_role:
        raise HTTPException(status_code=400, detail="The selected role is invalid.")
    if requested_role not in available_roles:
        raise HTTPException(
            status_code=403,
            detail=build_workspace_rejection_detail(user, requested),
        )
    return requested_role


def get_active_role(user: models.User) -> models.UserRole:
    active_role = _coerce_user_role(getattr(user, "_active_role", None))
    if active_role:
        return active_role
    return user.role


def _build_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token not provided or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_request_token(request: Request, bearer_token: Optional[str]) -> Optional[str]:
    return request.cookies.get("ems_session") or bearer_token


def _resolve_user_from_token(token: str, db: Session) -> Optional[models.User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        active_role = _coerce_user_role(payload.get("active_role"))
    except JWTError:
        return None

    if is_token_revoked(token, db):
        return None

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_active:
        return None
    if active_role and active_role not in get_available_roles(user):
        return None
    setattr(user, "_active_role", active_role or user.role)
    return user


def resolve_request_auth(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> RequestAuthState:
    token = _get_request_token(request, bearer_token)
    if not token:
        return RequestAuthState(token=None, user=None, invalid_token=False)

    user = _resolve_user_from_token(token, db)
    return RequestAuthState(token=token, user=user, invalid_token=user is None)


def _get_current_user_legacy(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dual-mode token extraction:
      1. HttpOnly cookie 'ems_session' (preferred — JS cannot read)
      2. Authorization: Bearer <token> (legacy / API clients)
    Cookie takes priority when both are present.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ไม่ถูกต้องหรือหมดอายุ",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try cookie first, then Bearer header
    token = request.cookies.get("ems_session") or bearer_token
    if not token:
        raise credentials_exc

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exc
        active_role = _coerce_user_role(payload.get("active_role"))
    except JWTError:
        raise credentials_exc

    # Check blacklist
    if is_token_revoked(token, db):
        raise credentials_exc

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise credentials_exc
    if active_role and active_role not in get_available_roles(user):
        raise credentials_exc
    setattr(user, "_active_role", active_role or user.role)
    return user


def get_current_user(
    auth_state: RequestAuthState = Depends(resolve_request_auth),
) -> models.User:
    if not auth_state.user:
        raise _build_credentials_exception()
    return auth_state.user


def get_current_user_optional(
    auth_state: RequestAuthState = Depends(resolve_request_auth),
) -> Optional[models.User]:
    return auth_state.user


def get_effective_role(user: models.User) -> models.UserRole:
    """role ที่ใช้งานจริง — ถ้า admin impersonate ใช้ view_as_role"""
    if user.role == models.UserRole.admin and user.view_as_role:
        return user.view_as_role
    return get_active_role(user)


def require_base_admin(user: models.User = Depends(get_current_user)):
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ admin")
    return user

def require_admin(user: models.User = Depends(get_current_user)):
    if get_effective_role(user) != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ admin")
    return user

def require_staff_or_admin(user: models.User = Depends(get_current_user)):
    if get_effective_role(user) not in (models.UserRole.admin, models.UserRole.staff):
        raise HTTPException(status_code=403, detail="ต้องการสิทธิ์ staff หรือ admin")
    return user



# ── Role helpers ─────────────────────────────────────────────

def require_print_shop(user: models.User = Depends(get_current_user)):
    if get_effective_role(user) != models.UserRole.print_shop:
        raise HTTPException(status_code=403, detail="Print shop role required")
    return user

def is_view_all_role(user: "models.User") -> bool:
    """esq_head + secretary เห็นทุกอย่าง แต่ edit ไม่ได้"""
    return get_effective_role(user) in (models.UserRole.esq_head, models.UserRole.secretary)

def is_signer(user: "models.User") -> bool:
    """admin + esq_head + secretary ลงนามได้"""
    return get_effective_role(user) in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    )

def require_view_all(user: "models.User" = Depends(get_current_user)):
    """เฉพาะ admin / esq_head / secretary"""
    if get_effective_role(user) not in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        raise HTTPException(403, "ต้องการสิทธิ์ระดับ admin หรือผู้มีอำนาจอนุมัติ")
    return user

def require_dept_or_admin(user: "models.User" = Depends(get_current_user)):
    """admin / dept_supervisor / esq_head / secretary"""
    if get_effective_role(user) not in (
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
    if get_effective_role(user) in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        return None   # ไม่ filter
    if get_effective_role(user) in (models.UserRole.dept_supervisor, models.UserRole.teacher):
        return normalize_academic_group_code(user.dept_code)
    return None



def require_read_only(user: "models.User" = Depends(get_current_user)):
    """
    esq_head + secretary อ่านได้อย่างเดียว
    ใช้ใน endpoints ที่ต้องการ block การแก้ไข
    """
    if get_effective_role(user) in (models.UserRole.esq_head, models.UserRole.secretary):
        raise HTTPException(403,
            "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว — ไม่สามารถแก้ไขได้")
    return user


def require_can_edit(user: "models.User" = Depends(get_current_user)):
    """
    แก้ไขได้: admin + teacher + dept_supervisor
    ไม่ได้: esq_head, secretary (read-only), staff (ไม่มี edit rights)
    """
    if get_effective_role(user) in (models.UserRole.esq_head, models.UserRole.secretary):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    if get_effective_role(user) not in (
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
    if get_effective_role(user) != models.UserRole.staff:
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
    return get_effective_role(user) == models.UserRole.esq_head


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
    effective_role = get_effective_role(user)
    target_group = normalize_academic_group_code(dept_code)
    viewer_group = normalize_academic_group_code(getattr(user, "dept_code", None))

    if effective_role in (
        models.UserRole.admin,
        models.UserRole.esq_head,
        models.UserRole.secretary,
    ):
        return

    if effective_role == models.UserRole.dept_supervisor:
        if not can_access_academic_group(viewer_group, target_group):
            raise HTTPException(
                403,
                f"เธเธธเธ“เธกเธตเธชเธดเธ—เธเธดเนเน€เธเนเธฒเธ–เธถเธเน€เธเธเธฒเธฐเธ เธฒเธเธงเธดเธเธฒ {viewer_group or user.dept_code} เน€เธ—เนเธฒเธเธฑเนเธ",
            )
        return

    if effective_role == models.UserRole.teacher:
        if viewer_group and not can_access_academic_group(viewer_group, target_group):
            raise HTTPException(
                403,
                f"เธเธธเธ“เธกเธตเธชเธดเธ—เธเธดเนเน€เธเนเธฒเธ–เธถเธเน€เธเธเธฒเธฐเธ เธฒเธเธงเธดเธเธฒ {viewer_group} เน€เธ—เนเธฒเธเธฑเนเธ",
            )
        return

    raise HTTPException(403, "เนเธกเนเธกเธตเธชเธดเธ—เธเธดเนเน€เธเนเธฒเธ–เธถเธเธเนเธญเธกเธนเธฅเธเธตเน")

    if get_effective_role(user) in (models.UserRole.admin,
                     models.UserRole.esq_head,
                     models.UserRole.secretary):
        return   # เห็นทุก dept
    if get_effective_role(user) == models.UserRole.dept_supervisor:
        if user.dept_code != dept_code:
            raise HTTPException(403,
                f"คุณมีสิทธิ์เข้าถึงเฉพาะภาควิชา {user.dept_code} เท่านั้น")
        return
    # teacher — เห็นเฉพาะ dept ตัวเอง
    if get_effective_role(user) == models.UserRole.teacher:
        if user.dept_code and user.dept_code != dept_code:
            raise HTTPException(403,
                f"คุณมีสิทธิ์เข้าถึงเฉพาะภาควิชา {user.dept_code} เท่านั้น")
        return
    raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึงข้อมูลนี้")

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
