"""
email_notifications.py — Email notification system
รอ SMTP credentials จาก CMU IT เพื่อ enable (no-op ถ้าไม่มี)

Events:
  ① Immediate: submission approved/rejected, swap request/response, propose manager
  ② Daily digest: สรุปการเปลี่ยนแปลงทั้งวัน + deadlines + pending actions
  ③ Exam day reminder: แจ้ง 1 วันก่อนสอบ (รายละเอียดครบ)
"""

import os, logging, smtplib, textwrap
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger("ems.email")

SMTP_HOST  = os.getenv("SMTP_HOST", "")
SMTP_PORT  = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER  = os.getenv("SMTP_USER", "")
SMTP_PASS  = os.getenv("SMTP_PASS", "")
FROM_ADDR  = os.getenv("EMAIL_FROM", "ems-noreply@polsci.cmu.ac.th")
APP_URL    = os.getenv("APP_URL", "https://ems.polsci.cmu.ac.th")
ENABLED    = bool(SMTP_HOST and SMTP_USER)

if not ENABLED:
    log.info("Email disabled — set SMTP_HOST + SMTP_USER to enable")

# ── สี brand ──────────────────────────────────────────────
NAVY   = "#0f1b35"
CRIMSON= "#c41230"
GOLD   = "#b8860b"
GREEN  = "#1a7a4a"
GRAY   = "#64748b"


