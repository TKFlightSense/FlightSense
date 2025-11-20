from __future__ import annotations
from typing import Dict, Union
import logging

from services.db_service.db_service import DbService
from services.orchestrator.filter import DataFilter
from services.access_control_service import AccessControlService
from packages.llm.segmentation_service import SegmentationService
from services.agents.jira_agent import JiraTicketAgent

logger = logging.getLogger(__name__)


class ReportingService:
    """
    Handles reporting-related operations:
      - LLM-based segmentation & labeling
      - Ticket creation via JiraTicketAgent (using mock Jira now)
    """

    def __init__(
        self,
        db_service: DbService,
        access_control: AccessControlService,
        segmentation: SegmentationService,
        jira_agent: JiraTicketAgent,
    ):
        self.db = db_service
        self.access = access_control
        self.segmentation = segmentation
        self.jira_agent = jira_agent

    # ---------- segmentation / labeling ----------

    def label_single_review(self, review: str):
        segments = self.segmentation.segment_review(review, max_segments=3)
        return segments

    # ---------- ticket creation ----------

    def create_tickets_for_filtered(
        self,
        user_info: Dict,
        filters: Union[Dict, DataFilter],
    ) -> Dict:
        """
        Use filters + role permissions to select feedback rows,
        then create Jira-like tickets for them (via JiraTicketAgent).
        """
        try:
            # Only ADMIN/MANAGER can trigger bulk ticket creation
            if not self.access.is_full_access_role(user_info["role"]):
                return {
                    "success": False,
                    "error": "Only admin/manager can trigger ticket creation",
                }

            if isinstance(filters, dict):
                data_filter = DataFilter.from_dict(filters)
            else:
                data_filter = filters

            validation_errors = data_filter.validate()
            if validation_errors:
                return {
                    "success": False,
                    "error": "Validation failed",
                    "details": validation_errors,
                }

            data_filter.to_enum()

            df = self.db.get_processed_data(
                limit=data_filter.limit,
                label_type=data_filter.label_type,
                label_status=data_filter.label_status,
                date_from=data_filter.date_from,
                date_to=data_filter.date_to,
            )

            if df.empty:
                return {
                    "success": True,
                    "created_tickets": [],
                    "count": 0,
                    "message": "No matching feedback for ticket creation",
                }

            # Optional: only rows without existing tickets
            if getattr(data_filter, "only_without_ticket", False):
                ticket_df = self.db.get_open_tickets()
                if not ticket_df.empty:
                    existing_ids = (
                        ticket_df["processed_data_id"]
                        .dropna()
                        .unique()
                        .tolist()
                    )
                    df = df[~df["id"].isin(existing_ids)]

            if df.empty:
                return {
                    "success": True,
                    "created_tickets": [],
                    "count": 0,
                    "message": "All matching feedback already has tickets",
                }

            created = self.jira_agent.create_tickets_for_dataframe(df)

            return {
                "success": True,
                "created_tickets": created,
                "count": len(created),
            }

        except Exception as e:
            logger.error(f"Error during ticket creation: {e}")
            return {"success": False, "error": str(e)}