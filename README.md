# TKFlightSense

FlightSense is an end-to-end system for turning airline customer feedback into actionable, department-routed work.

## Vision

Airlines receive huge volumes of free-form feedback that is difficult to triage quickly and consistently. FlightSense is built to:

- Convert unstructured text into structured insights (segments, labels, priority)
- Route issues to the right operational owners (departments) automatically
- Trigger immediate action when feedback is high priority
- Provide dashboards so teams can see trends and outcomes, not just raw comments

The long-term goal is a “closed loop” feedback pipeline: intake → understanding → routing → action → reporting.

## System at a Glance

FlightSense is split into small, composable services:

- **Review Entry UI (Streamlit)**: submits a new review into the database
- **Processing Pipeline (Worker + Orchestrator)**: classifies and routes reviews
- **Automation (Jira + Email)**: creates tickets/alerts for relevant teams
- **Review Status UI (Streamlit)**: shows a live, step-based progress view
- **Backend API (FastAPI)**: provides analytics/high-priority feeds to the frontend
- **Frontend UI (React/Vite + Nginx)**: role-based dashboards
- **MySQL**: source of truth for reviews, processed segments, and status tracking

## End-to-End Pipeline

### 1) Intake

1. A user submits customer feedback via the Review Entry UI.
2. A new row is inserted into the `reviews` table.
3. The `review_status` tracking row (id=1) is updated to point to this review and enable tracking.

### 2) Processing (Worker → Listener → Orchestrator)

1. The background worker periodically checks for new/unprocessed reviews.
2. The listener selects candidate reviews and passes them into the orchestrator.
3. The orchestrator runs the core logic:
	- **Segmentation**: split the review into meaningful parts
	- **Labeling**: assign department/topic labels to each segment via an LLM-backed classifier
	- **Priority detection**: identify high-priority cases for escalation
	- **Persistence**: store structured outputs (e.g., in `processed_reviews`)

### 3) Routing + Automation

1. Based on labels, FlightSense maps segments to departments.
2. For routed outputs, the automation layer can:
	- Create Jira tickets
	- Send alert emails for high-priority items

### 4) Live Status Tracking

The Review Status UI reads `review_status` (id=1) and displays a step timeline that turns green as the pipeline advances.

Status codes (current UI mapping):

- `0` Arrived
- `1` Segmented and Labeled
- `2` Relevant department obtained
- `3` Completed

When the review is flagged high priority (detected from `processed_reviews.priority = HIGH`), the status page shows a dedicated red alert box indicating immediate action.

### 5) Analytics + Dashboards

1. The FastAPI backend serves aggregated statistics and high-priority feeds.
2. The React frontend consumes these endpoints and renders role-based dashboards.

## Docker / Services Overview

The default Docker Compose setup runs:

- `mysql`: MySQL database
- `app`: FastAPI backend
- `worker`: background processing loop
- `review-entry`: Streamlit intake UI
- `review-status`: Streamlit status UI
- `frontend`: React UI served behind Nginx

## Configuration Philosophy

FlightSense is designed to be configuration-driven:

- Department routing rules and ticket mappings live under `configs/`
- Model/label/routing artifacts live under `models/artifacts/`
- Provider selection (OpenAI vs vLLM) is controlled via environment variables

## “What success looks like”

- A review comes in and is triaged in seconds, not days
- High-priority issues trigger immediate action reliably
- Department teams see fewer irrelevant tickets and more actionable ones
- Leadership can measure trends, root causes, and improvement over time

## More docs

- Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- LLM setup: [docs/LLM.md](docs/LLM.md)
- Jira integration: [docs/JIRA.md](docs/JIRA.md)
- Email integration: [docs/EMAIL.md](docs/EMAIL.md)