from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

import pandas as pd

from packages.tickets.client import AbstractTicketClient, TicketPayload
from packages.llm.summarizer import Summarizer
from models.labels import ALL_LABELS


@dataclass
class DepartmentConfig:
    project_key: str
    issue_type: str


def _load_department_routing_config() -> Dict[str, Any]:
    """Load department routing configuration from JSON file."""
    config_path = Path("models/artifacts/department_routing.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Department routing config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load configurations from JSON file
_ROUTING_CONFIG = _load_department_routing_config()
LABEL_TO_DEPARTMENT = _ROUTING_CONFIG["label_to_department"]
DEPARTMENT_CONFIG = {
    dept: DepartmentConfig(**config)
    for dept, config in _ROUTING_CONFIG["department_config"].items()
}


class JiraTicketAgent:
    """
    Agent responsible for turning classified feedback into tickets.

    It doesn't touch the DB directly; it only:
      - reads DataFrame rows
      - sends TicketPayloads to a TicketClient (mock Jira or real Jira).
    """

    def __init__(self, ticket_client: AbstractTicketClient, summarizer: Optional[Summarizer] = None):
        self.client = ticket_client
        self.summarizer = summarizer or Summarizer()

    # ---------- internal helpers ----------

    def _pick_primary_label(self, labels: str) -> Optional[str]:
        """
        labels: comma-separated fine-grained labels string from processed_data.labels
        e.g. "baggage_lost,inflight_experience_food_beverage"
        """
        if not labels:
            return None
        for raw in labels.split(","):
            lbl = raw.strip()
            if lbl in LABEL_TO_DEPARTMENT:
                return lbl
        return None

    def _build_summary(self, row: pd.Series, primary_label: str) -> str:
        return f"[{primary_label}] Customer feedback on recent flight"

    def _map_priority_to_jira(self, priority: str) -> str:
        """Map internal priority (HIGH/MEDIUM/LOW) to Jira priority names."""
        mapping = {
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low",
        }
        return mapping.get(priority.upper() if priority else "", "Medium")

    def _build_description(self, row: pd.Series, department: str) -> str:
        review = row.get("review", "")
        date = row.get("date", "N/A")
        flight_number = row.get("flight_number", "N/A")
        pnr = row.get("pnr", "N/A")
        
        # Use summarizer to generate AI summary
        ai_summary = self.summarizer.summarize(
            reviews=[review],
            department=department,
            purpose="create jira task"
        )
        
        # Clean, readable description
        return (
            f"h3. AI Summary\n"
            f"{ai_summary}\n\n"
            f"h3. Flight Information\n"
            f"* *Date:* {date}\n"
            f"* *Flight:* {flight_number}\n"
            f"* *PNR:* {pnr}\n\n"
            f"h3. Customer Feedback\n"
            f"{{quote}}{review}{{quote}}"
        )

    # ---------- public API ----------

    def create_ticket_for_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Create a single ticket for a processed_data row.
        Returns ticket metadata dict or None if no suitable label/department.
        """
        primary_label = self._pick_primary_label(row.get("labels", ""))
        if not primary_label:
            return None

        department = LABEL_TO_DEPARTMENT[primary_label]
        cfg = DEPARTMENT_CONFIG.get(department)
        if not cfg:
            return None

        summary = self._build_summary(row, primary_label)
        description = self._build_description(row, department)
        processed_id = row.get("id")  # requires 'id' column in DataFrame
        
        # Map priority and prepare labels for Jira
        internal_priority = row.get("priority", "MEDIUM")
        jira_priority = self._map_priority_to_jira(internal_priority)
        jira_labels = [primary_label, department]  # Add label and department as Jira labels

        payload = TicketPayload(
            project_key=cfg.project_key,
            issue_type=cfg.issue_type,
            summary=summary,
            description=description,
            department=department,
            primary_label=primary_label,
            priority=jira_priority,
            labels=jira_labels,
            processed_data_id=processed_id,
        )

        return self.client.create_issue(payload)

    def create_tickets_for_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create tickets for all applicable rows in a DataFrame.
        Returns list of ticket metadata dicts.
        """
        created: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            resp = self.create_ticket_for_row(row)
            if resp is not None:
                created.append(resp)
        return created
