from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Union, Optional
import os
import logging

from dateutil.relativedelta import relativedelta

from services.db_service.db_service import DbService
from services.db_service.my_db_service import Database
from services.orchestrator.filter import DataFilter
from services.access_control_service import AccessControlService
from services.auth_service import AuthService
from services.data_service import DataService
from services.reporting_service import ReportingService
from packages.llm.classifier import FeedbackClassifier
from packages.tickets.client import MockTicketClient, RealJiraTicketClient
from services.agents.jira_agent import JiraTicketAgent
from services.statistics_service import StatisticsService
from models.enums.enums import DepartmentToLabels

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
        self.stats = StatisticsService()

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

    # ---------- STATISTICS wrappers ----------

    def get_manager_stats(self, token: str,period: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> Dict:
        """
        Manager dashboard: aggregates all top-level stats in one call.
        """
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}

        # Optionally enforce that only manager/admin can access this
        role = user_info.get("role")
        if not self.access.is_full_access_role(role):
            return {"success": False, "error": "Forbidden: manager access required"}

        if date_to == None:
            date_to = datetime.now()

        if date_from == None:
            if period == "weekly":
                date_from = date_to - relativedelta(days=7)
            elif period == "monthly":
                date_from = date_to - relativedelta(weeks=4)
            else:
                date_from = date_to - relativedelta(months=12)

        review_count_distribution = self.stats.get_manager_review_count_distribution(date_from, date_to)
        sentiment = self.stats.get_manager_sentiment_distribution(date_from, date_to)
        priority = self.stats.get_manager_priority_distribution(date_from, date_to)

        if period == "weekly":
            period_label = "Last 7 days"
            historical_data = self.stats.get_manager_weekly_stats(date_from)
        elif period == "monthly":
            period_label = "Last 30 days"
            historical_data = self.stats.get_manager_monthly_stats(date_from)
        else:
            period_label = "Last year"
            historical_data = self.stats.get_manager_yearly_stats(date_from)

        return {
            "success": True,
            "data": {
                "total": review_count_distribution["total_count"],
                "department_distribution": review_count_distribution["department_counts"],
                "sentiment_counts": sentiment["counts"],
                "sentiment_percentages": sentiment["percentage"],
                "priority_counts": priority["counts"],
                "priority_percentages": priority["percentage"],
                "department_sentiment_distribution": sentiment["department_sentiment_distribution"],
                "period_label": period_label,
                "historical_data": historical_data
            },
        }

    def get_department_stats(self, token: str, department_name: str, period: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> Dict:
        """
        Department dashboard: stats for a single department.
        """
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}

        # Optionally enforce dep-based access
        # e.g., if non-manager, ensure user belongs to this department
        role = user_info.get("role")
        user_dept = user_info.get("department")
        if not self.access.is_full_access_role(role):
            if user_dept != department_name:
                return {"success": False, "error": "Forbidden: wrong department"}


        if date_to == None:
           date_to = datetime.now()

        if date_from == None:
            if period == "weekly":
                date_from = date_to - relativedelta(days=7)
            elif period == "monthly":
                date_from = date_to - relativedelta(weeks=4)
            else:
                date_from = date_to - relativedelta(months=12)

        total = self.stats.get_department_total_review_count(department_name, date_from, date_to)
        sentiment = self.stats.get_department_sentiment_distribution(department_name, date_from, date_to)
        priority = self.stats.get_department_priority_distribution(department_name, date_from, date_to)
        label_dist = self.stats.get_department_label_distribution(department_name, date_from, date_to)

        label_sentiment = {}

        for label in DepartmentToLabels[department_name].value:
            label_sentiment[label]= self.stats.get_label_sentiment_distribution(label, date_from, date_to)

        if period == "weekly":
            period_label = "Last 7 days"
            historical_data = self.stats.get_department_weekly_stats(department_name, date_from)
        elif period == "monthly":
            period_label = "Last 30 days"
            historical_data = self.stats.get_department_monthly_stats(department_name, date_from)
        else:
            period_label = "Last year"
            historical_data = self.stats.get_department_yearly_stats(department_name, date_from)


        return {
            "success": True,
            "data": {
                "department_name": department_name,
                "total": total,
                "sentiment_distribution": sentiment,
                "priority_distribution": priority,
                "label_distribution": label_dist,
                "label_sentiment_distribution": label_sentiment,
                "period_label": period_label,
                "historical_data": historical_data
            },
        }


