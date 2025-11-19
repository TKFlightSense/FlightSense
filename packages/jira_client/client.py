from __future__ import annotations
import os
import base64
from typing import Dict, Any
import requests


class JiraClient:
    """
    Thin wrapper around Jira REST API for creating issues.
    Works with Jira Cloud using email + API token. [oai_citation:1‡Atlassian Developer](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/?utm_source=chatgpt.com)
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("JIRA_BASE_URL")  # e.g. "https://your-domain.atlassian.net"
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")

        if not self.base_url or not self.email or not self.api_token:
            raise RuntimeError("JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be set.")

        token_bytes = f"{self.email}:{self.api_token}".encode("utf-8")
        self.auth_header = base64.b64encode(token_bytes).decode("utf-8")

    def create_issue(
        self,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str,
        extra_fields: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/issue"
        headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        fields: Dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
            "description": description,
        }

        if extra_fields:
            fields.update(extra_fields)

        payload = {"fields": fields}

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
