from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional

import pandas as pd

from services.db_service.db_service import DbService
from packages.tickets.client import AbstractTicketClient, MockTicketClient, TicketPayload


LABEL_TO_DEPARTMENT = {
    "checkin_process": "GroundOps",
    "boarding_process": "GroundOps",
    "baggage_lost": "Baggage",
    "baggage_damaged": "Baggage",
    "inflight_experience_food_beverage": "Catering",
    "inflight_experience_seats_comfort": "Catering",
    "inflight_experience_entertainment": "Catering",
    "inflight_experience_cabin_service": "Catering",
    "inflight_experience_cleanliness": "Catering",
    "booking_and_ticketing": "CustomerSupport",
    "customer_support": "CustomerSupport",
    "pricing_and_loyalty": "CustomerSupport",
}


@dataclass
class DepartmentConfig:
    project_key: str
    issue_type: str


DEPARTMENT_CONFIG = {
    "GroundOps": DepartmentConfig(project_key="GOPS", issue_type="Incident"),
    "Baggage": DepartmentConfig(project_key="BAG", issue_type="Incident"),
    "Catering": DepartmentConfig(project_key="CAT", issue_type="Task"),
    "CustomerSupport": DepartmentConfig(project_key="CS", issue_type="Task"),
}


class JiraTicketAgent:
    """
    Agent responsible for turning classified feedback into tickets.
    Works against a TicketClient (mock Jira now, real Jira later).
    """

    def __init__(
        self,
        db: Optional[DbService] = None,
        ticket_client: Optional[AbstractTicketClient] = None,
    ):
        self.db = db or DbService()
        self.client = ticket_client or MockTicketClient(self.db)

    def _pick_primary_label(self, labels: str) -> Optional[str]:
        if not labels:
            return None
        for lbl in labels.split(","):
            l = lbl.strip()
            if l in LABEL_TO_DEPARTMENT:
                return l
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

    def create_ticket_for_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        primary_label = self._pick_primary_label(row.get("labels", ""))
        if not primary_label:
            return None

        department = LABEL_TO_DEPARTMENT[primary_label]
        cfg = DEPARTMENT_CONFIG.get(department)
        if not cfg:
            return None

        summary = self._build_summary(row, primary_label)
        description = self._build_description(row)

        processed_id = row.get("id")  # requires processed_data.id in the DF

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