# UAT Test Script — EMS Exam Management System

> Version: 2026-05-20  
> Target: Pilot Users + QA Team  
> Purpose: Verify system functionality before production rollout

---

## Pre-Test Setup

```bash
# 1. Ensure system is running
curl http://localhost/health
# Expected: {"status": "ok", "db": "connected"}

# 2. Login credentials (from seed data)
# Admin: mathawee.m / admin123
# Teacher: pailin.phu / teacher123
# Student: 640610001 / (ask admin for temp password)
```

---

## Test Scenarios

### TC-01: Authentication Flow

**Steps:**
1. Navigate to `http://localhost`
2. Login as admin (`mathawee.m` / `admin123`)
3. Verify redirect to dashboard
4. Click logout
5. Verify redirect to login page

**Expected:**
- [x] Login succeeds, dashboard loads
- [x] Session persists across navigation
- [x] Logout clears session
- [x] Token expiry handled (test after 12 hours or force-refresh)

---

### TC-02: Role-Based Access (Teacher)

**Steps:**
1. Login as `pailin.phu` / `teacher123`
2. Navigate to `/submissions`
3. Verify only own submissions shown
4. Navigate to `/swaps`
5. Verify only own sections' exams listed

**Expected:**
- [x] Teacher sees only their submissions
- [x] Teacher cannot see other teachers' schedules
- [x] Teacher cannot access admin pages (403 expected)

---

### TC-03: Role-Based Access (Student)

**Steps:**
1. Login as student `640610001`
2. Navigate to `/schedule`
3. Verify only own exam schedule shown
4. Try accessing `/admin` (should fail)

**Expected:**
- [x] Student sees only their schedule
- [x] 403 on admin route access
- [x] No PII leak in page source

---

### TC-04: Export Audit Logging

**Steps:**
1. Login as admin
2. Navigate to `/schedule`
3. Click "Export PDF"
4. Check audit logs: `GET /api/exports/audit-logs`

**Expected:**
- [x] Export succeeds
- [x] Audit log entry created with `export_schedule_pdf`
- [x] Metadata shows file_type, row_count (no PII)
- [x] IP stored as hash, not raw value

---

### TC-05: QR Check-in Flow

**Steps:**
1. Login as assigned staff
2. Navigate to `/checkin`
3. Scan test QR code
4. Verify check-in logged
5. Supervisor confirms check-in

**Expected:**
- [x] Check-in recorded with timestamp
- [x] Audit log: `CHECKIN_SUCCESS`
- [x] Confirm action logs `CHECKIN_CONFIRM`

---

### TC-06: Swap Request Flow

**Steps:**
1. Login as teacher `pailin.phu`
2. Navigate to `/swaps`
3. Create swap request for eligible exam
4. Check status shows "pending"

**Expected:**
- [x] Swap created successfully
- [x] Status = pending
- [x] Audit log created

---

### TC-07: Optimization Session

**Steps:**
1. Login as admin
2. Navigate to `/optimizer`
3. Click "Initialize Session"
4. Review flag count
5. Click "Sign Session"

**Expected:**
- [x] Session initialized
- [x] Flags displayed correctly
- [x] Session signed off
- [x] Audit logs: `INIT_OPTIMIZATION_SESSION`, `SIGN_OPTIMIZATION_SESSION`

---

### TC-08: Historical Snapshot Comparison

**Steps:**
1. Login as admin
2. Navigate to `/historical`
3. Select Semester 2/2568
4. Compare baseline vs final

**Expected:**
- [x] Snapshots load without error
- [x] Differences highlighted
- [x] No data corruption in comparison view

---

### TC-09: Thai/English Language Toggle

**Steps:**
1. On any page, click language toggle
2. Verify UI text changes
3. Navigate between pages

**Expected:**
- [x] Thai text displays correctly
- [x] English text displays correctly
- [x] Preference persists in session

---

### TC-10: Error Handling

**Steps:**
1. Logout
2. Try accessing `/api/submissions/` without auth
3. Try accessing `/api/users/` as teacher
4. Try invalid URL

**Expected:**
- [x] 401 on unauthenticated request (redirect to login)
- [x] 403 on unauthorized role access
- [x] 404 on invalid URL (no stack trace exposed)

---

## Test Results Table

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-01 | Authentication flow | ⬜ | |
| TC-02 | Role access (teacher) | ⬜ | |
| TC-03 | Role access (student) | ⬜ | |
| TC-04 | Export audit logging | ⬜ | |
| TC-05 | QR check-in flow | ⬜ | |
| TC-06 | Swap request flow | ⬜ | |
| TC-07 | Optimization session | ⬜ | |
| TC-08 | Historical snapshots | ⬜ | |
| TC-09 | Language toggle | ⬜ | |
| TC-10 | Error handling | ⬜ | |

---

## Post-Test Verification

```bash
# Verify audit logs created during test
curl -b cookies.txt http://localhost/api/exports/audit-logs \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'

# Count audit entries per type
curl -b cookies.txt http://localhost/api/exports/audit-logs/count-by-type
```

---

## Sign-off

| Tester | Role | Date | Signature |
|--------|------|------|-----------|
| | | | |
| | | | |
| | | | |