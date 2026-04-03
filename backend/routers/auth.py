from fastapi import APIRouter, Depends, HTTPException, Request
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
from database import get_db
import models
import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == data.username,
        models.User.is_active == True,
    ).first()

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
                "ip": request.client.host if request.client else "unknown",
                "reason": "user_not_found" if not user else "wrong_password",
            },
        )
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="บัญชีผู้ใช้ถูกปิดใช้งาน")

    token = create_token({"sub": str(user.id)})
    log_action(db, user, "LOGIN", request=request, http_status=200)

    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserMe(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            view_as_role=user.view_as_role,
            effective_role=get_effective_role(user),
        ),
    )


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
        db,
        current_user,
        "VIEW_AS_CHANGE",
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
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    revoke_token(token, db)
    current_user.view_as_role = None
    db.commit()
    log_action(db, current_user, "LOGOUT", request=request, http_status=200)
    return {"success": True}
