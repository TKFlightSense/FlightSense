# Jira Integration

FlightSense can create Jira issues for high-priority feedback.

## Modes

- Mock mode (default): stores tickets in the local `tickets` table.
- Real Jira mode: creates issues in Jira Cloud and also stores a reference in the local `tickets` table.

The mode is controlled by the environment variable:

- USE_REAL_JIRA=false (mock)
- USE_REAL_JIRA=true (real)

## Required environment variables (real Jira)

Set these in your `.env`:

- JIRA_URL: Jira base URL (example: https://your-domain.atlassian.net)
- JIRA_USER: Jira account email
- JIRA_TOKEN: Jira API token

If any of these are missing while USE_REAL_JIRA=true, the Jira client will fail to initialize.

## Routing and project mapping

FlightSense uses a configuration file to map labels to departments and departments to Jira project settings:

- models/artifacts/department_routing.json

This file defines:

- label_to_department: fine-grained label -> department code
- department_config: department code -> Jira project key and issue type

If your Jira project keys or issue types differ, update department_config.

## When tickets are created

In the current implementation, tickets are created only for HIGH priority segments during processing.

Flow:

- A review is classified into segments.
- If any segment has priority HIGH, FlightSense triggers automation.
- For each affected department, it creates one Jira issue.

Notes:

- Batch ticket creation for arbitrary filters is not implemented.
- LOW/MEDIUM priority segments do not create Jira issues by default.

## Verifying tickets

### Mock mode

- Check the `tickets` table in MySQL.
- The stored ticket key will look like: MOCK-<project_key>-<issue_type>

### Real Jira mode

- Confirm issues appear in your Jira projects.
- A reference is also stored in the `tickets` table with source set to `jira`.

## Jira issue content

The Jira description is built as readable sections (AI summary, flight info, original feedback) and is converted into Atlassian Document Format before submission.
