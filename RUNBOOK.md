# EMS — Local Setup & Runbook

## ⚡ Quickstart (SQLite, no Docker needed)

```bash
# 1. Enter the backend directory
cd opt/ems_system/backend

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (SQLite mode — no Postgres needed)
cp ../env.local ../.env
# Edit .env if needed — defaults work for local dev

# 5. Run the server with hot reload
uvicorn main:app --reload --port 8000

# 6. Open browser
open http://localhost:8000
```

Default login credentials (dev seed only — rotate before production):
| Role | Username | Password |
|------|----------|----------|
| Admin | `mathawee.m` | `admin123` |
| Admin | `atikant.s` | `admin123` |
| ESQ Head | `napaporn.ph` | `esq123` |
| Dept Supervisor | `phusanisa.sai` | `staff123` |
| Staff | `araya.fa` | `staff123` |
| Teacher | `pailin.phu` | `teacher123` |
| Print Shop | `printshop.ops` | `print123` |

---

## 🐳 Docker (with hot reload)

```bash
cd opt/ems_system

# Copy env template
cp .env.local .env

# Run with hot reload (mounts source code into container)
docker compose -f docker-compose.dev.yml up --build

# Logs
docker compose -f docker-compose.dev.yml logs -f app
```

---

## 🐳 Docker (production-like, with Postgres)

```bash
cd opt/ems_system

# Set secrets
cp .env.local .env
# EDIT .env:
#   ENV=production
#   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
#   CRON_SECRET=<run: python -c "import secrets; print(secrets.token_hex(16))">
#   POSTGRES_PASSWORD=<strong-password>

# Create required data directories
mkdir -p ../../data/postgres ../../data/uploads ../../data/logs/nginx ../../data/ssl

# Start all services
docker compose up --build -d

# Check health
curl http://localhost/health
```

---

## 🔧 Test Key Endpoints

```bash
BASE=http://localhost:8000

# Health check
curl $BASE/health

# Login (sets HttpOnly cookie)
curl -c cookies.txt -X POST $BASE/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"mathawee.m","password":"admin123"}'

# Get current user (uses cookie)
curl -b cookies.txt $BASE/api/auth/me

# List submissions (authenticated)
curl -b cookies.txt $BASE/api/submissions/

# Student schedule lookup (authenticated; student can only view their own record)
curl -b cookies.txt $BASE/api/public/schedule/student/640610001

# Audit logs (admin only)
curl -b cookies.txt $BASE/api/exports/audit-logs

# Logout
curl -b cookies.txt -X POST $BASE/api/auth/logout
```

---

## 🔒 Secret Generation

```bash
# SECRET_KEY (minimum 32 chars)
python -c "import secrets; print(secrets.token_hex(32))"

# CRON_SECRET
python -c "import secrets; print(secrets.token_hex(16))"

# POSTGRES_PASSWORD
python -c "import secrets; print(secrets.token_urlsafe(20))"
```

---

## ♻️ Restore Procedure

```bash
# Restore the latest PostgreSQL backup into a non-running stack
gunzip -c ../../data/backups/db/ems_db_<timestamp>.sql.gz | \
  docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

# Restore uploaded files snapshot
rsync -av ../../data/backups/files/ ../../data/uploads/
```

Validate restore before reopening the service:
- `curl http://localhost/health`
- `curl http://localhost/api/health/ready -H 'X-Internal-Health: 1'`

---

## 🏥 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pikepdf` | `pip install pikepdf` or ignore (graceful fallback exists) |
| `WeasyPrint` error on Windows | Install GTK runtime or use Docker |
| Port 8000 in use | Change port: `uvicorn main:app --port 8001` |
| Cookie not sent | Ensure `credentials: 'include'` in fetch (already set in js_script.js) |
| 401 on every request | Check `ALLOWED_ORIGINS` matches your browser URL |
| DB locked (SQLite) | Restart — SQLite WAL mode should prevent this |

---

## 📋 API Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | None | Login, sets session cookie |
| `/api/auth/me` | GET | Cookie/Bearer | Current user info |
| `/api/auth/logout` | POST | Cookie/Bearer | Logout, clears cookie |
| `/api/auth/view-as` | POST | Admin | Impersonate role |
| `/api/dashboard/` | GET | Any auth | Dashboard stats |
| `/api/schedule/` | GET | Any auth | Exam schedule |
| `/api/submissions/` | GET | Any auth | Exam submissions |
| `/api/submissions/{id}/messages` | GET/POST | Teacher/Admin | Submission messages |
| `/api/swaps2/` | GET/POST | Staff/Teacher | Swap requests |
| `/api/checkins/` | POST | Assigned users | Check-in |
| `/api/checkins/confirm` | POST | Assigned users | Confirm check-in |
| `/api/scheduler/daily-digest` | POST | CRON_SECRET | Send digest emails |
| `/api/scheduler/run-all` | POST | Admin | Run all jobs |
| `/api/exports/audit-logs` | GET | Admin | Audit log query |
| `/api/public/schedule/{id}` | GET | None | Student schedule lookup |
| `/health` | GET | None | Service health |
