# FlightSense Deployment

This is the single deployment guide for the full FlightSense stack.

It covers Docker Compose (recommended) and the operational scripts used to manage MySQL and demo data.

## What gets deployed

Docker Compose runs these services:

- `mysql`: MySQL 8 (database)
- `app`: FastAPI backend (serves APIs for dashboards and processing endpoints)
- `worker`: background worker loop (processes new reviews, runs statistics updates, sends weekly reports)
- `review-entry`: Streamlit UI (submits a new review)
- `review-status`: Streamlit UI (shows pipeline status)
- `frontend`: React UI behind Nginx (dashboards)

## Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Docker Compose v2

## Configure environment

1) Create a `.env` file at the project root:

```bash
cp .env.example .env
```

2) Set at least these variables in `.env`:

- `OPENAI_API_KEY` (required for classification and summarization)
- `JWT_SECRET` (required for API auth)
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`

Optional (enable integrations):

- Jira: `USE_REAL_JIRA`, `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`

Important: set `MYSQL_PASSWORD` explicitly.
If it is missing, different services have different defaults and MySQL authentication can fail.

## Start (Docker Compose)

From the repo root:

```bash
docker-compose up -d --build
```

Check status:

```bash
docker-compose ps
docker-compose logs -f app
```

## URLs

- Frontend dashboards: http://localhost:3000
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health
- Review Entry UI: http://localhost:8501
- Review Status UI: http://localhost:8502
- MySQL: localhost:${MYSQL_PORT:-3306}

## How processing works in deployment

- Reviews are inserted into MySQL (`reviews` table).
- The `worker` container runs a loop:
  - Processes new reviews (classification + persistence)
  - Updates statistics periodically
  - Sends weekly email reports on a schedule

If you do not run the `worker` service, the system will accept reviews but processing will not happen automatically.

## Common operations

### View logs

```bash
docker-compose logs -f worker
docker-compose logs -f review-entry
docker-compose logs -f review-status
docker-compose logs -f frontend
```

### Reset or seed the database

- Create or reset the admin user (default: `admin` / `rootroot`):

```bash
docker-compose exec app python scripts/create_admin_user.py --username admin --password rootroot
```

- Insert sample reviews:

```bash
docker-compose exec app python scripts/add_test_reviews.py --count 20 --days 30
```

### Export/import database for sharing

- Export:

```bash
docker-compose exec app python scripts/export_database.py
```

- Import:

```bash
docker-compose exec app python scripts/import_database.py path/to/dump.sql.gz
```

### Clear data (dangerous)

This truncates tables but keeps schema:

```bash
docker-compose exec app python scripts/clear_databases.py --yes
```

## Stop

```bash
docker-compose down
```

To remove containers and delete the MySQL volume (this deletes all data):

```bash
docker-compose down -v
```

