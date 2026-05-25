# LARAVEL_OWNER_REQUEST_MEMO_TH_EN.md

**Date**: 2026-05-22
**Status**: READY TO SEND (recipient names and deadline are TBD)
**Audience**: Laravel owner and Faculty IT owner
**Language**: Thai first, then English (same intent)

---

## ภาษาไทย (Thai)

### เรื่อง
ขอข้อมูลสัญญาการยืนยันตัวตน (Auth Contract) ระหว่างระบบ EMS กับระบบ Laravel/CMU ของคณะ ก่อนเริ่มพัฒนา Auth Bridge

### เรียน
ผู้ดูแลระบบ Laravel ของคณะ และผู้รับผิดชอบด้าน IT

### บริบท
ระบบ EMS (Exam Management System) อยู่ระหว่างการเตรียมใช้งานบน Faculty LAN และจำเป็นต้องเชื่อมต่อกับระบบยืนยันตัวตนของคณะอย่างปลอดภัย

ในขณะนี้ EMS ยังใช้การเข้าสู่ระบบภายในระบบเพื่อการทดสอบเท่านั้น และยังไม่สามารถเริ่มพัฒนา Auth Bridge ได้จนกว่าจะยืนยันรายละเอียดจากโค้ด Laravel จริง

### สิ่งที่ต้องการจากทีม Laravel/IT
กรุณาตรวจสอบและตอบข้อมูลตามเอกสารต่อไปนี้:

1. `docs/deployment/LARAVEL_OWNER_HANDOFF_CHECKLIST.md`
2. `docs/deployment/LARAVEL_AUTH_CONTRACT_QUESTIONS.md`

โดยเน้นการยืนยันจากโค้ดจริงของ Laravel ในหัวข้อ:

- callback route และ HTTP method
- โครงสร้าง session (`session("USS")` หรือ key ที่ใช้งานจริง)
- วิธี validate token (`cmu_at` หรือ artifact อื่น)
- cookie/session policy (Domain, SameSite, Secure, HttpOnly)
- logout behavior
- EMS mount path และ reverse proxy path
- DB/deployment ownership และ security constraints

### ข้อกำหนดสำคัญ

- กรุณาอย่าส่ง secret จริงหรือ token จริงในอีเมล/เอกสาร
- ใช้ข้อมูลตัวอย่างที่ sanitize แล้วเท่านั้น
- รายการใดที่ยังไม่ยืนยัน ให้คงสถานะ `OPEN`
- อย่า mark `COMPLETE` หากยังไม่มีหลักฐานจากโค้ดจริง

### กำหนดส่ง (TBD)
- Deadline: `[TBD]`
- ช่องทางส่งกลับ: `[TBD]`
- ผู้ประสานงาน EMS: `[TBD]`

ขอบคุณครับ/ค่ะ
ทีม EMS

---

## English

### Subject
Request for Laravel/CMU authentication contract details before EMS Auth Bridge implementation

### To
Laravel owner and Faculty IT owner

### Context
EMS (Exam Management System) is preparing for Faculty LAN deployment and must integrate with the faculty authentication flow safely.

At this stage, EMS is using local demo authentication only. Auth Bridge implementation cannot begin until the Laravel contract is verified from real code evidence.

### Requested Inputs
Please review and respond using:

1. `docs/deployment/LARAVEL_OWNER_HANDOFF_CHECKLIST.md`
2. `docs/deployment/LARAVEL_AUTH_CONTRACT_QUESTIONS.md`

Please confirm, with code-backed evidence:

- callback route and HTTP method
- session payload structure (`session("USS")` or actual key)
- token validation path (`cmu_at` or other artifact)
- cookie/session policy (Domain, SameSite, Secure, HttpOnly)
- logout behavior
- EMS mount path and reverse proxy path
- DB/deployment ownership and security constraints

### Important Rules

- Do not share real secrets or raw production tokens.
- Provide sanitized examples only.
- Keep unresolved items as `OPEN`.
- Do not mark items `COMPLETE` without real code evidence.

### Timeline (TBD)
- Deadline: `[TBD]`
- Return channel: `[TBD]`
- EMS contact: `[TBD]`

Thank you,
EMS Team

---

**End of LARAVEL_OWNER_REQUEST_MEMO_TH_EN.md**