def _html_wrap(body: str, title: str = "") -> str:
    """Base HTML email template"""
    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{{font-family:'Sarabun',Arial,sans-serif;background:#f1f5f9;margin:0;padding:20px}}
  .card{{background:#fff;border-radius:12px;max-width:600px;margin:0 auto;overflow:hidden;
         box-shadow:0 2px 12px rgba(0,0,0,.08)}}
  .header{{background:{NAVY};color:#fff;padding:24px 28px;}}
  .header h1{{margin:0;font-size:20px;font-weight:700}}
  .header .sub{{margin:4px 0 0;font-size:13px;opacity:.7}}
  .body{{padding:24px 28px}}
  .section{{margin-bottom:20px}}
  .section-title{{font-size:12px;font-weight:700;color:{GRAY};text-transform:uppercase;
                  letter-spacing:.5px;margin-bottom:10px;padding-bottom:6px;
                  border-bottom:1px solid #e2e8f0}}
  .item{{display:flex;align-items:flex-start;gap:10px;padding:10px 0;
         border-bottom:1px solid #f1f5f9}}
  .item:last-child{{border-bottom:none}}
  .ico{{font-size:18px;flex-shrink:0;margin-top:1px}}
  .item-main{{flex:1}}
  .item-title{{font-weight:600;font-size:14px;color:#1e293b;margin-bottom:2px}}
  .item-desc{{font-size:12px;color:{GRAY}}}
  .badge{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;
          font-weight:700;margin-left:6px}}
  .badge-red{{background:#fee2e2;color:#dc2626}}
  .badge-yellow{{background:#fef3c7;color:#d97706}}
  .badge-green{{background:#dcfce7;color:#16a34a}}
  .badge-blue{{background:#dbeafe;color:#2563eb}}
  .deadline{{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;
             padding:12px 14px;margin-bottom:8px}}
  .deadline .dl-label{{font-size:11px;color:#ea580c;font-weight:700;margin-bottom:4px}}
  .deadline .dl-val{{font-size:14px;font-weight:700;color:#1e293b}}
  .cta{{text-align:center;padding:20px 0 4px}}
  .btn{{display:inline-block;background:{CRIMSON};color:#fff;padding:12px 28px;
        border-radius:8px;text-decoration:none;font-weight:700;font-size:14px}}
  .footer{{background:#f8fafc;padding:16px 28px;font-size:11px;color:{GRAY};text-align:center;
           border-top:1px solid #e2e8f0}}
  @media(max-width:600px){{.body{{padding:16px}}.header{{padding:20px 16px}}}}
</style></head>
<body>
<div class="card">
  <div class="header">
    <h1>🎓 EMS — ระบบจัดการข้อสอบ</h1>
    {f'<div class="sub">{title}</div>' if title else ''}
  </div>
  <div class="body">{body}</div>
  <div class="footer">
    คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่<br>
    <a href="{APP_URL}" style="color:{CRIMSON}">เข้าสู่ระบบ EMS</a>
  </div>
</div>
</body></html>"""


def _send(to: List[str], subject: str, body_html: str) -> bool:
    """Core send — no-op if SMTP not configured"""
    if not to:
        return False
    if not ENABLED:
        log.info(f"[EMAIL STUB] To={to} | {subject}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"EMS คณะรัฐศาสตร์ฯ <{FROM_ADDR}>"
        msg["To"]      = ", ".join(to)
        msg.attach(MIMEText(body_html, "html", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        log.info(f"Email sent → {to} | {subject}")
        return True
    except Exception as e:
        log.error(f"Email failed → {to} | {e}")
        return False


# ══════════════════════════════════════════════════════════════
# ① IMMEDIATE NOTIFICATIONS
# ══════════════════════════════════════════════════════════════

def notify_submission_approved(teacher_email, teacher_name, course_id, section_no, exam_type):
    et = "ปลายภาค" if exam_type == "final" else "กลางภาค"
    body = f"""
    <div class="section">
      <div class="item">
        <span class="ico">✅</span>
        <div class="item-main">
          <div class="item-title">{course_id} ตอน {section_no} ({et}) — อนุมัติแล้ว</div>
          <div class="item-desc">ข้อสอบของท่านได้รับการอนุมัติจาก Admin เรียบร้อยแล้ว</div>
        </div>
      </div>
    </div>
    <div class="cta"><a href="{APP_URL}" class="btn">ดูสถานะใน EMS</a></div>
    """
    return _send([teacher_email],
                 f"[EMS] ✅ อนุมัติแล้ว — {course_id} ตอน {section_no} ({et})",
                 _html_wrap(body, f"เรียน {teacher_name}"))


def notify_submission_rejected(teacher_email, teacher_name, course_id, section_no, exam_type, reason):
    et = "ปลายภาค" if exam_type == "final" else "กลางภาค"
    body = f"""
    <div class="section">
      <div class="item">
        <span class="ico">❌</span>
        <div class="item-main">
          <div class="item-title">{course_id} ตอน {section_no} ({et}) — ต้องแก้ไข</div>
          <div class="item-desc" style="color:#dc2626">{reason}</div>
        </div>
      </div>
    </div>
    <div class="cta"><a href="{APP_URL}" class="btn">แก้ไขใน EMS</a></div>
    """
    return _send([teacher_email],
                 f"[EMS] ❌ ต้องแก้ไข — {course_id} ตอน {section_no} ({et})",
                 _html_wrap(body, f"เรียน {teacher_name}"))


def notify_swap_request(target_email, target_name, requester_name,
                        course_id, exam_date, exam_time, room_name, swap_id):
    body = f"""
    <div class="section">
      <div class="item">
        <span class="ico">🔄</span>
        <div class="item-main">
          <div class="item-title">{requester_name} ขอสลับคุมสอบกับท่าน</div>
          <div class="item-desc">📅 {exam_date} · ⏰ {exam_time} · 🏛️ {room_name} · วิชา {course_id}</div>
        </div>
      </div>
    </div>
    <div class="cta"><a href="{APP_URL}" class="btn">ตอบรับ / ปฏิเสธ</a></div>
    """
    return _send([target_email],
                 f"[EMS] 🔄 {requester_name} ขอสลับคุมสอบ — {exam_date} {exam_time}",
                 _html_wrap(body, f"เรียน {target_name}"))


def notify_swap_responded(requester_email, requester_name, target_name,
                          response: str, exam_date, exam_time):
    accepted = response == "accepted"
    ico  = "✅" if accepted else "❌"
    verb = "รับ" if accepted else "ปฏิเสธ"
    body = f"""
    <div class="section">
      <div class="item">
        <span class="ico">{ico}</span>
        <div class="item-main">
          <div class="item-title">{target_name} {verb}คำขอสลับคุมสอบ</div>
          <div class="item-desc">📅 {exam_date} · ⏰ {exam_time}</div>
        </div>
      </div>
    </div>
    <div class="cta"><a href="{APP_URL}" class="btn">ดูตารางคุมสอบ</a></div>
    """
    return _send([requester_email],
                 f"[EMS] {ico} {target_name}{verb}การสลับ — {exam_date}",
                 _html_wrap(body, f"เรียน {requester_name}"))


def notify_confirm_manager(teacher_email, teacher_name, proposer_name,
                            course_id, section_no, exam_type):
    et = "ปลายภาค" if exam_type == "final" else "กลางภาค"
    body = f"""
    <div class="section">
      <div class="item">
        <span class="ico">🎯</span>
        <div class="item-main">
          <div class="item-title">{proposer_name} เสนอให้ท่านรับผิดชอบ {course_id} ตอน {section_no} ({et})</div>
          <div class="item-desc">กรุณายืนยันหรือปฏิเสธการรับผิดชอบ</div>
        </div>
      </div>
    </div>
    <div class="cta"><a href="{APP_URL}" class="btn">ยืนยัน / ปฏิเสธ</a></div>
    """
    return _send([teacher_email],
                 f"[EMS] 🎯 รอยืนยัน — รับผิดชอบ {course_id} ({et})",
                 _html_wrap(body, f"เรียน {teacher_name}"))


# ══════════════════════════════════════════════════════════════
# ② DAILY DIGEST — ส่งทุกวัน (ถ้ามีรายการ)
# ══════════════════════════════════════════════════════════════

def send_daily_digest(db, today: date = None):
    """
    ส่ง digest ทุกคนตามบทบาท ทุกวันที่มีการเปลี่ยนแปลง
    เรียกจาก cron ทุกวัน 17:00 หรือ 08:00
    """
    if today is None:
        today = date.today()

    # import models ใน function เพื่อหลีกเลี่ยง circular import
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import models
    from sqlalchemy import func as sqlfunc

    sent = 0

    # ─── 1. TEACHERS: pending actions + deadlines ────────────
    teachers = db.query(models.User).filter(
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True,
        models.User.email.isnot(None),
    ).all()

    for teacher in teachers:
        sections = db.query(models.Section).filter(
            models.Section.teacher_id == teacher.id
        ).all()
        if not sections:
            continue

        pending_items = []
        deadline_items = []

        for sec in sections:
            sub = db.query(models.ExamSubmission).filter(
                models.ExamSubmission.section_id == sec.id
            ).first()
            course_label = f"{sec.course.course_id} ตอน {sec.section_no}" if sec.course else f"section {sec.id}"

            if not sub or not sub.exam_format_confirmed:
                pending_items.append({"ico":"📋","title":f"{course_label}","desc":"ยังไม่ได้กำหนดรูปแบบการสอบ"})
            elif sub.exam_type_choice == "onsite":
                if not sub.has_uploaded_pdf:
                    pending_items.append({"ico":"📄","title":f"{course_label}","desc":"ยังไม่ได้อัปโหลดไฟล์ข้อสอบ"})
                if not sub.print_spec_confirmed:
                    pending_items.append({"ico":"🖨️","title":f"{course_label}","desc":"ยังไม่ได้กำหนดสเปคพิมพ์"})
            if sub and sub.status == "rejected":
                pending_items.append({"ico":"❌","title":f"{course_label}","desc":f"ถูกปฏิเสธ: {sub.rejected_reason or '—'}"})

        # หา deadline จาก settings
        settings = {s.key: s.value for s in db.query(models.SystemSetting).all()}
        dl_days = int(settings.get("exam_format_deadline", "7"))
        schedules = db.query(models.ExamSchedule).join(models.Section).filter(
            models.Section.teacher_id == teacher.id
        ).all()
        for sch in schedules:
            if not sch.exam_date:
                continue
            days_left = (sch.exam_date - today).days
            if 0 < days_left <= dl_days:
                deadline_items.append({
                    "label": f"ข้อสอบ {sch.section.course.course_id if sch.section and sch.section.course else '?'}",
                    "val": f"อีก {days_left} วัน ({sch.exam_date.strftime('%d/%m/%Y')})"
                })

        if not pending_items and not deadline_items:
            continue

        body = ""
        if pending_items:
            body += '<div class="section"><div class="section-title">📌 รายการที่ต้องดำเนินการ</div>'
            for item in pending_items:
                body += f'<div class="item"><span class="ico">{item["ico"]}</span><div class="item-main"><div class="item-title">{item["title"]}</div><div class="item-desc">{item["desc"]}</div></div></div>'
            body += '</div>'
        if deadline_items:
            body += '<div class="section"><div class="section-title">⏰ Deadline ใกล้ถึง</div>'
            for dl in deadline_items:
                body += f'<div class="deadline"><div class="dl-label">{dl["label"]}</div><div class="dl-val">{dl["val"]}</div></div>'
            body += '</div>'
        body += f'<div class="cta"><a href="{APP_URL}" class="btn">เข้าสู่ระบบ EMS</a></div>'

        if _send([teacher.email],
                 f"[EMS] 📋 สรุปงานค้างของท่าน — {today.strftime('%d/%m/%Y')}",
                 _html_wrap(body, f"เรียน {teacher.full_name or teacher.username}")):
            sent += 1

    # ─── 2. STAFF: swap summary + tomorrow exam ──────────────
    staff_users = db.query(models.User).filter(
        models.User.role == models.UserRole.staff,
        models.User.is_active == True,
        models.User.email.isnot(None),
    ).all()

    tomorrow = today + timedelta(days=1)

    for staff in staff_users:
        items_today = []

        # swap requests pending
        pending_swaps = db.query(models.SwapRequest).filter(
            models.SwapRequest.target_id == staff.id,
            models.SwapRequest.status == "pending",
        ).count()
        if pending_swaps > 0:
            items_today.append({"ico":"🔄","title":f"คำขอสลับรอการตอบรับ {pending_swaps} รายการ","desc":"กรุณาตอบรับหรือปฏิเสธใน EMS"})

        # accepted swaps today
        accepted_today = db.query(models.SwapRequest).filter(
            models.SwapRequest.requester_id == staff.id,
            models.SwapRequest.status == "accepted",
        ).count()
        if accepted_today > 0:
            items_today.append({"ico":"✅","title":f"สลับที่ได้รับการอนุมัติแล้ว {accepted_today} รายการ","desc":""})

        # exam tomorrow
        tomorrow_scheds = db.query(models.ExamSchedule).join(models.Supervision).filter(
            models.Supervision.user_id == staff.id,
            models.ExamSchedule.exam_date == tomorrow,
        ).all()

        if not items_today and not tomorrow_scheds:
            continue

        body = ""
        if items_today:
            body += '<div class="section"><div class="section-title">📌 สรุปวันนี้</div>'
            for item in items_today:
                body += f'<div class="item"><span class="ico">{item["ico"]}</span><div class="item-main"><div class="item-title">{item["title"]}</div><div class="item-desc">{item["desc"]}</div></div></div>'
            body += '</div>'

        if tomorrow_scheds:
            body += '<div class="section"><div class="section-title">📅 สอบพรุ่งนี้ — รายละเอียด</div>'
            for sch in tomorrow_scheds:
                sup = db.query(models.Supervision).filter(
                    models.Supervision.schedule_id == sch.id,
                    models.Supervision.user_id == staff.id,
                ).first()
                role_th = {"room_keeper":"🔑 ดูแลห้อง","distributor":"📦 กระจายข้อสอบ"}.get(
                    sup.role_in_exam if sup else "", "👮 คุมสอบ")
                sups_names = ", ".join(
                    sv.user.full_name for sv in (sch.supervisions or [])
                    if sv.user and sv.user.id != staff.id
                ) or "—"
                body += f"""
                <div style="background:#f8fafc;border-radius:8px;padding:14px;margin-bottom:10px;border-left:3px solid {CRIMSON}">
                  <div style="font-weight:700;font-size:15px;color:{NAVY}">{sch.section.course.course_id if sch.section and sch.section.course else '?'} ตอน {sch.section.section_no if sch.section else '?'}</div>
                  <div style="font-size:13px;color:{GRAY};margin-top:4px">{sch.section.course.course_name_th if sch.section and sch.section.course else ''}</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;font-size:13px">
                    <div>📅 <b>{tomorrow.strftime('%d/%m/%Y')}</b></div>
                    <div>⏰ <b>{sch.exam_time or '?'}</b></div>
                    <div>🏛️ <b>{sch.room.room_name if sch.room else '?'}</b></div>
                    <div>👥 <b>{sch.section.num_students if sch.section else 0} คน</b></div>
                  </div>
                  <div style="margin-top:8px;font-size:12px">
                    <span style="background:{CRIMSON}22;color:{CRIMSON};padding:3px 10px;border-radius:12px;font-weight:700">{role_th}</span>
                  </div>
                  <div style="font-size:12px;color:{GRAY};margin-top:8px">กรรมการร่วม: {sups_names}</div>
                </div>"""
            body += '</div>'

        body += f'<div class="cta"><a href="{APP_URL}" class="btn">เข้าสู่ EMS</a></div>'
        if _send([staff.email],
                 f"[EMS] {'⚠️ มีคุมสอบพรุ่งนี้ · ' if tomorrow_scheds else ''}สรุป {today.strftime('%d/%m/%Y')}",
                 _html_wrap(body, f"เรียน {staff.full_name or staff.username}")):
            sent += 1

    # ─── 3. ADMIN: daily overview ────────────────────────────
    admins = db.query(models.User).filter(
        models.User.role == models.UserRole.admin,
        models.User.is_active == True,
        models.User.email.isnot(None),
    ).all()

    pending_subs = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.status == "submitted"
    ).count()
    pending_swaps_all = db.query(models.SwapRequest).filter(
        models.SwapRequest.status == "pending"
    ).count()
    tomorrow_exams = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.exam_date == tomorrow
    ).count()

    if admins and (pending_subs or pending_swaps_all or tomorrow_exams):
        body = f"""
        <div class="section">
          <div class="section-title">📊 สรุปภาพรวมประจำวัน — {today.strftime('%d/%m/%Y')}</div>
          <div class="item"><span class="ico">📤</span><div class="item-main">
            <div class="item-title">ข้อสอบรอตรวจสอบ <span class="badge {'badge-yellow' if pending_subs else 'badge-blue'}">{pending_subs} รายการ</span></div>
          </div></div>
          <div class="item"><span class="ico">🔄</span><div class="item-main">
            <div class="item-title">คำขอสลับรอดำเนินการ <span class="badge {'badge-yellow' if pending_swaps_all else 'badge-blue'}">{pending_swaps_all} รายการ</span></div>
          </div></div>
          <div class="item"><span class="ico">📅</span><div class="item-main">
            <div class="item-title">สอบพรุ่งนี้ <span class="badge badge-blue">{tomorrow_exams} วิชา</span></div>
          </div></div>
        </div>
        <div class="cta"><a href="{APP_URL}" class="btn">จัดการใน EMS</a></div>
        """
        for admin in admins:
            if _send([admin.email],
                     f"[EMS] 📊 สรุปประจำวัน — {today.strftime('%d/%m/%Y')}",
                     _html_wrap(body, f"เรียน {admin.full_name or admin.username}")):
                sent += 1

    log.info(f"Daily digest sent: {sent} emails")
    return sent


# ══════════════════════════════════════════════════════════════
# ③ EXAM DAY REMINDER — 1 วันก่อนสอบ
# ══════════════════════════════════════════════════════════════

def send_exam_reminders(db, target_date: date = None):
    """
    แจ้ง staff + teacher ทุกคนที่มีสอบพรุ่งนี้
    เรียกจาก cron ทุกวัน 16:00 (วันก่อนสอบ)
    """
    import models

    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    schedules = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.exam_date == target_date
    ).all()

    if not schedules:
        log.info(f"No exams on {target_date} — skip reminders")
        return 0

    notified = set()
    sent = 0

    for sch in schedules:
        sec    = sch.section
        course = sec.course if sec else None
        room   = sch.room

        course_id   = course.course_id    if course else "?"
        course_name = course.course_name_th if course else ""
        section_no  = sec.section_no      if sec    else "?"
        num_students= sec.num_students    if sec    else 0
        exam_time   = sch.exam_time       or "?"
        room_name   = room.room_name      if room   else "?"

        # หา supervisions ทั้งหมดของ schedule นี้
        all_sups = sch.supervisions or []
        sup_list = ", ".join(
            f"{sv.user.full_name}" for sv in all_sups if sv.user
        )

        for sv in all_sups:
            if not sv.user or not sv.user.email:
                continue
            if sv.user_id in notified:
                continue
            notified.add(sv.user_id)

            role_th = {
                "room_keeper": "🔑 ดูแลห้องสอบ",
                "distributor": "📦 กระจายข้อสอบ",
                "supervisor":  "👮 คุมสอบ",
            }.get(sv.role_in_exam or "supervisor", "👮 คุมสอบ")

            others = ", ".join(
                s.user.full_name for s in all_sups
                if s.user and s.user_id != sv.user_id
            ) or "—"

            body = f"""
            <div style="background:linear-gradient(135deg,{NAVY},{NAVY}dd);color:#fff;
              border-radius:10px;padding:20px;margin-bottom:20px;text-align:center">
              <div style="font-size:36px;margin-bottom:8px">📋</div>
              <div style="font-size:20px;font-weight:800">มีสอบพรุ่งนี้!</div>
              <div style="font-size:14px;opacity:.8;margin-top:4px">
                {target_date.strftime('%A %d %B %Y').replace('Monday','วันจันทร์').replace('Tuesday','วันอังคาร').replace('Wednesday','วันพุธ').replace('Thursday','วันพฤหัสบดี').replace('Friday','วันศุกร์').replace('Saturday','วันเสาร์').replace('Sunday','วันอาทิตย์')}
              </div>
            </div>
            <div style="background:#f8fafc;border-radius:10px;padding:20px;margin-bottom:16px">
              <div style="font-weight:800;font-size:18px;color:{NAVY};margin-bottom:4px">
                {course_id} — {course_name}
              </div>
              <div style="color:{GRAY};font-size:14px;margin-bottom:16px">ตอนที่ {section_no}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div style="background:#fff;border-radius:8px;padding:12px;text-align:center">
                  <div style="font-size:20px">⏰</div>
                  <div style="font-weight:700;font-size:16px;color:{NAVY};margin-top:4px">{exam_time}</div>
                  <div style="font-size:11px;color:{GRAY}">เวลาสอบ</div>
                </div>
                <div style="background:#fff;border-radius:8px;padding:12px;text-align:center">
                  <div style="font-size:20px">🏛️</div>
                  <div style="font-weight:700;font-size:16px;color:{NAVY};margin-top:4px">{room_name}</div>
                  <div style="font-size:11px;color:{GRAY}">ห้องสอบ</div>
                </div>
                <div style="background:#fff;border-radius:8px;padding:12px;text-align:center">
                  <div style="font-size:20px">👥</div>
                  <div style="font-weight:700;font-size:16px;color:{NAVY};margin-top:4px">{num_students}</div>
                  <div style="font-size:11px;color:{GRAY}">ผู้เข้าสอบ</div>
                </div>
                <div style="background:#fff;border-radius:8px;padding:12px;text-align:center">
                  <div style="font-size:20px">{role_th.split()[0]}</div>
                  <div style="font-weight:700;font-size:13px;color:{NAVY};margin-top:4px">{' '.join(role_th.split()[1:])}</div>
                  <div style="font-size:11px;color:{GRAY}">บทบาท</div>
                </div>
              </div>
              <div style="margin-top:14px;padding:10px;background:#fff;border-radius:8px;font-size:13px">
                <span style="color:{GRAY}">กรรมการร่วม:</span>
                <span style="font-weight:600;color:{NAVY}">{others}</span>
              </div>
            </div>
            <div class="cta"><a href="{APP_URL}" class="btn">ดูรายละเอียดใน EMS</a></div>
            """

            if _send([sv.user.email],
                     f"[EMS] 📋 แจ้งเตือน — สอบพรุ่งนี้ {exam_time} ห้อง {room_name}",
                     _html_wrap(body, f"เรียน {sv.user.full_name or sv.user.username}")):
                sent += 1

        # แจ้ง teacher เจ้าของวิชาด้วย (ถ้ายังไม่ได้แจ้ง)
        if sec and sec.teacher and sec.teacher.email and sec.teacher_id not in notified:
            teacher = sec.teacher
            notified.add(teacher.id)
            body_t = f"""
            <div class="section">
              <div class="item">
                <span class="ico">📚</span>
                <div class="item-main">
                  <div class="item-title">วิชา {course_id} ตอน {section_no} — สอบพรุ่งนี้</div>
                  <div class="item-desc">⏰ {exam_time} · 🏛️ {room_name} · 👥 {num_students} คน</div>
                  <div class="item-desc" style="margin-top:4px">กรรมการ: {sup_list or '—'}</div>
                </div>
              </div>
            </div>
            <div class="cta"><a href="{APP_URL}" class="btn">ดูรายละเอียด</a></div>
            """
            if _send([teacher.email],
                     f"[EMS] 📚 วิชาของท่านสอบพรุ่งนี้ — {course_id} {exam_time}",
                     _html_wrap(body_t, f"เรียน {teacher.full_name or teacher.username}")):
                sent += 1

    log.info(f"Exam reminders sent: {sent} emails for {target_date}")
    return sent
