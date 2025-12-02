# FlightSense Docker Deployment Guide

## Overview

FlightSense can be deployed using Docker and Docker Compose for easy, consistent deployment across different environments.

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Installing Docker

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Follow installation wizard
- Restart computer

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**macOS:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Install the application

---

## Quick Start

## Quick Start

### Windows PowerShell Quick Deploy

```powershell
# 1. Configure environment
cp .env.example .env
# Edit .env with your settings (OPENAI_API_KEY, JWT_SECRET, MySQL passwords)

# 2. Start services
docker-compose up -d --build

# 3. Check health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f app
```

### Linux/macOS Quick Deploy

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your settings (OPENAI_API_KEY, JWT_SECRET, MySQL passwords)

# 2. Start services
docker-compose up -d --build

# 3. Check health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f app
```

### 1. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` with your configuration:

```dotenv
# MySQL Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=flightsense
MYSQL_USER=flightsense
MYSQL_PASSWORD=your_secure_password

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here

# Jira Configuration (optional)
USE_REAL_JIRA=true
JIRA_URL=https://your-domain.atlassian.net
JIRA_USER=your-email@example.com
JIRA_TOKEN=your_jira_api_token

# API Security
JWT_SECRET=generate-a-very-secure-random-string-here

# Environment
ENVIRONMENT=production
API_PORT=8000
```

### 2. Start Services

```bash
# Start all services (app + MySQL)
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check running containers
docker-compose ps

# Check application logs
docker-compose logs -f app

# Check MySQL logs
docker-compose logs -f mysql

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "FlightSense API",
  "database": "MySQL",
  "jira": "Real"
}
```

---

## Docker Compose Services

### Service Architecture

```
┌─────────────────┐
│  App (8000)     │  <- FastAPI Application
└────────┬────────┘
         │
┌────────▼────────┐
│  MySQL (3306)   │  <- Database
└─────────────────┘
```

### Available Services

1. **mysql**: MySQL 8.0 database server
   - Port: 3306
   - Persistent volume: `mysql_data`
   - Auto-initializes tables on first start

2. **app**: FlightSense FastAPI application
   - Port: 8000
   - 4 workers (configurable)
   - Health checks enabled
   - Auto-restarts on failure

---

## Common Commands

### Managing Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart app

# View logs
docker-compose logs -f app
docker-compose logs -f mysql

# Execute commands in container
docker-compose exec app bash
docker-compose exec mysql mysql -u root -p
```

### Database Management

```bash
# Access MySQL shell
docker-compose exec mysql mysql -u flightsense -p flightsense

# Backup database
docker-compose exec mysql mysqldump -u root -p flightsense > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -p flightsense < backup.sql

# View tables
docker-compose exec mysql mysql -u flightsense -p -e "USE flightsense; SHOW TABLES;"
```

### Building and Updating

```bash
# Rebuild application image
docker-compose build app

# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build

# Remove all containers and volumes (WARNING: deletes data)
docker-compose down -v
```

---

## Production Deployment

### 1. Security Configuration

**Change default passwords:**
```dotenv
MYSQL_ROOT_PASSWORD=<strong-random-password>
MYSQL_PASSWORD=<strong-random-password>
JWT_SECRET=<strong-random-string>
```

**Generate secure secrets:**
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate MySQL password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 2. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 3. Monitoring and Logging

```bash
# Enable persistent logging
docker-compose logs -f app > logs/app.log 2>&1 &

# Monitor resource usage
docker stats
```

### 4. Security Best Practices

- Change all default passwords in `.env`
- Use strong JWT secret (32+ characters)
- Set up automated backups
- Configure resource limits
- Enable monitoring
- Use Docker secrets for sensitive data
- Consider using a reverse proxy (Nginx, Traefik, etc.) for production
- Enable HTTPS with SSL/TLS certificates

---

## Scaling

### Horizontal Scaling

Scale application workers:

```bash
# Scale to 4 app instances
docker-compose up -d --scale app=4
```

Note: For production load balancing with multiple instances, consider using an external load balancer or reverse proxy.

### Vertical Scaling

Modify Dockerfile to use more workers:

```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

---

## Backup and Restore

### Database Backup

**Automated backup script:**

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose exec -T mysql mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  flightsense > $BACKUP_DIR/flightsense_$DATE.sql

echo "Backup created: $BACKUP_DIR/flightsense_$DATE.sql"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Volume Backup

```bash
# Backup MySQL data volume
docker run --rm \
  -v flightsense_mysql_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/mysql_data_backup.tar.gz -C /data .
```

### Restore from Backup

```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d mysql
sleep 10
docker-compose exec -T mysql mysql -u root -p < backups/flightsense_backup.sql

# Restart all services
docker-compose up -d
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Check container status
docker-compose ps

# Inspect container
docker inspect flightsense-app
```

### Database Connection Issues

```bash
# Verify MySQL is running
docker-compose exec mysql mysqladmin ping -h localhost -u root -p

# Check connection from app container
docker-compose exec app python -c "
from services.db_service.mysql_db_service import MySQLDbService
db = MySQLDbService()
print('Connection successful')
"
```

### Port Conflicts

```bash
# Check what's using port 8000
# Windows:
netstat -ano | findstr :8000
# Linux/macOS:
lsof -i :8000

# Change port in .env
echo "API_PORT=8001" >> .env
docker-compose up -d
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Reduce workers in Dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Rebuild and restart
docker-compose up -d --build
```

### Clean Slate Restart

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

---

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MYSQL_ROOT_PASSWORD` | MySQL root password | - | Yes |
| `MYSQL_DATABASE` | Database name | flightsense | No |
| `MYSQL_USER` | Database user | flightsense | No |
| `MYSQL_PASSWORD` | Database password | - | Yes |
| `LLM_PROVIDER` | LLM provider (openai/vllm) | openai | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | If using OpenAI |
| `VLLM_API_BASE` | vLLM API endpoint | http://localhost:8001 | If using vLLM |
| `USE_REAL_JIRA` | Enable Jira integration | false | No |
| `JIRA_URL` | Jira instance URL | - | If using Jira |
| `JIRA_USER` | Jira user email | - | If using Jira |
| `JIRA_TOKEN` | Jira API token | - | If using Jira |
| `JWT_SECRET` | JWT signing secret | - | Yes |
| `ENVIRONMENT` | Environment (dev/prod) | production | No |
| `API_PORT` | API port | 8000 | No |

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy FlightSense

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker image
        run: |
          docker build -t flightsense:latest .
          docker push flightsense:latest
      
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && docker-compose pull && docker-compose up -d'
```

---

## Performance Tuning

### Optimize Docker Image

```dockerfile
# Use multi-stage build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### MySQL Optimization

Add to `docker-compose.yml`:

```yaml
mysql:
  command: >
    --max_connections=500
    --innodb_buffer_pool_size=2G
    --innodb_log_file_size=512M
```

---

## Support

For Docker-specific issues:
- Check container logs: `docker-compose logs`
- Verify network connectivity: `docker network inspect flightsense_flightsense-network`
- Review Docker documentation: https://docs.docker.com
