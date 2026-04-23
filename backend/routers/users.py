from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List

from auth_utils import hash_password, get_current_user, require_admin, log_action
from academic_groups import normalize_academic_group_code
from database import get_db
import models
import schemas

router = APIRouter()

PROTECTED_USERNAMES = {"admin"}
DELETE_BLOCKED_MESSAGE = (
    "This user has linked exam or audit records and cannot be deleted. "
    "Deactivate the account instead."
)
LAST_ADMIN_MESSAGE = "At least one active administrator must remain in the system."


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_username(value: object) -> str:
    username = _clean_text(value)
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
    return username


def _normalize_email(value: object) -> str:
    email = _clean_text(value)
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
    return email.lower()


def _dept_code_for_role(role: models.UserRole, department: str | None, fallback: str | None = None) -> str | None:
    if role in (models.UserRole.teacher, models.UserRole.dept_supervisor):
        return normalize_academic_group_code(department) or normalize_academic_group_code(fallback) or department or fallback
    return None


def _assert_unique_identity(
    db: Session,
    *,
    username: str,
    email: str,
    exclude_user_id: int | None = None,
) -> None:
    query = db.query(models.User).filter(
        or_(
            func.lower(models.User.username) == username.lower(),
            func.lower(models.User.email) == email.lower(),
        )
    )
    if exclude_user_id is not None:
        query = query.filter(models.User.id != exclude_user_id)

    if query.first():
        raise HTTPException(
            status_code=400,
            detail="A user with this username or email already exists.",
        )


def _count_other_active_admins(db: Session, user_id: int) -> int:
    return db.query(models.User).filter(
        models.User.role == models.UserRole.admin,
        models.User.is_active == True,
        models.User.id != user_id,
    ).count()


def _assert_not_last_active_admin(
    db: Session,
    user: models.User,
    *,
    next_role: models.UserRole | None = None,
    next_is_active: bool | None = None,
) -> None:
    effective_role = next_role if next_role is not None else user.role
    effective_active = next_is_active if next_is_active is not None else user.is_active

    if (
        user.role == models.UserRole.admin
        and user.is_active
        and (effective_role != models.UserRole.admin or not effective_active)
        and _count_other_active_admins(db, user.id) == 0
    ):
        raise HTTPException(status_code=400, detail=LAST_ADMIN_MESSAGE)


def _serialize_user_identity(user: models.User) -> dict[str, object]:
    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "department": user.department,
        "role": user.role.value if isinstance(user.role, models.UserRole) else str(user.role),
        "is_active": user.is_active,
    }


def _apply_user_update(user: models.User, payload: dict[str, object]) -> dict[str, object]:
    applied: dict[str, object] = {}

    if "username" in payload:
        user.username = _normalize_username(payload["username"])
        applied["username"] = user.username

    if "email" in payload:
        user.email = _normalize_email(payload["email"])
        applied["email"] = user.email

    if "full_name" in payload:
        user.full_name = _clean_text(payload["full_name"])
        applied["full_name"] = user.full_name

    if "department" in payload:
        user.department = _clean_text(payload["department"])
        applied["department"] = user.department

    if "role" in payload and payload["role"] is not None:
        user.role = payload["role"]
        user.dept_code = _dept_code_for_role(user.role, user.department, user.dept_code)
        if user.role != models.UserRole.admin:
            user.view_as_role = None
        applied["role"] = user.role.value

    if "department" in payload and "role" not in payload:
        user.dept_code = _dept_code_for_role(user.role, user.department, user.dept_code)

    if "is_active" in payload and payload["is_active"] is not None:
        user.is_active = bool(payload["is_active"])
        if not user.is_active:
            user.view_as_role = None
        applied["is_active"] = user.is_active

    return applied


