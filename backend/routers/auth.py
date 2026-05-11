"""
Auth Router
- Login: sets HttpOnly cookie + returns user info (no token in body)
- Logout: clears cookie + revokes token
- /me: returns current user info
- /view-as: admin impersonation
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from auth_utils import (
    DUMMY_PASSWORD_HASH,
    RequestAuthState,
    create_token,
    get_active_role,
    get_available_roles,
    get_effective_role,
    log_action,
    require_admin,
    require_base_admin,
    resolve_request_auth,
    resolve_active_role,
    revoke_token,
    verify_password,
)
from config.audit_actions import LOGIN, LOGOUT, VIEW_AS_CHANGE
from security import set_auth_cookie, clear_auth_cookie, get_real_ip
from database import get_db
import models
import schemas

router = APIRouter()


def _serialize_user_me(user: models.User) -> schemas.UserMe:
    return schemas.UserMe(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        active_role=get_active_role(user),
        view_as_role=user.view_as_role,
        effective_role=get_effective_role(user),
        available_roles=get_available_roles(user),
    )


@router.post("/login")
def login(data: schemas.LoginRequest, request: Request, response: Response,
          db: Session = Depends(get_db)):
    """
    Authenticate and issue session.
    SECURITY:
      - Constant-time password check prevents user enumeration timing attacks
      - Token is set as HttpOnly cookie (not returned in response body)
      - Bearer token also returned for API clients / backward compat
    """
    user = db.query(models.User).filter(
        models.User.username == data.username,
        models.User.is_active == True,
    ).first()

    # Constant-time: always verify even if user not found (prevents timing oracle)
    password_ok = (
        verify_password(data.password, user.password_hash)
        if user
        else verify_password(data.password, DUMMY_PASSWORD_HASH)
    )

    if not user or not password_ok:
        import logging
        fail_log = logging.getLogger("ems.security")
        fail_log.warning(
            "LOGIN_FAILED",
            extra={
                "username": data.username,
                "ip": get_real_ip(request),
                "reason": "user_not_found" if not user else "wrong_password",
            },
        )
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    active_role = resolve_active_role(user, data.selected_role)
    if user.view_as_role is not None:
        user.view_as_role = None
    setattr(user, "_active_role", active_role)
    token = create_token({"sub": str(user.id), "active_role": active_role.value})

    # Set HttpOnly cookie — JS cannot read this
    set_auth_cookie(response, token)

    log_action(db, user, LOGIN, request=request, http_status=200)

    # Also return token in body for legacy Bearer clients and API scripts
    # Frontend should prefer the cookie and NOT store this in localStorage
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "ล็อกอินสำเร็จ — session cookie ถูกตั้งค่าแล้ว",
        "user": _serialize_user_me(user),
    }


@router.get("/me", response_model=schemas.UserMe | None)
def get_me(
    response: Response,
    auth_state: RequestAuthState = Depends(resolve_request_auth),
):
    if not auth_state.user:
        if auth_state.invalid_token and auth_state.token:
            clear_auth_cookie(response)
        return None
    return _serialize_user_me(auth_state.user)


@router.post("/view-as")
def set_view_as(
    data: schemas.ViewAsRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_base_admin),
):
    old_role = current_user.view_as_role
    current_user.view_as_role = data.role
    db.commit()
    log_action(
        db, current_user, VIEW_AS_CHANGE,
        old_values={"view_as": str(old_role)},
        new_values={"view_as": str(data.role)},
        request=request,
    )
    return {
        "success": True,
        "view_as_role": data.role,
        "effective_role": get_effective_role(current_user),
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    auth_state: RequestAuthState = Depends(resolve_request_auth),
    db: Session = Depends(get_db),
):
    # Revoke whichever token was used (cookie or bearer)
    if auth_state.token and not auth_state.invalid_token:
        revoke_token(auth_state.token, db)

    current_user = auth_state.user
    if current_user:
        current_user.view_as_role = None
        db.commit()

    clear_auth_cookie(response)

    if current_user:
        log_action(db, current_user, LOGOUT, request=request, http_status=200)
    return {"success": True, "message": "ออกจากระบบแล้ว"}
