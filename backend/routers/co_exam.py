"""
Co-Exam Router — จัดกลุ่มวิชาสอบร่วม

เหตุผล: ลดจำนวนกรรมการ ใช้ห้องร่วมกัน
  - วิชาเดียว คนละตอน: 126101 sec1+sec2+sec5 → รวมนักศึกษา 216 คน ใช้ Auditorium
  - ต่างวิชา อาจารย์คนเดียว: optimizer จัด slot เดียวกัน กรรมการชุดเดียว

POST /api/co-exam/                สร้างกลุ่ม
GET  /api/co-exam/                รายการกลุ่มใน active period
GET  /api/co-exam/{id}            รายละเอียด
PUT  /api/co-exam/{id}            แก้ไข
DELETE /api/co-exam/{id}          ลบ
POST /api/co-exam/{id}/members    เพิ่ม section เข้ากลุ่ม
DELETE /api/co-exam/{id}/members/{section_id}  ถอด section
POST /api/co-exam/auto-detect     ตรวจหากลุ่มอัตโนมัติ (same teacher / same course)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import and_, func
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
import models
from auth_utils import require_admin, get_current_user, log_action

router = APIRouter()


class CoExamCreate(BaseModel):
    label:       str
    exam_date:   str
    exam_time:   str
    exam_type:   str = "final"
    section_ids: List[int] = []


class CoExamUpdate(BaseModel):
    label:     Optional[str] = None
    exam_date: Optional[str] = None
    exam_time: Optional[str] = None


class AddMembersRequest(BaseModel):
    section_ids: List[int]


def _get_active_period(db):
    p = db.query(models.ExamPeriod).filter(models.ExamPeriod.is_active == True).first()
    if not p:
        raise HTTPException(400, "ไม่มี active period")
    return p


def _group_dict(g: models.CoExamGroup) -> dict:
    members = []
    for m in g.members:
        sec  = m.section
        if not sec:
            continue
        course = sec.course
        members.append({
            "member_id":   m.id,
            "section_id":  sec.id,
            "section_no":  sec.section_no,
            "course_id":   course.course_id   if course else None,
            "course_name": course.course_name_th if course else None,
            "num_students":sec.num_students or 0,
            "teacher":     sec.teacher.full_name if sec.teacher else None,
        })
    return {
        "id":            g.id,
        "group_key":     g.group_key,
        "label":         g.label,
        "exam_date":     g.exam_date,
        "exam_time":     g.exam_time,
        "exam_type":     g.exam_type,
        "total_students":g.total_students,
        "members":       members,
        "member_count":  len(members),
    }


@router.get("/")
def list_co_exam_groups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    p = _get_active_period(db)
    groups = db.query(models.CoExamGroup).options(
        joinedload(models.CoExamGroup.members)
            .joinedload(models.CoExamMember.section)
            .joinedload(models.Section.course),
        joinedload(models.CoExamGroup.members)
            .joinedload(models.CoExamMember.section)
            .joinedload(models.Section.teacher),
    ).filter(
        models.CoExamGroup.exam_period_id == p.id
    ).order_by(models.CoExamGroup.exam_date, models.CoExamGroup.exam_time).all()

    return [_group_dict(g) for g in groups]


@router.post("/")
def create_co_exam_group(
    data: CoExamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    p = _get_active_period(db)

    import secrets as _sec
    group_key = f"co_{data.exam_date}_{data.exam_time}_{_sec.token_hex(4)}".replace(":", "").replace(".", "")

    group = models.CoExamGroup(
        exam_period_id = p.id,
        group_key      = group_key,
        label          = data.label,
        exam_date      = data.exam_date,
        exam_time      = data.exam_time,
        exam_type      = data.exam_type,
        created_by     = current_user.id,
    )
    db.add(group)
    db.flush()

    total_stu = 0
    for sec_id in data.section_ids:
        sec = db.query(models.Section).filter(models.Section.id == sec_id).first()
        if not sec:
            continue
        db.add(models.CoExamMember(group_id=group.id, section_id=sec_id))
        total_stu += sec.num_students or 0
        # อัปเดต section flag
        sec.is_co_exam  = True
        sec.co_group_id = group_key

    group.total_students = total_stu
    db.commit()
    db.refresh(group)

    log_action(db, current_user, "CREATE_CO_EXAM", "co_exam_groups",
               record_id=group.id,
               new_values={"label": data.label, "sections": data.section_ids},
               request=request)

    return _group_dict(db.query(models.CoExamGroup).options(
        joinedload(models.CoExamGroup.members)
            .joinedload(models.CoExamMember.section)
            .joinedload(models.Section.course),
    ).filter(models.CoExamGroup.id == group.id).first())


@router.put("/{group_id}")
def update_co_exam_group(
    group_id: int,
    data: CoExamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    group = db.query(models.CoExamGroup).filter(models.CoExamGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "ไม่พบกลุ่ม")
    if data.label:     group.label     = data.label
    if data.exam_date: group.exam_date = data.exam_date
    if data.exam_time: group.exam_time = data.exam_time
    db.commit()
    log_action(db, current_user, "UPDATE_CO_EXAM", "co_exam_groups",
               record_id=group_id, request=request)
    return {"status": "updated"}


@router.delete("/{group_id}")
def delete_co_exam_group(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    group = db.query(models.CoExamGroup).filter(models.CoExamGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "ไม่พบกลุ่ม")
    # reset section flags
    for m in group.members:
        if m.section:
            m.section.is_co_exam  = False
            m.section.co_group_id = None
    db.delete(group)
    db.commit()
    log_action(db, current_user, "DELETE_CO_EXAM", "co_exam_groups",
               record_id=group_id, request=request)
    return {"status": "deleted"}


@router.post("/{group_id}/members")
def add_members(
    group_id: int,
    data: AddMembersRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    group = db.query(models.CoExamGroup).filter(models.CoExamGroup.id == group_id).first()
    if not group:
        raise HTTPException(404, "ไม่พบกลุ่ม")

    existing = {m.section_id for m in group.members}
    added = []
    for sec_id in data.section_ids:
        if sec_id in existing:
            continue
        sec = db.query(models.Section).filter(models.Section.id == sec_id).first()
        if not sec:
            continue
        db.add(models.CoExamMember(group_id=group.id, section_id=sec_id))
        sec.is_co_exam  = True
        sec.co_group_id = group.group_key
        added.append(sec_id)

    # อัปเดต total_students
    group.total_students = sum(
        (m.section.num_students or 0)
        for m in db.query(models.CoExamMember).filter(
            models.CoExamMember.group_id == group_id
        ).options(joinedload(models.CoExamMember.section)).all()
    )
    db.commit()
    log_action(db, current_user, "ADD_CO_EXAM_MEMBERS", "co_exam_members",
               record_id=group_id,
               new_values={"added_sections": added},
               request=request)
    return {"added": added, "total_students": group.total_students}


@router.delete("/{group_id}/members/{section_id}")
def remove_member(
    group_id: int,
    section_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    member = db.query(models.CoExamMember).filter(
        and_(
            models.CoExamMember.group_id   == group_id,
            models.CoExamMember.section_id == section_id,
        )
    ).first()
    if not member:
        raise HTTPException(404, "ไม่พบ member")

    sec = member.section
    if sec:
        # ตรวจว่า section นี้ยังอยู่ในกลุ่มอื่นไหม
        other = db.query(models.CoExamMember).filter(
            and_(
                models.CoExamMember.section_id != member.id,
                models.CoExamMember.section_id == section_id,
            )
        ).first()
        if not other:
            sec.is_co_exam  = False
            sec.co_group_id = None

    db.delete(member)
    db.commit()
    log_action(db, current_user, "REMOVE_CO_EXAM_MEMBER", "co_exam_members",
               new_values={"group_id": group_id, "section_id": section_id},
               request=request)
    return {"status": "removed"}


@router.post("/auto-detect")
def auto_detect_co_exams(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    ตรวจหากลุ่มอัตโนมัติ:
    1. วิชาเดียวกัน หลายตอน (is_co_exam=True ใน data)
    2. อาจารย์คนเดียวกัน สอบวัน+เวลาเดียวกัน
    """
    p = _get_active_period(db)
    sections = db.query(models.Section).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
        joinedload(models.Section.schedules)
            .load_only(
                models.ExamSchedule.exam_date,
                models.ExamSchedule.exam_time,
                models.ExamSchedule.exam_type,
            ),
    ).filter(
        and_(
            models.Section.semester      == p.semester,
            models.Section.academic_year == p.academic_year,
        )
    ).all()

    suggestions = []

    # Case 1: same course_id + same exam_date + same exam_time
    from collections import defaultdict
    by_course_slot = defaultdict(list)
    for sec in sections:
        sch = next((s for s in sec.schedules if s.exam_type.value == p.exam_type), None)
        if sch and sch.exam_date and sch.exam_time:
            key = (sec.course.course_id if sec.course else "?",
                   sch.exam_date, sch.exam_time)
            by_course_slot[key].append(sec)

    for (course_id, date, time), secs in by_course_slot.items():
        if len(secs) > 1:
            total = sum(s.num_students or 0 for s in secs)
            suggestions.append({
                "type":        "same_course",
                "label":       f"{course_id} รวม {len(secs)} ตอน ({total} คน) — {date} {time}",
                "exam_date":   date,
                "exam_time":   time,
                "exam_type":   p.exam_type,
                "section_ids": [s.id for s in secs],
                "total_students": total,
                "sections":    [{"id":s.id,"no":s.section_no,"n":s.num_students} for s in secs],
            })

    # Case 2: same teacher + same exam_date + same exam_time (ต่างวิชา)
    by_teacher_slot = defaultdict(list)
    for sec in sections:
        if not sec.teacher_id:
            continue
        sch = next((s for s in sec.schedules if s.exam_type.value == p.exam_type), None)
        if sch and sch.exam_date and sch.exam_time:
            key = (sec.teacher_id, sch.exam_date, sch.exam_time)
            by_teacher_slot[key].append(sec)

    for (teacher_id, date, time), secs in by_teacher_slot.items():
        # กรองเฉพาะต่างวิชา (ถ้าวิชาเดียวกันจะถูก Case 1 จับแล้ว)
        course_ids = {(s.course.course_id if s.course else None) for s in secs}
        if len(secs) > 1 and len(course_ids) > 1:
            teacher_name = secs[0].teacher.full_name if secs[0].teacher else f"teacher#{teacher_id}"
            total = sum(s.num_students or 0 for s in secs)
            suggestions.append({
                "type":        "same_teacher",
                "label":       f"{teacher_name} สอน {len(secs)} วิชา ({total} คน) — {date} {time}",
                "exam_date":   date,
                "exam_time":   time,
                "exam_type":   p.exam_type,
                "section_ids": [s.id for s in secs],
                "total_students": total,
                "sections":    [
                    {"id":s.id, "course": s.course.course_id if s.course else "?",
                     "no":s.section_no, "n":s.num_students}
                    for s in secs
                ],
            })

    return {
        "suggestions":    suggestions,
        "count":          len(suggestions),
        "note": "ใช้ POST /co-exam/ พร้อม section_ids เพื่อสร้างกลุ่ม",
    }
