from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from auth_utils import (
    hash_password, get_current_user, require_admin, log_action
)

router = APIRouter()


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    return db.query(models.User).order_by(models.User.full_name).all()


@router.post("/", response_model=schemas.UserOut)
def create_user(
    data: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    exists = db.query(models.User).filter(
        (models.User.username == data.username) | (models.User.email == data.email)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="username หรือ email ซ้ำ")

    user = models.User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        full_name=data.full_name,
        department=data.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, current_user, "CREATE_USER", "users", user.id,
               new_values={"username": user.username, "role": str(user.role)},
               request=request)
    return user


@router.put("/{uid}", response_model=schemas.UserOut)
def update_user(
    uid: int,
    data: schemas.UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    updates = data.model_dump(exclude_none=True)
    old = {"role": str(user.role), "is_active": user.is_active}
    for field, val in updates.items():
        setattr(user, field, val)
    if data.role and data.role != models.UserRole.admin:
        user.view_as_role = None
    db.commit()
    db.refresh(user)
    log_action(db, current_user, "UPDATE_USER", "users", uid,
               old_values=old, new_values=updates,
               request=request)
    return user


@router.delete("/{uid}")
def delete_user(
    uid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    if user.username == "admin" or user.email == current_user.email:
        raise HTTPException(status_code=400, detail="ไม่สามารถลบบัญชีนี้ได้")
    # Soft delete — ปิดใช้งานแทนการลบจริง เพื่อรักษา FK references
    user.is_active = False
    db.commit()
    log_action(db, current_user, "DEACTIVATE_USER", "users", uid, request=request)
    return {"success": True, "message": f"{user.full_name} ถูกปิดใช้งานแล้ว"}


@router.get("/teachers", response_model=List[schemas.UserOut])
def list_teachers(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    return db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True
    ).order_by(models.User.full_name).all()
