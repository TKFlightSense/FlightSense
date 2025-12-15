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
    def wiki_to_adf(text: str) -> Dict[str, Any]:
        """
        Convert wiki-style markup to Atlassian Document Format (ADF).
        Supports: h3. headers, * bullets, {quote} blocks, and plain paragraphs.
        """
        content = []
        lines = text.split("\n")
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Handle h3. headers
            if line.startswith("h3. "):
                header_text = line[4:].strip()
                content.append({
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": header_text}]
                })
                i += 1
                continue
            
            # Handle {quote} blocks
            if line.strip().startswith("{quote}"):
                quote_text = line.replace("{quote}", "").strip()
                # Collect all lines until closing {quote}
                while i + 1 < len(lines) and "{quote}" not in lines[i + 1]:
                    i += 1
                    quote_text += " " + lines[i].strip()
                if i + 1 < len(lines) and "{quote}" in lines[i + 1]:
                    quote_text += " " + lines[i + 1].replace("{quote}", "").strip()
                    i += 1
                
                content.append({
                    "type": "blockquote",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": quote_text.strip()}]
                    }]
                })
                i += 1
                continue
            
            # Handle * bullet points
            if line.strip().startswith("* "):
                bullet_items = []
                while i < len(lines) and lines[i].strip().startswith("* "):
                    bullet_line = lines[i].strip()[2:]  # Remove "* "
                    # Handle bold with *text*
                    bullet_content = []
                    if bullet_line.startswith("*") and "*" in bullet_line[1:]:
                        # Extract bold text
                        end_bold = bullet_line.index("*", 1)
                        bold_text = bullet_line[1:end_bold]
                        rest_text = bullet_line[end_bold + 1:]
                        bullet_content.append({"type": "text", "text": bold_text, "marks": [{"type": "strong"}]})
                        if rest_text:
                            bullet_content.append({"type": "text", "text": rest_text})
                    else:
                        bullet_content.append({"type": "text", "text": bullet_line})
                    
                    bullet_items.append({
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": bullet_content
                        }]
                    })
                    i += 1
                
                content.append({
                    "type": "bulletList",
                    "content": bullet_items
                })
                continue
            
            # Handle regular paragraphs (skip empty lines)
            if line.strip():
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}]
                })
            
            i += 1
        
        return {
            "type": "doc",
            "version": 1,
            "content": content
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
            "description": self.wiki_to_adf(description),  # Use wiki_to_adf for proper formatting
            "priority": {"name": priority},
        }

        if extra_fields:
            fields.update(extra_fields)

        payload = {"fields": fields}

        resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
