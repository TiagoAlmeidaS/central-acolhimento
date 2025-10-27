# Deployment Runbook - Central de Acolhimento

## Pre-Deployment Checklist

- [ ] Code review aprovado
- [ ] CI/CD pipeline passed
- [ ] Test coverage > 80%
- [ ] Security scan passed (no critical CVEs)
- [ ] Database migrations preparadas
- [ ] Backup do banco anterior realizado
- [ ] Rollback plan documentado

## Deployment Environments

### Development
- **URL**: http://localhost:8000
- **Database**: SQLite (local)
- **LLM**: Docker container local
- **Deploy**: Manual via `docker-compose up`

### Staging
- **URL**: https://staging-api.central-acolhimento.com
- **Database**: PostgreSQL managed
- **LLM**: Container em Kubernetes (staging cluster)
- **Deploy**: Automated via CI/CD (GitHub Actions)

### Production
- **URL**: https://api.central-acolhimento.com
- **Database**: PostgreSQL HA (multi-AZ)
- **LLM**: Container em Kubernetes (prod cluster) com GPU
- **Deploy**: Manual approval required

## Deployment Steps (Kubernetes)

### 1. Pre-Deployment

```bash
# Verify you're on correct context
kubectl config current-context
# Should be: prod-eks-central-acolhimento

# Check current deployment
kubectl get deployments -n central-acolhimento
kubectl get pods -n central-acolhimento
```

### 2. Backup Database

```bash
# Backup production database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_*.sql
```

### 3. Update Image Tags

```bash
# Build and push new image
docker build -t your-registry/central-acolhimento-api:v1.2.3 ./api
docker push your-registry/central-acolhimento-api:v1.2.3
```

### 4. Apply Database Migrations

```bash
# Run migrations
kubectl run alembic-migration \
  --image=your-registry/central-acolhimento-api:v1.2.3 \
  --rm -it --restart=Never -- \
  alembic upgrade head
```

### 5. Update Deployment

```bash
# Update image tag in deployment
kubectl set image deployment/api \
  api=your-registry/central-acolhimento-api:v1.2.3 \
  -n central-acolhimento

# Watch rollout status
kubectl rollout status deployment/api -n central-acolhimento
```

### 6. Verify Deployment

```bash
# Check pods are running
kubectl get pods -n central-acolhimento

# Check logs
kubectl logs -f deployment/api -n central-acolhimento

# Test health endpoint
curl https://api.central-acolhimento.com/health
```

### 7. Post-Deployment

```bash
# Smoke tests
curl -X POST https://api.central-acolhimento.com/api/v1/contatos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Test", "telefone": "11-9999-8888", "motivo": "test"}'

# Check metrics
kubectl top pods -n central-acolhimento
```

## Rollback Procedure

### If Deployment Fails

```bash
# 1. Rollback to previous version
kubectl rollout undo deployment/api -n central-acolhimento

# 2. Watch rollback status
kubectl rollout status deployment/api -n central-acolhimento

# 3. Verify service is working
curl https://api.central-acolhimento.com/health

# 4. If database migration is the issue, restore backup
pg_restore $DATABASE_URL < backup_*.sql
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n central-acolhimento

# Check logs
kubectl logs <pod-name> -n central-acolhimento

# Common issues:
# - Image pull errors: Check registry credentials
# - Database connection errors: Check DATABASE_URL env var
# - Out of memory: Check resource limits
```

### LLM Service Unavailable

```bash
# Check LLM pod
kubectl get pods -n central-acolhimento | grep llm

# Check LLM logs
kubectl logs -f statefulset/llm -n central-acolhimento

# Restart LLM if needed
kubectl rollout restart statefulset/llm -n central-acolhimento
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl run db-test \
  --image=postgres:15 \
  --rm -it --restart=Never -- \
  psql $DATABASE_URL

# Check connection pool
kubectl exec -it deployment/api -n central-acolhimento -- \
  python -c "from app.core.database import engine; print(engine.pool.size())"
```

## Post-Deployment Monitoring

### Metrics to Watch

- **API Latency**: P95 < 3s
- **Error Rate**: < 1%
- **LLM Response Time**: P95 < 5s
- **Database Connections**: < 80% of pool

### Grafana Dashboards

Access: https://grafana.central-acolhimento.com

- **API Health Dashboard**: Monitor request rate, latency, errors
- **LLM Dashboard**: Monitor LLM call duration, success rate
- **Database Dashboard**: Monitor query performance, connections

### Alerts

- **PagerDuty**: Critical alerts (API down, DB unavailable)
- **Slack**: Warnings (high latency, high error rate)
- **Email**: Info notifications (deployments, scaling events)

## Communication

### Stakeholders to Notify

- **Development Team**: Deployment started
- **Operations Team**: Watch metrics for issues
- **Business Team**: New features available

### Post-Deployment Announcement

```markdown
✅ Deployment completed successfully

Version: v1.2.3
Environment: Production
Deployed by: [Your Name]
Deployment time: [Timestamp]

Changes:
- Added Excel export feature
- Improved LLM entity extraction accuracy
- Fixed bug in contact update endpoint

Please monitor dashboards for next 30 minutes.
```

## Emergency Contacts

- **On-Call Engineer**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Kubernetes Admin**: [Contact Info]
