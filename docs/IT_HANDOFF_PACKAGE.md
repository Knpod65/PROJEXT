# IT Handoff Package — EMS Exam Management System

> Version: 2026-05-20  
> Target: IT Operations Team  
> Purpose: Deployment, monitoring, and incident response handoff

---

## 1. Environment Variables

### Required Variables

| Variable | Format | Example | Notes |
|----------|--------|---------|-------|
| `SECRET_KEY` | 64 hex chars | `a1b2c3d4...` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL URI | `postgresql://ems:pwd@db:5432/ems_prod` | Must use PostgreSQL for production |
| `CORS_ALLOWED_ORIGINS` | Comma-separated URLs | `https://exam.example.edu` | No trailing slashes |
| `POSTGRES_USER` | String | `ems_admin` | DB username |
| `POSTGRES_PASSWORD` | Strong password | `gen with secrets.token_urlsafe(20)` | |
| `POSTGRES_DB` | String | `ems_prod` | Database name |
| `CRON_SECRET` | 32 hex chars | `x9y8z7...` | For scheduled jobs |
| `ENV` | `production` or `development` | `production` | Enables/disables debug features |

### Optional Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `RETENTION_CLEANUP_ENABLED` | `False` | Set `True` only after admin + DPO sign-off |
| `LOG_LEVEL` | `INFO` | `DEBUG` for troubleshooting |
| `PDPA_IP_SALT` | Random string | Salt for IP hashing in audit logs |

---

## 2. Deployment Steps

### Prerequisites

```bash
# Required directories
mkdir -p /data/postgres /data/uploads /data/logs /data/backups
chown -R 1000:1000 /data
```

### Docker Compose (Production)

```bash
cd /opt/ems_system

# 1. Copy env template
cp .env.example .env

# 2. Edit .env with production values
nano .env

# 3. Create secrets (if using Docker secrets)
echo "your-secret-key" > secrets/secret_key
echo "your-postgres-pwd" > secrets/postgres_password

# 4. Start services
docker compose -f docker-compose.prod.yml up -d

# 5. Verify health
curl http://localhost/health
curl http://localhost/api/health/ready
```

### Database Initialization

```bash
# Run migrations
docker compose exec app python -c "
from backend.database import init_db
from backend.seed import seed_production
init_db()
seed_production()
"

# Verify tables
docker compose exec app python -c "
from backend.database import SessionLocal
db = SessionLocal()
print('Tables:', len(db.execute('SELECT tablename FROM pg_tables').fetchall()))
"
```

---

## 3. Monitoring

### Health Endpoints

| Endpoint | Purpose | Response | Alert Threshold |
|----------|---------|----------|-----------------|
| `GET /health` | Basic health | `{"status": "ok"}` | Non-200 |
| `GET /api/health/ready` | Deep health check | `{"db": "connected"}` | Non-200 |
| `GET /api/health/stats` | System stats | `{"cpu": ..., "mem": ...}` | CPU > 80% |

### Key Metrics to Monitor

```bash
# Database connection pool
curl -s http://localhost/api/health/stats | jq '.db.pool'

# Audit log volume (detect anomalies)
docker compose exec db psql -U ems_admin -d ems_prod \
  -c "SELECT count(*) FROM audit_logs WHERE created_at > now() - interval '1 hour';"

# Pending swap requests
docker compose exec db psql -U ems_admin -d ems_prod \
  -c "SELECT count(*) FROM swap_requests WHERE status = 'pending';"
```

### Log Locations

| Log | Path | Format |
|-----|------|--------|
| Application | `/data/logs/app.log` | JSON structured |
| Nginx access | `/data/logs/nginx/access.log` | Standard combined |
| Nginx error | `/data/logs/nginx/error.log` | Error log |
| PostgreSQL | `/data/logs/postgres.log` | CSV format |

---

## 4. Backup & Restore

### Backup Script

```bash
#!/bin/bash
# /opt/ems_system/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/data/backups"

# Database backup
docker compose exec db pg_dump -U ems_admin ems_prod | \
  gzip > "$BACKUP_DIR/db/ems_db_$DATE.sql.gz"

# Uploads backup
rsync -a /data/uploads/ "$BACKUP_DIR/files/"

# Retention (keep 30 days)
find "$BACKUP_DIR/db" -name "*.sql.gz" -mtime +30 -delete
find "$BACKUP_DIR/files" -type f -mtime +30 -delete
```

### Restore Procedure

```bash
# 1. Stop application
docker compose stop app

# 2. Restore database
gunzip -c /data/backups/db/ems_db_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose exec -T db psql -U ems_admin -d ems_prod

# 3. Restore uploads
rsync -av /data/backups/files/ /data/uploads/

# 4. Start application
docker compose start app

# 5. Verify
curl http://localhost/health
```

---

## 5. Scheduled Jobs

### Cron Configuration

```bash
# Add to crontab (crontab -e)
0 2 * * * cd /opt/ems_system && ./scripts/backup.sh >> /data/logs/backup.log 2>&1

# Daily digest (runs at 6 AM)
0 6 * * * curl -X POST http://localhost:8000/api/scheduler/daily-digest \
  -H "X-Cron-Secret: $CRON_SECRET"
```

### Manual Job Triggers

```bash
# Run all scheduled jobs
curl -X POST http://localhost/api/scheduler/run-all \
  -H "X-Cron-Secret: $CRON_SECRET"

# Send digest now (for testing)
curl -X POST http://localhost/api/scheduler/daily-digest \
  -H "X-Cron-Secret: $CRON_SECRET"
```

---

## 6. SSL/TLS Configuration

### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name exam.example.edu;

    ssl_certificate /data/ssl/fullchain.pem;
    ssl_certificate_key /data/ssl/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 7. Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| 502 Bad Gateway | App not running | `docker compose logs app` |
| Cookie not sent | CORS mismatch | Check `CORS_ALLOWED_ORIGINS` |
| DB connection failed | DB down or wrong URL | `docker compose logs db` |
| Permission denied | Wrong ownership | `chown -R 1000:1000 /data` |
| Slow queries | Missing indexes | Check `pg_stat_statements` |

### Diagnostic Commands

```bash
# Check all services
docker compose ps

# View logs (last 100 lines)
docker compose logs --tail=100 app

# Check database connectivity
docker compose exec app python -c "from backend.database import SessionLocal; print(SessionLocal().execute('SELECT 1').scalar())"

# Check disk space
df -h /data

# Check connected sessions
docker compose exec db psql -U ems_admin -d ems_prod -c "SELECT count(*) FROM sessions;"
```

---

## 8. Contact & Escalation

| Role | Contact | Hours |
|------|---------|-------|
| System Administrator | devops@example.edu | 24/7 |
| Application Owner | app-team@example.edu | 08:00-18:00 ICT |
| Security/DPO | dpo@example.edu | 09:00-17:00 ICT |