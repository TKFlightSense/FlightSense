from __future__ import annotations

import os
import base64
from typing import Dict, Any, Optional

import requests


class JiraClient:
    """
    Thin wrapper around Jira REST API for creating issues.
    Works with Jira Cloud using email + API token.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("JIRA_URL", "").rstrip("/")
        self.email = os.getenv("JIRA_USER")
        self.api_token = os.getenv("JIRA_TOKEN")

        if not self.base_url or not self.email or not self.api_token:
            raise RuntimeError("JIRA_URL, JIRA_USER, and JIRA_TOKEN must be set in environment.")

        token_bytes = f"{self.email}:{self.api_token}".encode("utf-8")
        self.auth_header = base64.b64encode(token_bytes).decode("utf-8")

        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def plain_to_adf(text: str) -> Dict[str, Any]:
        """Convert plain text to Atlassian Document Format (ADF) for v3 fields."""
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }

    def create_issue(
        self,
        project_key: str,
        issue_type: str,
        summary: str,
        description: str,
        priority: str = "Medium",

        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/issue"

        fields: Dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
            "description": self.plain_to_adf(description),
            "priority": {"name": priority},
        }

        if extra_fields:
            fields.update(extra_fields)

        payload = {"fields": fields}

        resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
