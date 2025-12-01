# Docker Deployment Files

This document lists all Docker-related files created for FlightSense deployment.

## Files Created

### 1. Dockerfile
**Location:** `./Dockerfile`
**Purpose:** Defines the Docker image for the FlightSense application
**Features:**
- Based on Python 3.11-slim
- Multi-stage optimization ready
- Non-root user for security
- Health check included
- 4 uvicorn workers for production

### 2. docker-compose.yml
**Location:** `./docker-compose.yml`
**Purpose:** Orchestrates all services (app, MySQL)
**Services:**
- `mysql`: MySQL 8.0 database with persistent volume
- `app`: FlightSense FastAPI application

### 3. .dockerignore
**Location:** `./.dockerignore`
**Purpose:** Excludes unnecessary files from Docker build context
**Excludes:** Python cache, virtual envs, .env files, logs, documentation

### 4. Database Initialization Script
**Location:** `./scripts/docker/init_db.sql`
**Purpose:** Auto-creates database tables on first MySQL container start
**Tables:** processed_data, tickets, statistics, user_data

### 5. Docker Deployment Guide
**Location:** `./docs/DOCKER.md`
**Purpose:** Complete guide for Docker deployment
**Sections:**
- Quick start commands
- Service architecture
- Common Docker commands
- Production deployment checklist
- Backup and restore procedures
- Troubleshooting guide
- Environment variables reference

## Quick Start Commands

### Start Services
```bash
# Start deployment (app + MySQL)
docker-compose up -d

# Rebuild and start
docker-compose up -d --build
```

### View Status
```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f mysql

# Check health
curl http://localhost:8000/health
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Environment Configuration

Required `.env` variables:
```dotenv
# MySQL
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=flightsense
MYSQL_USER=flightsense
MYSQL_PASSWORD=your_secure_password

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Security
JWT_SECRET=your-secure-random-string

# Environment
ENVIRONMENT=production
```

## Port Mappings

- **8000**: FastAPI application (app service)
- **3306**: MySQL database (mysql service)

## Volumes

- `mysql_data`: Persistent MySQL database storage
- `./logs`: Application logs (bind mount)
- `./data`: Application data (bind mount)
- `./models`: Model configurations (read-only bind mount)
- `./configs`: Application configs (read-only bind mount)

## Network

All services communicate through `flightsense-network` bridge network.

## Health Checks

### MySQL
- Command: `mysqladmin ping`
- Interval: 10 seconds
- Retries: 5

### Application
- Command: `curl http://localhost:8000/health`
- Interval: 30 seconds
- Start period: 40 seconds
- Retries: 3

## Production Recommendations

1. Change all default passwords in `.env`
2. Use strong JWT secret (32+ characters)
3. Set up automated backups
4. Configure resource limits
5. Enable monitoring
6. Use Docker secrets for sensitive data
7. Consider using a reverse proxy (Nginx, Traefik, etc.) for production
8. Enable HTTPS with SSL/TLS certificates

## Troubleshooting

### Container won't start
```bash
docker-compose logs app
docker-compose ps
```

### Database connection issues
```bash
docker-compose exec mysql mysqladmin ping -h localhost -u root -p
```

### Port conflicts
```bash
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000

# Change port in .env
echo "API_PORT=8001" >> .env
```

### Clean restart
```bash
docker-compose down -v
docker-compose up -d --build
```

## Additional Resources

- Full deployment guide: `docs/DOCKER.md`
- General deployment: `docs/DEPLOYMENT.md`
- Docker documentation: https://docs.docker.com
- Docker Compose reference: https://docs.docker.com/compose/
