"""
Auth Router
- Login: sets HttpOnly cookie + returns user info (no token in body)
- Logout: clears cookie + revokes token
- /me: returns current user info
- /view-as: admin impersonation
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from auth_utils import (
    DUMMY_PASSWORD_HASH,
    create_token,
    get_current_user,
    get_effective_role,
    log_action,
    require_admin,
    revoke_token,
    verify_password,
)
from security import set_auth_cookie, clear_auth_cookie, get_real_ip
from database import get_db
import models
import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
router = APIRouter()


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

    token = create_token({"sub": str(user.id)})

    # Set HttpOnly cookie — JS cannot read this
    set_auth_cookie(response, token)

    log_action(db, user, "LOGIN", request=request, http_status=200)

    # Also return token in body for legacy Bearer clients and API scripts
    # Frontend should prefer the cookie and NOT store this in localStorage
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "ล็อกอินสำเร็จ — session cookie ถูกตั้งค่าแล้ว",
        "user": schemas.UserMe(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            view_as_role=user.view_as_role,
            effective_role=get_effective_role(user),
        ),
    }


@router.get("/me", response_model=schemas.UserMe)
def get_me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserMe(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        view_as_role=current_user.view_as_role,
        effective_role=get_effective_role(current_user),
    )


@router.post("/view-as")
def set_view_as(
    data: schemas.ViewAsRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    old_role = current_user.view_as_role
    current_user.view_as_role = data.role
    db.commit()
    log_action(
        db, current_user, "VIEW_AS_CHANGE",
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
    bearer_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Revoke whichever token was used (cookie or bearer)
    token = request.cookies.get("ems_session") or bearer_token
    if token:
        revoke_token(token, db)

    current_user.view_as_role = None
    db.commit()

    # Clear cookie
    clear_auth_cookie(response)

    log_action(db, current_user, "LOGOUT", request=request, http_status=200)
    return {"success": True, "message": "ออกจากระบบแล้ว"}
