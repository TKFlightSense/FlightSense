# Deprecated

Docker deployment documentation was consolidated.

Use the single deployment guide instead:

- docs/DEPLOYMENT.md
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
