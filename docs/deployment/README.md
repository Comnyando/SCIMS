# Deployment Guide

Complete guide for deploying SCIMS to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Manual Deployment](#manual-deployment)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Database Setup](#database-setup)
- [Backup & Recovery](#backup--recovery)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

- **OS**: Linux (Ubuntu 22.04+ recommended) or Windows Server
- **RAM**: Minimum 4GB, 8GB+ recommended
- **CPU**: 2+ cores recommended
- **Storage**: 20GB+ free space (more for database backups)
- **Network**: Ports 80, 443, 5432 (PostgreSQL), 6379 (Redis) available

### Required Software

- Docker Engine 20.10+ and Docker Compose v2.0+
- Git
- SSL certificate (Let's Encrypt recommended)

### Optional

- Domain name with DNS access
- Email service (for notifications)
- Monitoring tools (Prometheus, Grafana, etc.)

## Pre-Deployment Checklist

- [ ] Server meets requirements
- [ ] Docker and Docker Compose installed
- [ ] Domain name configured (if using)
- [ ] SSL certificate obtained or ready to obtain
- [ ] Environment variables prepared
- [ ] Database backup strategy planned
- [ ] Monitoring solution configured
- [ ] Firewall rules configured

## Docker Compose Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/scims.git
cd scims
```

### Step 2: Configure Environment

```bash
# Copy production environment template
cp .env.example .env.production

# Edit with production values
nano .env.production
```

**Critical Environment Variables:**

```env
# Security
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET=<generate-strong-random-key>
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+psycopg://user:password@postgres:5432/scims

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# CORS (update with your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (if using)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
```

**Generate Secret Keys:**

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Run Database Migrations

```bash
# Using Docker Compose
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### Step 4: Start Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Step 5: Verify Deployment

```bash
# Check health endpoint
curl http://localhost/health

# Check API root
curl http://localhost/api/v1

# Check Swagger docs
curl http://localhost/api/docs
```

## Manual Deployment

### Backend Deployment

1. **Install Dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment:**

```bash
export DATABASE_URL=postgresql+psycopg://...
export SECRET_KEY=...
# ... other environment variables
```

3. **Run Migrations:**

```bash
alembic upgrade head
```

4. **Start Application:**

```bash
# Using Gunicorn (recommended)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Or using Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

5. **Start Celery Workers:**

```bash
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

### Frontend Deployment

1. **Build Production Bundle:**

```bash
cd frontend
pnpm install
pnpm build
```

2. **Serve Static Files:**

The build output is in `frontend/dist/`. Serve with Nginx or another web server.

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

1. **Install Certbot:**

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain Certificate:**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-Renewal:**

Certbot sets up automatic renewal. Test with:

```bash
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

See [SSL Configuration Guide](ssl-configuration.md) for detailed Nginx SSL setup.

## Database Setup

### Initial Setup

```bash
# Create database
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres -c "CREATE DATABASE scims;"

# Run migrations
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### Database Backups

See [Backup & Recovery](#backup--recovery) section below.

## Backup & Recovery

### Automated Backups

Set up automated PostgreSQL backups:

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups/scims"
DATE=$(date +%Y%m%d_%H%M%S)
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres scims > "$BACKUP_DIR/backup_$DATE.sql"

# Keep last 7 days
find "$BACKUP_DIR" -name "backup_*.sql" -mtime +7 -delete
```

**Cron Job (daily at 2 AM):**

```bash
0 2 * * * /path/to/backup-script.sh
```

### Restore from Backup

```bash
# Restore database
docker compose -f docker-compose.prod.yml exec -T postgres psql -U postgres scims < backup_20240101_020000.sql
```

### Redis Backups

Redis data is less critical but can be backed up:

```bash
# Save Redis snapshot
docker compose -f docker-compose.prod.yml exec redis redis-cli SAVE
docker compose -f docker-compose.prod.yml cp redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

## Monitoring & Health Checks

### Health Check Endpoints

- **Application Health**: `GET /health`
- **API Health**: `GET /api/v1`

### Logging

View logs:

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
```

### Monitoring Tools

Consider setting up:
- **Prometheus** for metrics
- **Grafana** for dashboards
- **Sentry** for error tracking
- **Uptime monitoring** (UptimeRobot, Pingdom, etc.)

## Troubleshooting

### Services Won't Start

1. Check logs: `docker compose -f docker-compose.prod.yml logs`
2. Verify environment variables
3. Check port availability: `netstat -tulpn | grep :80`
4. Verify Docker resources: `docker system df`

### Database Connection Issues

1. Verify DATABASE_URL format
2. Check PostgreSQL is running: `docker compose -f docker-compose.prod.yml ps postgres`
3. Test connection: `docker compose -f docker-compose.prod.yml exec backend python -c "from app.database import engine; engine.connect()"`

### SSL Certificate Issues

1. Verify domain DNS points to server
2. Check port 80 is accessible (for HTTP-01 challenge)
3. Review Certbot logs: `sudo journalctl -u certbot.timer`

### Performance Issues

1. Check resource usage: `docker stats`
2. Review database query performance
3. Check Redis connection
4. Review application logs for errors

## Post-Deployment

### Initial Setup

1. Create admin user (if needed)
2. Configure email settings
3. Set up monitoring alerts
4. Test all critical features
5. Document deployment details

### Maintenance

- **Regular Updates**: Keep dependencies updated
- **Security Patches**: Apply promptly
- **Backup Verification**: Test restore procedures monthly
- **Log Rotation**: Configure log rotation
- **Performance Monitoring**: Review metrics regularly

---

For more details, see:
- [SSL Configuration Guide](ssl-configuration.md)
- [Email Setup Guide](../user-guide/email-setup.md)
- [Backend README](../../backend/README.md)

