from __future__ import annotations
from typing import Dict, Union, Optional
import os
import logging

from services.db_service.db_service import DbService
from services.orchestrator.filter import DataFilter
from services.access_control_service import AccessControlService
from services.auth_service import AuthService
from services.data_service import DataService
from services.reporting_service import ReportingService
from packages.llm.classifier import FeedbackClassifier
from packages.tickets.client import MockTicketClient, RealJiraTicketClient
from services.agents.jira_agent import JiraTicketAgent

logger = logging.getLogger(__name__)


class FlightSenseOrchestrator:
    """
    Thin façade that composes domain services.
    """

    def __init__(self, db_service: DbService, secret_key: str):
        self.db = db_service

        self.access = AccessControlService()
        self.auth = AuthService(self.db, secret_key, self.access)
        self.data = DataService(self.db, self.access)

        classifier = FeedbackClassifier()
        
        # Choose between mock and real Jira based on environment
        use_real_jira = os.getenv("USE_REAL_JIRA", "false").lower() == "true"
        if use_real_jira:
            try:
                ticket_client = RealJiraTicketClient(self.db)
                logger.info("Using REAL Jira client")
            except Exception as e:
                logger.warning(f"Failed to initialize real Jira, falling back to mock: {e}")
                ticket_client = MockTicketClient(self.db)
        else:
            ticket_client = MockTicketClient(self.db)
            logger.info("Using MOCK Jira client")
        
        jira_agent = JiraTicketAgent(ticket_client=ticket_client)
        self.reporting = ReportingService(
            self.db, self.access, classifier, jira_agent
        )

    # ---------- AUTH wrappers ----------

    def register_user(self, *args, **kwargs):
        return self.auth.register_user(*args, **kwargs)

    def login(self, username: str, password: str) -> Dict:
        return self.auth.login(username, password)

    def verify_token(self, token: str) -> Optional[Dict]:
        return self.auth.verify_token(token)

    # ---------- DATA wrappers (token → user_info) ----------

    def get_processed_data_filtered(
        self, token: str, filters: Union[Dict, DataFilter]
    ) -> Dict:
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}
        return self.data.get_processed_data_filtered(user_info, filters)

    def get_dashboard_summary(self, token: str, page: str = "dashboard") -> Dict:
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}
        return self.data.get_dashboard_summary(user_info, page)

    def get_category_analytics(self, token: str, label: str) -> Dict:
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}
        return self.data.get_category_analytics(user_info, label)

    def push_processed_data(self, token: str, data) -> Dict:
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}
        return self.data.push_processed_data(user_info, data)

    # ---------- REPORTING wrappers ----------

    def label_single_review(self, review: str):
        return self.reporting.label_single_review(review)

    def create_tickets_for_filtered(
        self, token: str, filters: Union[Dict, DataFilter]
    ) -> Dict:
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}
        return self.reporting.create_tickets_for_filtered(user_info, filters)
