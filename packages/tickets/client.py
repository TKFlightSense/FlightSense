# packages/tickets/client.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from services.db_service.db_service import DbService


@dataclass
class TicketPayload:
    project_key: str
    issue_type: str
    summary: str
    description: str
    department: str
    primary_label: str
    processed_data_id: Optional[int] = None


class AbstractTicketClient:
    """
    Interface so we can swap between a mock client and real Jira later.
    """
    def create_issue(self, payload: TicketPayload) -> Dict[str, Any]:
        raise NotImplementedError


class MockTicketClient(AbstractTicketClient):
    """
    Jira clone: stores tickets in the 'tickets' table via DbService.
    """

    def __init__(self, db: Optional[DbService] = None) -> None:
        self.db = db or DbService()

    def create_issue(self, payload: TicketPayload) -> Dict[str, Any]:
        fake_key = f"MOCK-{payload.project_key}-{payload.issue_type}"
        ticket_id = self.db.insert_ticket(
            processed_data_id=payload.processed_data_id,
            primary_label=payload.primary_label,
            department=payload.department,
            summary=payload.summary,
            description=payload.description,
            external_key=fake_key,
            source="mock",
            status="OPEN",
        )
        return {
            "id": ticket_id,
            "key": fake_key,
            "project_key": payload.project_key,
            "issue_type": payload.issue_type,
        }