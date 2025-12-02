from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

import pandas as pd

from packages.tickets.client import AbstractTicketClient, TicketPayload
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

    def __init__(self, ticket_client: AbstractTicketClient):
        self.client = ticket_client

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

    def _build_description(self, row: pd.Series) -> str:
        review = row.get("review", "")
        date = row.get("date", "N/A")
        labels = row.get("labels", "")
        return (
            f"*Customer feedback date:* {date}\n"
            f"*Detected labels:* {labels}\n\n"
            f"*Raw feedback:*\n{review}\n"
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
        description = self._build_description(row)
        processed_id = row.get("id")  # requires 'id' column in DataFrame

        payload = TicketPayload(
            project_key=cfg.project_key,
            issue_type=cfg.issue_type,
            summary=summary,
            description=description,
            department=department,
            primary_label=primary_label,
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
