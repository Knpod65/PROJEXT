# คู่มือติดตั้ง EMS จาก Git Clone สำหรับเครื่องใหม่

คู่มือนี้ใช้สำหรับการรัน EMS แบบ local development/demo เท่านั้น ไม่ใช่คู่มือ deploy สำหรับ pilot
หรือ production และห้ามใช้ค่าลับสำหรับ production ในสภาพแวดล้อมนี้

## 1. เครื่องมือที่ต้องมี

- Git
- Python ที่รองรับ dependencies ใน `backend/requirements.txt`
- Node.js และ npm
- PowerShell บน Windows

เวอร์ชันที่ตรวจว่าสามารถรัน session วันที่ 2026-06-15 ได้คือ Python `3.14.3`, Node.js `v24.15.0`,
npm `11.12.1`, และ Git `2.53.0.windows.2` เวอร์ชันเหล่านี้เป็นหลักฐานของเครื่องที่ทดสอบ ไม่ใช่
ข้อกำหนด version pin ของ repository

ตรวจเวอร์ชัน:

```powershell
py --version
node --version
npm --version
git --version
```

### หมายเหตุเรื่องฟอนต์เอกสารภาษาไทย

การเปิดไฟล์ XLSX ภาษาไทยให้ได้หน้าตาใกล้เคียงเอกสารทางการควรติดตั้งฟอนต์ `TH Sarabun New`, `Sarabun`, หรือ `Noto Sans Thai` บนเครื่องที่เปิดไฟล์
ระบบจะบันทึกข้อความภาษาไทยเป็น UTF-8 และกำหนดชื่อฟอนต์ใน workbook แต่ XLSX ไม่ฝังไฟล์ฟอนต์ไว้ในเอกสาร

สำหรับ PDF ระบบจะใช้ฟอนต์ภาษาไทยที่ติดตั้งอยู่ในเครื่องเท่านั้น หากไม่มีฟอนต์ที่ฝังได้ ระบบจะ fallback เป็น Helvetica และต้องไม่ถือว่าเป็นหลักฐานผ่านการตรวจภาพ PDF ภาษาไทย
ห้าม commit ไฟล์ฟอนต์ลิขสิทธิ์หรือฟอนต์จากเครื่อง local เข้า repository

## 2. Clone และตรวจสอบ repository

```powershell
git clone https://github.com/Knpod65/PROJEXT.git
cd PROJEXT\opt\ems_system
git status --short --branch
git pull --ff-only origin main
```

ต้องตรวจว่าอยู่บน `main` และ worktree สะอาดก่อนเริ่มติดตั้ง

## 3. ติดตั้ง Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

สำหรับ local demo สามารถใช้ environment แบบ development โดยไม่กำหนด `DATABASE_URL`; ระบบจะใช้
SQLite ที่ `backend\ems.db` และ startup จะสร้าง schema/seed ข้อมูล development ตามโค้ดปัจจุบัน
เท่านั้น ห้ามใช้ fallback นี้สำหรับ pilot หรือ production

ใช้ `backend\.env.example` เป็นรายการอ้างอิงของตัวแปรที่รองรับ แต่ direct startup command ไม่ได้
โหลดไฟล์ `.env.local` ให้อัตโนมัติ หากต้องกำหนดค่า local เพิ่มเติม ให้ตั้ง environment variable
ใน PowerShell session หรือใช้ secret-management tooling ที่ได้รับอนุมัติ และห้าม commit secret:

```powershell
$env:ENVIRONMENT = "development"
# ตั้งค่า local variable อื่นเฉพาะที่จำเป็น ห้ามใช้หรือบันทึก production secret
```

environment variable ที่ตั้งใน PowerShell จะถูกส่งต่อไปยัง backend process ที่ start จาก session
นั้น

## 4. ติดตั้ง Frontend

```powershell
cd frontend
npm ci
cd ..
```

Vite local development ใช้ `/api` ผ่าน proxy ไปยัง `http://127.0.0.1:8000` และไม่ต้องมี frontend
environment file สำหรับการรันแบบมาตรฐานนี้

## 5. ตรวจ port ก่อน start

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,3000 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress,LocalPort,OwningProcess
```

หาก port ถูกใช้งาน ให้ตรวจ executable และ command line ของ PID ก่อน ห้ามหยุด process ที่ไม่ทราบ
เจ้าของ

## 6. Start Backend และ Frontend

รันจาก repository root:

```powershell
$root = (Get-Location).Path

Start-Process -FilePath "$root\backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","main:app","--host","127.0.0.1","--port","8000" `
  -WorkingDirectory "$root\backend" -WindowStyle Hidden `
  -RedirectStandardOutput "$root\backend-local-session.out.log" `
  -RedirectStandardError "$root\backend-local-session.err.log"

Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev" `
  -WorkingDirectory "$root\frontend" -WindowStyle Hidden `
  -RedirectStandardOutput "$root\frontend-local-session.out.log" `
  -RedirectStandardError "$root\frontend-local-session.err.log"
```

ไฟล์ log เหล่านี้ถูก ignore และห้าม commit

## 7. ตรวจสอบการทำงาน

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/
```

เปิด `http://127.0.0.1:3000` เลือกบทบาท และเข้าสู่ระบบด้วยบัญชี local demo ที่ได้รับอนุญาตจาก
ผู้ดูแลระบบ ห้ามบันทึกรหัสผ่านในเอกสารหรือ Git

เส้นทางหลักสำหรับ reviewer:

- `/dashboard`
- `/invigilation-payment-document-draft`
- `/payment-document-settings`
- `/invigilation-advance-batch-preview`

## 8. ปิดระบบอย่างปลอดภัย

```powershell
$backendPid = (Get-NetTCPConnection -State Listen -LocalPort 8000).OwningProcess
$frontendPid = (Get-NetTCPConnection -State Listen -LocalPort 3000).OwningProcess

Get-CimInstance Win32_Process -Filter "ProcessId=$backendPid" |
  Select-Object ProcessId,Name,CommandLine
Get-CimInstance Win32_Process -Filter "ProcessId=$frontendPid" |
  Select-Object ProcessId,Name,CommandLine

# หยุดเฉพาะเมื่อยืนยันแล้วว่าเป็น Uvicorn/Vite ของ repository นี้
Stop-Process -Id $backendPid -ErrorAction Stop
Stop-Process -Id $frontendPid -ErrorAction Stop
```

## Troubleshooting

- Backend ไม่ start: ตรวจ `backend-local-session.err.log`, Python environment, dependencies, และ
  local environment configuration
- Frontend ไม่ start: ตรวจ `frontend-local-session.err.log`, `npm ci`, และ port `3000`
- API health ไม่ผ่าน: ตรวจว่า listener port `8000` เป็น Uvicorn ของ repository นี้
- Database schema ไม่ตรง: หยุดระบบ สำรอง database และใช้ migration ที่ระบุสำหรับ commit ปัจจุบัน
  เท่านั้น ห้ามรัน migration scripts ทั้งหมดแบบสุ่ม
- ห้ามอ้างว่า local demo ผ่านแล้วเท่ากับพร้อม pilot หรือ production