def _delete_blockers(db: Session, user_id: int) -> list[str]:
    blockers: list[str] = []

    checks = [
        ("teaching sections", db.query(models.Section.id).filter(models.Section.teacher_id == user_id).first()),
        (
            "ownership assignments",
            db.query(models.SectionExamManager.id).filter(
                or_(
                    models.SectionExamManager.manager_id == user_id,
                    models.SectionExamManager.proposed_by == user_id,
                    models.SectionExamManager.confirmed_by == user_id,
                )
            ).first(),
        ),
        (
            "exam submissions",
            db.query(models.ExamSubmission.id).filter(
                or_(
                    models.ExamSubmission.submitted_by == user_id,
                    models.ExamSubmission.approved_by == user_id,
                )
            ).first(),
        ),
        ("submission history", db.query(models.ExamSubmissionVersion.id).filter(models.ExamSubmissionVersion.changed_by == user_id).first()),
        ("exam access tokens", db.query(models.ExamAccessToken.id).filter(models.ExamAccessToken.issued_to == user_id).first()),
        (
            "print queue jobs",
            db.query(models.PrintQueueJob.id).filter(
                or_(
                    models.PrintQueueJob.created_by == user_id,
                    models.PrintQueueJob.assigned_to == user_id,
                )
            ).first(),
        ),
        (
            "supervision assignments",
            db.query(models.Supervision.id).filter(
                or_(
                    models.Supervision.user_id == user_id,
                    models.Supervision.swap_with_id == user_id,
                    models.Supervision.baseline_user_id == user_id,
                )
            ).first(),
        ),
        ("swap requests", db.query(models.SwapRequest.id).filter(or_(models.SwapRequest.requester_id == user_id, models.SwapRequest.target_id == user_id)).first()),
        ("check-ins", db.query(models.CheckinEvent.id).filter(models.CheckinEvent.user_id == user_id).first()),
        ("messages", db.query(models.ExamMessage.id).filter(models.ExamMessage.sender_id == user_id).first()),
        ("audit logs", db.query(models.AuditLog.id).filter(models.AuditLog.actor_id == user_id).first()),
        ("import sessions", db.query(models.ImportSession.id).filter(models.ImportSession.created_by == user_id).first()),
        ("import overrides", db.query(models.ImportRowLog.id).filter(models.ImportRowLog.override_by == user_id).first()),
        ("lecturer mappings", db.query(models.LecturerNameMap.id).filter(or_(models.LecturerNameMap.teacher_id == user_id, models.LecturerNameMap.confirmed_by == user_id)).first()),
        ("system settings", db.query(models.SystemSetting.id).filter(models.SystemSetting.updated_by == user_id).first()),
        ("period records", db.query(models.ExamPeriod.id).filter(models.ExamPeriod.created_by == user_id).first()),
    ]

    for label, record in checks:
        if record:
            blockers.append(label)

    return blockers


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.User).order_by(
        models.User.is_active.desc(),
        models.User.full_name.asc(),
        models.User.username.asc(),
    ).all()


@router.post("/", response_model=schemas.UserOut)
def create_user(
    data: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    username = _normalize_username(data.username)
    email = _normalize_email(data.email)
    _assert_unique_identity(db, username=username, email=email)

    department = _clean_text(data.department)
    user = models.User(
        username=username,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role,
        full_name=_clean_text(data.full_name),
        department=department,
        dept_code=_dept_code_for_role(data.role, department),
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(
        db,
        current_user,
        "CREATE_USER",
        "users",
        user.id,
        new_values=_serialize_user_identity(user),
        request=request,
    )
    return user


@router.put("/{uid}", response_model=schemas.UserOut)
def update_user(
    uid: int,
    data: schemas.UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    payload = data.model_dump(exclude_unset=True)
    next_username = _normalize_username(payload.get("username", user.username))
    next_email = _normalize_email(payload.get("email", user.email))
    _assert_unique_identity(db, username=next_username, email=next_email, exclude_user_id=uid)

    next_role = payload.get("role", user.role)
    next_is_active = payload.get("is_active", user.is_active)
    _assert_not_last_active_admin(db, user, next_role=next_role, next_is_active=next_is_active)

    old_values = _serialize_user_identity(user)
    applied = _apply_user_update(user, payload)
    db.commit()
    db.refresh(user)

    log_action(
        db,
        current_user,
        "UPDATE_USER",
        "users",
        uid,
        old_values=old_values,
        new_values=applied,
        request=request,
    )
    return user


@router.post("/{uid}/status", response_model=schemas.UserOut)
def update_user_status(
    uid: int,
    data: schemas.UserStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    _assert_not_last_active_admin(db, user, next_is_active=data.is_active)
    old_values = {"is_active": user.is_active}
    user.is_active = data.is_active
    if not user.is_active:
        user.view_as_role = None
    db.commit()
    db.refresh(user)

    log_action(
        db,
        current_user,
        "ACTIVATE_USER" if data.is_active else "DEACTIVATE_USER",
        "users",
        uid,
        old_values=old_values,
        new_values={"is_active": user.is_active},
        request=request,
    )
    return user


@router.delete("/{uid}")
def delete_user(
    uid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id or user.username in PROTECTED_USERNAMES:
        raise HTTPException(
            status_code=400,
            detail="This account cannot be deleted.",
        )

    _assert_not_last_active_admin(db, user, next_is_active=False, next_role=models.UserRole.staff)
    blockers = _delete_blockers(db, user.id)
    if blockers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "user_delete_blocked",
                "message": DELETE_BLOCKED_MESSAGE,
                "blockers": blockers,
            },
        )

    old_values = _serialize_user_identity(user)
    db.delete(user)
    db.commit()

    log_action(
        db,
        current_user,
        "DELETE_USER",
        "users",
        uid,
        old_values=old_values,
        request=request,
    )
    return {"success": True, "message": f"Deleted {old_values['username']}."}


@router.get("/teachers", response_model=List[schemas.UserOut])
def list_teachers(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True,
    ).order_by(models.User.full_name, models.User.username).all()
