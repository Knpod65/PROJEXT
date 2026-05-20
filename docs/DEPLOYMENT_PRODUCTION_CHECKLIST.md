# Deployment Production Checklist

## Pre-Deployment Verification

### Environment Variables
- [ ] `SECRET_KEY` set to random 32+ character string (not default)
- [ ] `DATABASE_URL` or connection parameters configured
- [ ] `ENV` or `ENVIRONMENT` set to "production"
- [ ] `ALLOWED_ORIGINS` configured for production domain
- [ ] `LOG_LEVEL` set to appropriate level (INFO or WARNING)
- [ ] `JSON_LOGS` enabled for structured logging

### Database Configuration
- [ ] PostgreSQL connection pool configured (if using PostgreSQL)
- [ ] Database migrations applied via `alembic upgrade head`
- [ ] Backup schedule configured and tested
- [ ] Connection string does not contain secrets in logs

### HTTPS / SSL Configuration
- [ ] SSL certificate valid and not expiring within 30 days
- [ ] HTTPS redirect enforced in nginx.conf
- [ ] HSTS headers configured
- [ ] Certificate chain complete (intermediate certificates included)

### Nginx Configuration
- [ ] Reverse proxy configured for backend API
- [ ] Static file serving configured for frontend dist/
- [ ] Rate limiting configured for auth endpoints
- [ ] Request size limits appropriate
- [ ] Error pages configured (404, 500, 502, 503, 504)

### Docker / Container Configuration
- [ ] `docker-compose.prod.yml` or production compose file validated
- [ ] Health check endpoints exposed (`/health/ready`)
- [ ] Container restart policies configured
- [ ] Resource limits (memory, CPU) set appropriately
- [ ] Secrets passed via environment or Docker secrets (not in image)

---

## Startup Verification

### Application Startup
- [ ] `import main` succeeds without errors
- [ ] No startup warnings about default secrets
- [ ] Database connection established successfully
- [ ] RBAC dependencies built (`permissions.build_dependencies()`)
- [ ] Seed data loaded (if applicable for production)
- [ ] Event handlers registered

### Health Check Endpoints
- [ ] `GET /health/ready` returns 200 with service status
- [ ] `GET /health/live` returns 200 (liveness probe)
- [ ] Health checks include database connectivity
- [ ] Health checks include settings validation
- [ ] Health checks include RBAC guard validation

### Logging Configuration
- [ ] Structured JSON logging enabled in production
- [ ] Request correlation IDs generated
- [ ] Sensitive data (passwords, tokens) excluded from logs
- [ ] Log rotation configured
- [ ] Log aggregation (ELK, Loki, etc.) connected if applicable

---

## Backup & Recovery

### Automated Backup
- [ ] Daily database backup scheduled
- [ ] Backup retention policy: minimum 30 days
- [ ] Backup stored in separate location/region
- [ ] Backup encryption at rest enabled
- [ ] Backup verification (restore test) performed monthly

### Restore Procedures
- [ ] Documented restore procedure in RUNBOOK.md
- [ ] Restore tested in staging environment
- [ ] Point-in-time recovery capability verified
- [ ] RTO (Recovery Time Objective) documented
- [ ] RPO (Recovery Point Objective) documented

---

## Monitoring & Observability

### Metrics Collection
- [ ] Application metrics exposed (Prometheus format if applicable)
- [ ] Database query performance metrics collected
- [ ] API endpoint latency tracked
- [ ] Error rate monitoring configured
- [ ] Dashboard uptime monitoring configured

### Alerting
- [ ] Critical alerts routed to on-call team
- [ ] Warning alerts routed to operations channel
- [ ] Alert escalation procedures documented
- [ ] False positive rate acceptable (<5%)

### Dashboards
- [ ] Operational health dashboard accessible
- [ ] PDPA compliance dashboard accessible to DPO
- [ ] Performance dashboard accessible to IT
- [ ] Error tracking dashboard accessible to developers

---

## Security Hardening

### Secrets Management
- [ ] No secrets in source code or repository
- [ ] Secrets rotated before production deployment
- [ ] Secrets stored in secure vault (HashiCorp Vault, AWS Secrets Manager, etc.)
- [ ] Secret access audited

### Access Control
- [ ] Production database access restricted to authorized personnel
- [ ] SSH/RDP access to production servers restricted
- [ ] Jump host or bastion host configured if applicable
- [ ] Multi-factor authentication enforced for production access

### Network Security
- [ ] Production servers in private network (no public IPs except load balancer)
- [ ] Security groups / firewall rules restrict traffic
- [ ] DDoS protection enabled at CDN/load balancer level
- [ ] WAF (Web Application Firewall) rules configured

---

## Performance Verification

### Load Testing
- [ ] Baseline performance established (response time, throughput)
- [ ] Load test performed at expected pilot user count
- [ ] Stress test performed at 2x expected load
- [ ] Memory leak testing (4+ hour sustained load)

### Resource Allocation
- [ ] CPU allocation sufficient for expected load
- [ ] Memory allocation sufficient for expected load
- [ ] Database connection pool sized appropriately
- [ ] Cache (Redis/Memcached) configured if applicable

---

## Rollback Readiness

### Rollback Procedures
- [ ] Documented rollback decision tree
- [ ] Hot rollback capability (zero-downtime if possible)
- [ ] Warm restart procedure documented
- [ ] Cold restart from backup procedure documented
- [ ] Data reconciliation procedure after rollback

### Rollback Testing
- [ ] Rollback tested in staging environment
- [ ] Rollback time measured and within acceptable limits
- [ ] Rollback communication template prepared

---

## Communication & Support

### User Communication
- [ ] Pilot user onboarding documentation
- [ ] Known issues / limitations communicated
- [ ] Support contact information provided
- [ ] Feedback mechanism established

### Incident Response
- [ ] Incident response runbook updated
- [ ] On-call rotation established
- [ ] Escalation matrix defined
- [ ] Post-incident review process defined

---

## Final Pre-Go-Live Checklist

### Mandatory (Must Pass)
- [ ] All environment variables configured correctly
- [ ] Database migrations applied
- [ ] SSL certificate valid
- [ ] Health checks passing
- [ ] Backup configured and tested
- [ ] Rollback procedure tested
- [ ] Monitoring and alerting operational
- [ ] No critical security vulnerabilities
- [ ] Backend tests passing (1413+)
- [ ] Frontend build passing
- [ ] i18n parity maintained

### Recommended (Should Pass)
- [ ] Performance benchmarks met
- [ ] Load testing completed
- [ ] Documentation complete
- [ ] Support team trained
- [ ] Pilot users briefed

### Sign-Off
- [ ] Operations team sign-off
- [ ] Security team sign-off (if applicable)
- [ ] DPO sign-off on PDPA controls
- [ ] Executive sponsor sign-off

---
*Checklist version: 1.0*
*Last updated: 2026-05-20*
*Owner: Platform Operations Team*