from __future__ import annotations
from typing import Dict, Any, Union, List, Optional, Set
import logging
import pandas as pd

from services.db_service.mysql_db_service import MySQLDbService
from services.access_control_service import AccessControlService
from services.orchestrator.filter import DataFilter
from packages.llm.classifier import FeedbackClassifier
from services.agents.jira_agent import JiraTicketAgent
from services.agents.email_agent import EmailSummaryAgent
from models.enums.enums import LabelToDepartment

logger = logging.getLogger(__name__)

class ReportingService:
    """
    Service for handling reporting tasks, including:
    - Manual review labeling
    - Batch ticket creation
    - High-priority automation (Jira + Email)
    """

    def __init__(
        self, 
        db: MySQLDbService, 
        access: AccessControlService, 
        classifier: FeedbackClassifier, 
        jira_agent: JiraTicketAgent,
        email_agent: Optional[EmailSummaryAgent] = None
    ):
        self.db = db
        self.access = access
        self.classifier = classifier
        self.jira_agent = jira_agent
        self.email_agent = email_agent

    def label_single_review(self, review: str) -> Dict[str, Any]:
        """Classify a single review text on demand."""
        return self.classifier.label_review(review)

    def create_tickets_for_filtered(self, user_info: Dict, filters: Union[Dict, DataFilter]) -> Dict[str, Any]:
        """
        Create Jira tickets for all reviews matching the filter.
        """
        return {"success": False, "error": "Batch ticket creation not fully implemented yet"}

    def handle_high_priority_automation(self, review_row: Dict[str, Any], segments: List[Dict[str, Any]]) -> None:
        """
        Check segments for HIGH priority and trigger Jira/Email agents.
        """
        if not self.email_agent:
            logger.warning("Email agent not available for automation")
            return

        review_id = review_row.get("id")
        
        # Filter for HIGH priority segments
        high_priority_segments = [s for s in segments if s.get("priority") == "HIGH"]
        
        if not high_priority_segments:
            return

        logger.info(f"Found {len(high_priority_segments)} HIGH priority segments in review {review_id}")
        
        alerted_departments: Set[str] = set()
        
        for seg in high_priority_segments:
            label = seg.get("label")
            if not label:
                continue
                
            try:
                # Map label to department
                if label in LabelToDepartment.__members__:
                     department = LabelToDepartment[label].value
                else:
                     logger.warning(f"Label '{label}' not found in LabelToDepartment mapping")
                     continue

                if department in alerted_departments:
                    continue
                
                # Construct a row-like dict for the agents
                enhanced_row = review_row.copy()
                enhanced_row["labels"] = label
                enhanced_row["priority"] = "HIGH"
                
                # Convert to Series for compatibility with Jira agent
                row_series = pd.Series(enhanced_row)
                
                # 1. Create Jira Ticket
                logger.info(f"Creating Jira ticket for high priority review {review_id} (Dept: {department})")
                self.jira_agent.create_ticket_for_row(row_series)
                
                # 2. Send Email Alert
                logger.info(f"Sending email alert for high priority review {review_id} (Dept: {department})")
                self.email_agent.send_alert_email(enhanced_row, department, "HIGH")
                
                alerted_departments.add(department)
                
            except Exception as e:
                logger.error(f"Error triggering agents for high priority review {review_id}: {e}")
