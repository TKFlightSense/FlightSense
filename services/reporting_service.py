from __future__ import annotations
from typing import Dict, Any, Union, List, Optional, Set
import logging
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

from services.statistics_service import StatisticsService
from services.db_service.mysql_db_service import MySQLDbService
from services.access_control_service import AccessControlService
from services.orchestrator.filter import DataFilter
from packages.llm.classifier import FeedbackClassifier
from services.agents.jira_agent import JiraTicketAgent
from services.agents.email_agent import EmailSummaryAgent
from models.enums.enums import LabelToDepartment

logger = logging.getLogger(__name__)

def _load_department_routing_config() -> Dict[str, Any]:
    config_path = Path("models/artifacts/department_routing.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Department routing config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

_ROUTING_CONFIG = _load_department_routing_config()
_DEPARTMENT_LABELS = _ROUTING_CONFIG["department_labels"]

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
        email_agent: Optional[EmailSummaryAgent] = None,
        stats_service: StatisticsService = None
    ):
        self.db = db
        self.access = access
        self.classifier = classifier
        self.jira_agent = jira_agent
        self.email_agent = email_agent
        self.stats = stats_service

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

    def _get_department_samples(self, department_labels: List[str], date_from: datetime, date_to: datetime, sample_size: int = 3) -> List[str]:
        df = self.db.get_processed_data(
            date_from=date_from.date().isoformat(),
            date_to=date_to.date().isoformat(),
        )
        if df.empty or "labels" not in df.columns:
            return []

        mask = df["labels"].fillna("").apply(
            lambda s: any(lbl in s.split(",") for lbl in department_labels)
        )
        df = df[mask]
        if df.empty:
            return []

        return df["review"].head(sample_size).tolist()

    def _compute_label_shifts(self, department_labels: List[str], date_from: datetime, date_to: datetime, prev_from: datetime, prev_to: datetime) -> List[Dict[str, Any]]:
        shifts = []
        for label in department_labels:
            curr = self.stats.get_label_sentiment_distribution(label, date_from, date_to)
            prev = self.stats.get_label_sentiment_distribution(label, prev_from, prev_to)
            curr_neg = float(curr["percentage"].get("negative", 0.0))
            prev_neg = float(prev["percentage"].get("negative", 0.0))
            shifts.append({
                "label": label,
                "prev": prev_neg,
                "curr": curr_neg,
                "delta": curr_neg - prev_neg,
            })

        shifts.sort(key=lambda x: abs(x["delta"]), reverse=True)
        return shifts[:3]

    def run_weekly_reports(self) -> Dict[str, Any]:
        if not self.email_agent:
            msg = "Email agent not available for weekly reports"
            logger.warning(msg)
            return {"success": False, "error": msg}

        days = int(os.getenv("WEEKLY_REPORT_DAYS", "7"))
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days)
        prev_to = date_from
        prev_from = prev_to - timedelta(days=days)

        for dept, labels in _DEPARTMENT_LABELS.items():
            curr_sent = self.stats.get_department_sentiment_distribution(dept, date_from, date_to)
            prev_sent = self.stats.get_department_sentiment_distribution(dept, prev_from, prev_to)

            curr_total = self.stats.get_department_total_review_count(dept, date_from, date_to)
            prev_total = self.stats.get_department_total_review_count(dept, prev_from, prev_to)

            curr_pct = curr_sent["percentage"]
            prev_pct = prev_sent["percentage"]

            payload = {
                "department": dept,
                "date_from": date_from.date().isoformat(),
                "date_to": date_to.date().isoformat(),
                "total_feedback": curr_total,
                "total_feedback_delta": curr_total - prev_total,
                "sentiment_prev": prev_pct,
                "sentiment_curr": curr_pct,
                "sentiment_delta": {
                    "negative": float(curr_pct.get("negative", 0.0)) - float(prev_pct.get("negative", 0.0)),
                    "positive": float(curr_pct.get("positive", 0.0)) - float(prev_pct.get("positive", 0.0)),
                    "neutral": float(curr_pct.get("neutral", 0.0)) - float(prev_pct.get("neutral", 0.0)),
                },
                "label_shifts": self._compute_label_shifts(labels, date_from, date_to, prev_from, prev_to),
                "highlights": [
                    f"Total feedback change: {curr_total - prev_total:+d} vs last week",
                    f"Negative rate change: {float(curr_pct.get('negative', 0.0)) - float(prev_pct.get('negative', 0.0)):+.1f} pp",
                ],
                "samples": self._get_department_samples(labels, date_from, date_to, sample_size=3),
            }

            self.email_agent.send_weekly_report(payload)

        return {"success": True, "message": "Weekly reports sent"}


