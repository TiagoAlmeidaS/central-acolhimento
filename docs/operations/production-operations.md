# Central de Acolhimento - Production Operations Guide
# Complete guide for operating the production environment

## Overview

This guide provides comprehensive instructions for operating the Central de Acolhimento system in production, including deployment, monitoring, maintenance, and troubleshooting.

## Quick Start

### 1. Deploy to Production
```bash
# Copy environment file
cp env.prod.example .env.prod
# Edit .env.prod with your production values

# Deploy services
./deploy-prod.sh
```

### 2. Verify Deployment
```bash
# Check all services
curl http://localhost:8000/health  # API
curl http://localhost:8001/health  # LLM
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
```

### 3. Access Services
- **API**: http://localhost:8000
- **LLM**: http://localhost:8001
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

## Production Architecture

### Service Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   API Service   │    │   LLM Service   │
│   (Port 80/443) │────│   (Port 8000)   │────│   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   PostgreSQL    │    │     Ollama      │
│   (Port 3000)   │    │   (Port 5432)   │    │   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Redis       │
│   (Port 9090)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘
```

### Data Flow
1. **Client Request** → Nginx Proxy
2. **API Request** → API Service → PostgreSQL
3. **LLM Request** → LLM Service → Ollama
4. **Monitoring** → Prometheus → Grafana

## Deployment Procedures

### Initial Deployment
```bash
# 1. Prepare environment
cp env.prod.example .env.prod
# Edit .env.prod with production values

# 2. Deploy services
./deploy-prod.sh

# 3. Verify deployment
./monitor.sh

# 4. Setup monitoring
# Access Grafana at http://localhost:3000
# Import dashboards from monitoring/grafana/dashboards/
```

### Rolling Updates
```bash
# 1. Build new images
docker build -t central-acolhimento-api:latest ./api-repo/
docker build -t central-acolhimento-llm:latest ./llm-repo/

# 2. Update services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --no-deps api-service
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --no-deps llm-service

# 3. Verify update
./monitor.sh
```

### Database Migrations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec api-service alembic upgrade head

# Verify migration
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec postgres psql -U postgres -d central_acolhimento -c "\dt"
```

## Monitoring and Alerting

### Health Checks
```bash
# Manual health check
./monitor.sh

# Continuous monitoring
./monitor.sh continuous

# Generate report
./monitor.sh report
```

### Key Metrics to Monitor
- **API Response Time**: < 1 second
- **LLM Response Time**: < 5 seconds
- **Database Connections**: < 80% of max
- **Memory Usage**: < 85%
- **CPU Usage**: < 80%
- **Disk Usage**: < 90%

### Alerting Channels
- **Email**: Configured in ALERT_EMAIL
- **Slack**: Configured in ALERT_WEBHOOK_URL
- **Grafana**: Built-in alerting rules

### Grafana Dashboards
1. **System Overview**: CPU, Memory, Disk usage
2. **API Metrics**: Request rate, response time, error rate
3. **LLM Metrics**: Processing time, model usage
4. **Database Metrics**: Connections, query performance
5. **Container Metrics**: Resource usage per container

## Backup and Recovery

### Automated Backups
```bash
# Run backup
./backup.sh

# Schedule daily backups (add to crontab)
0 2 * * * /path/to/backup.sh
```

### Manual Backup
```bash
# Database backup
docker exec central-acolhimento-postgres-prod pg_dump -U postgres central_acolhimento > backup.sql

# Application data backup
docker run --rm -v central-acolhimento_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
```

### Recovery Procedures
```bash
# Restore from backup
./backup.sh restore YYYYMMDD_HHMMSS

# Manual database restore
docker exec -i central-acolhimento-postgres-prod psql -U postgres central_acolhimento < backup.sql
```

## Maintenance Procedures

### Regular Maintenance Tasks
- **Daily**: Check logs, verify backups
- **Weekly**: Review metrics, update dependencies
- **Monthly**: Security updates, performance tuning

### Log Management
```bash
# View logs
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs -f

# View specific service logs
docker logs central-acolhimento-api-prod -f
docker logs central-acolhimento-llm-prod -f

# Clean old logs
docker system prune -f
```

### Performance Tuning
```bash
# Check resource usage
docker stats

# Scale services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --scale api-service=3

# Optimize database
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec postgres psql -U postgres -d central_acolhimento -c "VACUUM ANALYZE;"
```

## Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check container status
docker ps -a

# Check logs
docker logs <container_name>

# Restart service
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart <service_name>
```

#### 2. Database Connection Issues
```bash
# Check database status
docker exec central-acolhimento-postgres-prod pg_isready -U postgres

# Check connections
docker exec central-acolhimento-postgres-prod psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Reset connections
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart postgres
```

#### 3. LLM Service Issues
```bash
# Check Ollama status
curl http://localhost:11434/

# Check model availability
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart ollama
```

#### 4. High Resource Usage
```bash
# Check resource usage
docker stats

# Check system resources
top
free -h
df -h

# Scale services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --scale api-service=2
```

### Emergency Procedures

#### 1. Service Outage
```bash
# Quick restart
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart

# Check status
./monitor.sh
```

#### 2. Database Corruption
```bash
# Stop services
docker-compose -f docker-compose.prod.yml --env-file .env.prod stop

# Restore from backup
./backup.sh restore <backup_date>

# Start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod start
```

#### 3. Security Incident
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Check logs for suspicious activity
docker logs central-acolhimento-api-prod | grep -i "error\|exception\|failed"

# Restart with security updates
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## Security Considerations

### SSL/TLS Configuration
- Use Let's Encrypt certificates in production
- Enable HSTS headers
- Configure proper cipher suites
- Regular certificate renewal

### Access Control
- Use strong passwords
- Enable basic auth for monitoring
- Restrict network access
- Regular security updates

### Data Protection
- Encrypt data at rest
- Use secure connections
- Regular backups
- Access logging

## Performance Optimization

### API Service
- Enable connection pooling
- Use Redis caching
- Optimize database queries
- Implement rate limiting

### LLM Service
- Model caching
- Request batching
- Resource monitoring
- Error handling

### Database
- Connection pooling
- Query optimization
- Index management
- Regular maintenance

## Scaling Procedures

### Horizontal Scaling
```bash
# Scale API service
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --scale api-service=3

# Scale LLM service
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --scale llm-service=2
```

### Vertical Scaling
- Increase container resources
- Optimize application code
- Use faster hardware
- Implement caching

## Disaster Recovery

### Backup Strategy
- Daily database backups
- Weekly full system backups
- Offsite backup storage
- Regular restore testing

### Recovery Procedures
- RTO: 4 hours
- RPO: 24 hours
- Automated failover
- Manual intervention procedures

## Support and Maintenance

### Regular Tasks
- Monitor system health
- Review logs and metrics
- Update dependencies
- Security patches

### Emergency Contacts
- System Administrator: admin@central-acolhimento.com
- Development Team: dev@central-acolhimento.com
- On-call Engineer: +55-11-99999-9999

### Documentation Updates
- Keep this guide updated
- Document new procedures
- Share knowledge with team
- Regular review cycles
