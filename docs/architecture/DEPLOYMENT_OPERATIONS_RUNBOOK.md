# Deployment & Operations Runbook

## Startup

1. Ensure `.env` has valid `SECRET_KEY`, `DATABASE_URL`, `CRON_SECRET`
2. `docker-compose up -d` - wait 60s for health check grace period
3. Verify: `curl http://localhost:8000/health` returns `{"status": "ok"}`

## Rollback Procedure

1. `docker-compose down`
2. Restore DB from backup: `psql $DATABASE_URL < backup.sql`
3. `git checkout <previous-working-tag>`
4. `docker-compose up -d`

## Emergency Disable

Set `EMERGENCY_MODE=true` in `.env` and restart containers. This returns 503 for non-read endpoints.

## Degraded Mode

- `SKIP_OPTIMIZER=true` - skip schedule optimization jobs
- `SKIP_PDF=true` - skip PDF report generation

## Recovery Checklist

- [ ] PostgreSQL connectivity ok
- [ ] Redis connectivity ok (if used)
- [ ] Disk space > 20% free
- [ ] Memory usage < 80%
- [ ] `/health` endpoint returns 200
- [ ] `/api/analytics/executive-summary` returns data