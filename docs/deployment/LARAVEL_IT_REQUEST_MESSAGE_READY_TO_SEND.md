# LARAVEL_IT_REQUEST_MESSAGE_READY_TO_SEND.md

**Date**: 2026-05-25

---

## Thai Version (ส่งให้เจ้าของระบบ Laravel / IT Faculty)

**เรื่อง:** ขอความร่วมมือยืนยันสัญญาการยืนยันตัวตน (Auth Contract) ระหว่าง EMS กับระบบ Laravel / POLSCI OAuth

เรียน เจ้าของระบบ Laravel / ทีม IT คณะรัฐศาสตร์และรัฐประศาสนศาสตร์

ปัจจุบันระบบ EMS (Exam Management System) ของคณะฯ ได้ผ่านการทดสอบแบบ standalone อย่างสมบูรณ์ (Demo Readiness 98/100) โดยมีผู้ใช้ทดสอบจริงผ่านเบราว์เซอร์ 4 บทบาทหลัก (admin, esq_head, print_shop, teacher) และทุก flow หลักทำงานได้ตามที่ออกแบบไว้

อย่างไรก็ตาม เพื่อให้สามารถนำ EMS ไปใช้งานจริงบน Faculty LAN ได้ เราต้องการยืนยันรายละเอียดของการยืนยันตัวตนผ่านระบบ Laravel / POLSCI OAuth ที่คณะฯ ใช้อยู่ก่อน

**สิ่งที่เราต้องการให้ช่วยยืนยัน (สำคัญมาก)**

1. โครงสร้างของ payload ที่ EMS จะได้รับหลังจากผู้ใช้ login ผ่าน Laravel (โดยเฉพาะ session("USS"), cmu_at, และฟิลด์อีเมล CMU)
2. วิธีที่ EMS ควรเรียก callback / ServiceUrl
3. ควร mount EMS ไว้ที่ path ใดบน Faculty LAN
4. กลยุทธ์สำหรับผู้ใช้ print-shop ที่ไม่มีบัญชี CMU
5. เป้าหมาย PostgreSQL ที่ EMS ควรใช้ และผู้รับผิดชอบ backup/restore
6. พฤติกรรมการ logout (single sign-out หรือแยกกัน)

**เอกสารแนบ (กรุณาตรวจสอบ)**

- LARAVEL_AUTH_CONTRACT_QUESTIONS.md (คำถามละเอียด 203 ข้อ)
- LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md
- LARAVEL_OWNER_REQUEST_PACKAGE.md
- LARAVEL_OWNER_HANDOFF_CHECKLIST.md
- LARAVEL_AUTH_CONTRACT_COMPLETENESS_CHECKLIST.md
- POLSCI_OAUTH_FLOW_ANALYSIS.md
- FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md
- HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md

**ข้อควรระวังด้านความปลอดภัย**
- กรุณาอย่าส่งข้อมูลลับจริง (secret, token, password)
- ส่งเฉพาะโครงสร้างและตัวอย่างที่ sanitize แล้ว
- หากต้องการประชุมสั้นเพื่ออธิบายเพิ่มเติม กรุณาติดต่อกลับได้ทันที

เราขอรับคำตอบภายใน 2 สัปดาห์ เพื่อจะได้วางแผนขั้นตอนต่อไปได้

ขอบคุณมากสำหรับความร่วมมือ

ด้วยความเคารพ  
ทีม EMS  
คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่

---

## English Version (for reference / English-speaking stakeholders)

**Subject:** Request for Verification of EMS – Laravel / POLSCI OAuth Authentication Contract

Dear Laravel System Owner / Faculty IT Team,

The EMS (Exam Management System) has successfully completed standalone interactive testing (Demo Readiness 98/100) with real browser testing across four primary roles. All core operational and intelligence workflows have been validated.

To proceed toward a controlled Faculty LAN pilot, we need verified details of the current Laravel / POLSCI OAuth authentication flow that the Faculty uses.

**Critical items we need confirmed:**

1. Structure of the identity payload EMS will receive after login (especially session("USS"), cmu_at, and the CMU email field)
2. Callback / ServiceUrl behavior expected by the Laravel side
3. Recommended mount path / ServiceUrl for EMS on the Faculty LAN
4. Strategy for non-CMU users (print-shop external accounts)
5. Target PostgreSQL instance for EMS and the owner of backup/restore
6. Logout behavior (single sign-out vs separate sessions)

**Attached documents (please review):**

- LARAVEL_AUTH_CONTRACT_QUESTIONS.md (detailed 203 questions)
- LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md
- LARAVEL_OWNER_REQUEST_PACKAGE.md
- LARAVEL_OWNER_HANDOFF_CHECKLIST.md
- LARAVEL_AUTH_CONTRACT_COMPLETENESS_CHECKLIST.md
- POLSCI_OAUTH_FLOW_ANALYSIS.md
- FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md
- HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md

**Security note:**
- Please do not send real secrets, tokens, or passwords.
- Sanitized structure and examples are sufficient.
- We are happy to schedule a short call if verbal clarification would help.

We would greatly appreciate receiving answers within two weeks so we can plan the next steps responsibly.

Thank you for your support.

Best regards,  
EMS Team  
Faculty of Political Science and Public Administration  
Chiang Mai University

---
*Use the Thai version for primary dispatch. Keep English for reference.*
