# FlightSense Deployment Guide

This guide provides step-by-step instructions for deploying the FlightSense application.

## Prerequisites

- **Docker & Docker Compose**: For containerized deployment.
- **Python 3.9+**: For running scripts and local development.
- **MySQL Client**: Optional, for manual database verification.

## Deployment Steps

### 1. Environment Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` and configure the following:
    -   **LLM Configuration**: Set `OPENAI_API_KEY` or configure vLLM settings.
    -   **Jira Configuration**: Set `JIRA_URL`, `JIRA_USER`, and `JIRA_TOKEN` if using real Jira.
    -   **Security**: Change `JWT_SECRET` to a strong random string.

### 2. Database Setup

You can set up the MySQL database using the provided Python script. This script creates the database, user, and all necessary tables.

1.  Ensure your MySQL server is running.
2.  Run the setup script:
    ```bash
    python scripts/setup_mysql.py
    ```
3.  Follow the interactive prompts. You will need the MySQL root password.

### 3. Application Deployment

#### Using Docker (Recommended)

1.  Build and start the containers:
    ```bash
    docker-compose up -d --build
    ```
2.  Check the logs to ensure everything started correctly:
    ```bash
    docker-compose logs -f app
    ```
3.  The API will be available at `http://localhost:8000`.

#### Running Locally

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Start the application:
    ```bash
    python app.py
    ```

## Testing the Listener Flow

The "Listener" is a component that processes raw reviews from the database, classifies them using the LLM, and stores the results.

Since the listener is configured to run on-demand (synchronous), you can test the entire flow using the provided test script.

### Automated Test Script

We have provided a script `scripts/test_listener_flow.py` that:
1.  Inserts a sample raw review into the `reviews` table.
2.  Triggers the listener to process new reviews.
3.  Verifies that the review was classified and segments were stored in `processed_reviews`.

**To run the test:**

```bash
python scripts/test_listener_flow.py
```

### Manual Verification

1.  **Insert a Raw Review**:
    Connect to your MySQL database and run:
    ```sql
    INSERT INTO reviews (review, date, flight_number) 
    VALUES ('The flight was great but the food was cold.', CURDATE(), 'TK1234');
    ```

2.  **Trigger Processing**:
    You can trigger the listener via the Python shell:
    ```python
    from app import get_orchestrator
    from services.db_service.mysql_db_service import MySQLDbService
    
    # Initialize services
    db = MySQLDbService()
    orch = get_orchestrator() # Note: might need manual init if not running via app
    
    # Or simpler, if you have the app running, you might add an endpoint to trigger it.
    # Currently, the listener is internal. Use the test script for easiest verification.
    ```

## Troubleshooting

-   **Database Connection Errors**: Check `MYSQL_HOST`, `MYSQL_PORT`, and credentials in `.env`. If running in Docker, `MYSQL_HOST` should be `mysql`.
-   **LLM Errors**: Verify `OPENAI_API_KEY` is correct and you have quota.
-   **Missing Tables**: Re-run `scripts/setup_mysql.py`.

