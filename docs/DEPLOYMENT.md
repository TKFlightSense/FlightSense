# FlightSense Deployment Guide

## Overview

FlightSense can be deployed with either SQLite (development) or MySQL (production). This guide covers local MySQL deployment and Docker deployment.

---

## Prerequisites

### Software Requirements
- Python 3.10+
- MySQL Server 8.0+ (for production deployment)
- Git

### System Requirements
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB minimum
- CPU: 2 cores minimum

---

## Database Setup

### Option 1: SQLite (Development)
SQLite is used by default for development. No additional setup required.

```bash
# Just set in .env
USE_MYSQL=false
```

### Option 2: MySQL (Production - Recommended)

#### 1. Install MySQL Server

**Windows:**
```powershell
# Download from https://dev.mysql.com/downloads/mysql/
# Or use chocolatey
choco install mysql
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

#### 2. Create Database and User

```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE flightsense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace with secure password!)
CREATE USER 'flightsense'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON flightsense.* TO 'flightsense'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user='flightsense';

EXIT;
```

#### 3. Test Connection

```bash
mysql -u flightsense -p flightsense
```

---

## Application Setup

### 1. Clone Repository

```bash
git clone https://github.com/TKFlightSense/FlightSense.git
cd FlightSense
```

### 2. Create Virtual Environment

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
```

**Required `.env` Configuration:**

```dotenv
# Database - Choose one
USE_MYSQL=true

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=flightsense
MYSQL_USER=flightsense
MYSQL_PASSWORD=your_secure_password

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Jira (if using real Jira)
USE_REAL_JIRA=true
JIRA_URL=https://tkflightsense.atlassian.net
JIRA_USER=your_jira_email@example.com
JIRA_TOKEN=your_jira_api_token

# API Security
JWT_SECRET=generate-a-secure-random-string-here
API_HOST=0.0.0.0
API_PORT=8000
```

### 5. Initialize Database

```bash
# Test database connection and create tables
python -c "from services.db_service.mysql_db_service import MySQLDbService; db = MySQLDbService(); print('Database initialized')"
```

---

## Running the Application

### Development Mode

```bash
# With auto-reload
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Set environment
export ENV=production  # Linux/macOS
$env:ENV="production"  # Windows PowerShell

# Run with production settings
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn (Linux/macOS Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Testing the Deployment

### 1. Health Check

```bash
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

### 2. Register Test User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@airline.com",
    "password": "SecurePass123",
    "role": "admin"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePass123"
  }'
```

### 4. Test Classification

```bash
# Get token from login response and use it
curl -X POST http://localhost:8000/api/classify/label \
  -H "Content-Type: application/json" \
  -d '{
    "review": "My baggage was lost and the food was terrible"
  }'
```

---

## Database Migration (SQLite to MySQL)

If you have existing SQLite data:

```python
# migration_script.py
from services.db_service.db_service import DbService
from services.db_service.mysql_db_service import MySQLDbService

# Connect to both databases
sqlite_db = DbService()
mysql_db = MySQLDbService()

# Migrate processed_data
df = sqlite_db.get_processed_data(limit=None)
if not df.empty:
    mysql_db.push_processed_data(df)
    print(f"Migrated {len(df)} processed_data rows")

# Migrate users
# Note: You'll need to add get_all_users() method to DbService
# Or manually export/import users

print("Migration complete")
```

---

## Monitoring

### Check Database Status

```sql
-- Connect to MySQL
mysql -u flightsense -p flightsense

-- Check tables
SHOW TABLES;

-- Check data counts
SELECT COUNT(*) FROM processed_data;
SELECT COUNT(*) FROM tickets;
SELECT COUNT(*) FROM user_data;

-- Check recent feedback
SELECT id, labels, DATE(created_at) as date
FROM processed_data
ORDER BY created_at DESC
LIMIT 10;
```

### Application Logs

```bash
# View application logs (if running in background)
tail -f logs/flightsense.log

# Or use journalctl for systemd service
sudo journalctl -u flightsense -f
```

---

## Production Security Checklist

- [ ] Change default JWT_SECRET to a strong random value
- [ ] Use strong MySQL password
- [ ] Enable MySQL SSL/TLS connections
- [ ] Configure firewall rules (only allow port 3306 from application server)
- [ ] Use environment variables, never commit .env file
- [ ] Enable HTTPS (use nginx/Apache as reverse proxy)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Use MySQL user with minimal privileges (not root)
- [ ] Enable rate limiting on API endpoints
- [ ] Set up monitoring and alerting

---

## Troubleshooting

### MySQL Connection Errors

**Error:** `Access denied for user 'flightsense'@'localhost'`
```bash
# Reset user password
mysql -u root -p
ALTER USER 'flightsense'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

**Error:** `Can't connect to MySQL server on 'localhost'`
```bash
# Check if MySQL is running
sudo systemctl status mysql  # Linux
mysql.server status          # macOS
Get-Service MySQL            # Windows PowerShell

# Start MySQL
sudo systemctl start mysql   # Linux
mysql.server start           # macOS
Start-Service MySQL          # Windows
```

### Application Won't Start

```bash
# Check Python dependencies
pip list

# Test database connection separately
python -c "from services.db_service.mysql_db_service import MySQLDbService; MySQLDbService()"

# Check environment variables
python -c "import os; print('MySQL:', os.getenv('USE_MYSQL')); print('Host:', os.getenv('MYSQL_HOST'))"
```

### Port Already in Use

```bash
# Find process using port 8000
# Linux/macOS:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill the process or use different port
export API_PORT=8001
```

---

## Systemd Service (Linux Production)

Create `/etc/systemd/system/flightsense.service`:

```ini
[Unit]
Description=FlightSense API Service
After=network.target mysql.service

[Service]
Type=simple
User=flightsense
WorkingDirectory=/opt/flightsense
Environment="PATH=/opt/flightsense/.venv/bin"
EnvironmentFile=/opt/flightsense/.env
ExecStart=/opt/flightsense/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flightsense
sudo systemctl start flightsense
sudo systemctl status flightsense
```

---

## Next Steps

After successful deployment:

1. Set up automated backups
2. Configure monitoring (Prometheus + Grafana)
3. Set up reverse proxy (nginx/Apache)
4. Enable HTTPS with Let's Encrypt
5. Configure log aggregation (ELK stack)
6. Set up CI/CD pipeline
7. Create admin dashboard
8. Configure email alerts for system errors

---

## Support

For issues or questions:
- Check logs: `tail -f logs/flightsense.log`
- Review error messages in console output
- Check MySQL error log: `/var/log/mysql/error.log`
- Open an issue on GitHub
