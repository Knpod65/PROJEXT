from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session, joinedload, contains_eager
from typing import List, Optional
from database import get_db
import models, schemas
from auth_utils import get_current_user, require_admin, require_staff_or_admin, log_action

router = APIRouter()


# ── Courses ──────────────────────────────────────────────────
@router.get("/", response_model=List[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Course).order_by(models.Course.course_id).all()


# ── Sections ──────────────────────────────────────────────────
@router.get("/sections", response_model=List[schemas.SectionOut])
def list_sections(
    search: Optional[str] = Query(None),
    semester: str = Query("2"),
    academic_year: str = Query("2568"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from auth_utils import get_effective_role
    effective = get_effective_role(current_user)

    q = db.query(models.Section).join(
        models.Course, models.Section.course_id == models.Course.id, isouter=True
    ).options(
        contains_eager(models.Section.course),
        joinedload(models.Section.teacher),
        joinedload(models.Section.schedules).joinedload(models.ExamSchedule.room),
        joinedload(models.Section.schedules).joinedload(models.ExamSchedule.supervisions)
            .joinedload(models.Supervision.user),
    ).filter(
        models.Section.semester == semester,
        models.Section.academic_year == academic_year
    )

    # Teacher เห็นเฉพาะวิชาตัวเอง
    if effective == models.UserRole.teacher:
        q = q.filter(models.Section.teacher_id == current_user.id)

    if search:
        q = q.filter(
            (models.Course.course_id.ilike(f"%{search}%")) |
            (models.Course.course_name_th.ilike(f"%{search}%")) |
            (models.Course.course_name_en.ilike(f"%{search}%"))
        )

    return q.order_by(models.Course.course_id).all()


@router.post("/sections", response_model=schemas.SectionOut)
def create_section(
    data: schemas.SectionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    section = models.Section(**data.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    log_action(db, current_user, "CREATE_SECTION", "sections", section.id,
               new_values=data.model_dump(), request=request)
    return db.query(models.Section).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
    ).filter(models.Section.id == section.id).first()


@router.put("/sections/{sid}", response_model=schemas.SectionOut)
def update_section(
    sid: int,
    data: schemas.SectionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    section = db.query(models.Section).filter(models.Section.id == sid).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(section, k, v)
    db.commit()
    log_action(db, current_user, "UPDATE_SECTION", "sections", sid, request=request)
    return db.query(models.Section).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
        joinedload(models.Section.schedules),
    ).filter(models.Section.id == sid).first()


@router.delete("/sections/{sid}")
def delete_section(
    sid: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    section = db.query(models.Section).filter(models.Section.id == sid).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")
    db.delete(section)
    db.commit()
    log_action(db, current_user, "DELETE_SECTION", "sections", sid, request=request)
    return {"success": True}


# ── Rooms ─────────────────────────────────────────────────────
@router.get("/rooms", response_model=List[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Room).filter(models.Room.is_active == True).all()


@router.post("/rooms", response_model=schemas.RoomOut)
def create_room(
    data: schemas.RoomCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin)
):
    room = models.Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    log_action(db, current_user, "CREATE_ROOM", "rooms", room.id, request=request)
    return room
