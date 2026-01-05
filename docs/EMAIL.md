# Email Integration

FlightSense can send two types of emails:

- High-priority alert emails (immediate)
- Weekly department overview reports (scheduled)

Email sending is performed by the background worker service.

## Configuration sources

### 1) Recipient configuration (JSON)

Recipients and subject templates live in:

- models/artifacts/email_config.json

This file includes:

- department_recipients: department code -> list of recipient emails
- email_subject_template: subject template string
- default_days_lookback: default window for daily lookback flows

### 2) SMTP configuration (environment)

SMTP settings are read from environment variables:

- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASS
- SMTP_FROM

These variables must be set for the `worker` container if you want emails to send.

## High-priority alerts

When a review is processed, FlightSense checks classified segments.

- If a segment is priority HIGH, FlightSense determines the department from the label.
- It creates a Jira ticket (depending on Jira mode) and sends an alert email to that department.

Alert recipients are taken from models/artifacts/email_config.json.

## Weekly reports

The background worker sends weekly reports on a schedule.

Schedule configuration (environment variables on the worker):

- WEEKLY_REPORT_WEEKDAY: 0 = Monday, 6 = Sunday (default: 0)
- WEEKLY_REPORT_HOUR: hour of day (default: 6)
- WEEKLY_REPORT_MINUTE: minute of hour (default: 0)
- WEEKLY_REPORT_DAYS: number of days per comparison window (default: 7)

Weekly reports:

- Compute department sentiment totals for the current window and the previous window.
- Highlight the largest negative-rate shifts by label.
- Include a small sample of raw feedback.
- Use the LLM summarizer for some summaries.

## Testing emails

### 1) Safest approach

Set every department recipient to your own email in models/artifacts/email_config.json.

Then start the stack and watch worker logs:

```bash
docker-compose up -d --build
docker-compose logs -f worker
```

### 2) Manual trigger (inside container)

You can trigger daily reports directly:

```bash
docker-compose exec app python -c "from services.agents.email_agent import EmailSummaryAgent; EmailSummaryAgent().send_daily_reports()"
```

Notes:

- This requires MySQL connectivity and SMTP env vars.
- Summaries use the LLM summarizer, so the OpenAI API key must be set.
