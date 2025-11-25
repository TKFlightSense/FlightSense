from dotenv import load_dotenv
load_dotenv(override=True)

from packages.jira_client.client import JiraClient

client = JiraClient()

issue = client.create_issue(
    project_key="KHB",
    issue_type="Task",
    summary="Test Issue from API",
    description="This is a test issue created via the JiraClient API.",
    priority="Low",
)

print("Created:", issue["key"])