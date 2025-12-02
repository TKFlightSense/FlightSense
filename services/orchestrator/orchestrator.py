from __future__ import annotations
from typing import Dict, Union, Optional, Any
import os
import logging

from services.db_service.db_service import DbService
from services.orchestrator.filter import DataFilter
from services.orchestrator.review_listener import ReviewListener
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

        self.classifier = FeedbackClassifier()
        
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
            self.db, self.access, self.classifier, jira_agent
        )

        # Initialize ReviewListener (if db_service is MySQLDbService)
        # This is a synchronous utility that can be called on-demand to process new reviews
        self.review_listener: Optional[ReviewListener] = None
        if hasattr(self.db, '_get_connection'):
            # Duck-typing check: MySQLDbService has _get_connection method
            try:
                self.review_listener = ReviewListener(self.db, self)
                # Register callback to notify when new reviews are detected
                self.review_listener.on_new_reviews(self._on_new_reviews_detected)
                logger.info("ReviewListener initialized (call check_and_process() to process new reviews)")
            except Exception as e:
                logger.warning(f"Failed to initialize ReviewListener: {e}")
        else:
            logger.info("ReviewListener skipped: db_service is not MySQLDbService")

    def _on_new_reviews_detected(self, reviews: list) -> None:
        """
        Callback invoked when ReviewListener detects new reviews.
        This can trigger downstream actions like notifications, analytics, etc.
        
        Args:
            reviews: List of new review rows detected (dicts with id, review, date, etc.)
        """
        logger.info(f"[EVENT] New reviews detected: {len(reviews)} rows")
        for review in reviews:
            logger.debug(f"  - Review ID {review.get('id')}: {review.get('review', '')[:50]}...")
        # Add more event handlers here as needed

    def process_new_reviews(self) -> Dict:
        """
        Manually trigger processing of new unprocessed reviews.
        This calls the ReviewListener to check for and classify new reviews.
        
        Returns:
            Dict with success status and number of reviews processed
        """
        if not self.review_listener:
            return {"success": False, "error": "ReviewListener not available"}
        
        try:
            processed = self.review_listener.check_and_process()
            stats = self.review_listener.get_stats()
            return {
                "success": True,
                "processed_this_batch": processed,
                "stats": stats,
            }
        except Exception as e:
            logger.error(f"Error processing new reviews: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def process_review(self, review_row: Dict[str, Any]) -> Dict:
        """
        Process a single review: classify it and persist segments.
        Called by ReviewListener when new reviews are detected.
        
        Args:
            review_row: Dict with keys: id, review, date, flight_number, pnr
            
        Returns:
            Dict with success status and number of segments inserted
        """
        review_id = review_row.get("id")
        review_text = review_row.get("review", "")

        if not review_text:
            logger.warning(f"Review {review_id} has empty text, skipping")
            return {"success": False, "error": "Empty review text"}

        try:
            # Step 1: Call LLM classifier
            logger.info(f"Classifying review id={review_id}")
            result = self.classifier.label_review(review_text)
            segments = result.get("segments", [])

            if not segments:
                logger.warning(f"No segments extracted from review id={review_id}")
                return {"success": False, "error": "No segments extracted"}

            # Step 2: Convert segments to DataFrame using segments_to_table
            segments_df = self.classifier.segments_to_table(review_id, segments)

            if segments_df.empty:
                logger.warning(f"Segments DataFrame empty for review id={review_id}")
                return {"success": False, "error": "Empty segments DataFrame"}

            # Step 3: Persist segments to processed_reviews table
            segments_list = segments_df.to_dict("records")
            inserted = self.db.insert_review_details_bulk(segments_list)

            logger.info(f"Processed review id={review_id}: inserted {inserted} segments")
            return {
                "success": True,
                "review_id": review_id,
                "segments_inserted": inserted,
            }

        except Exception as e:
            logger.error(f"Error processing review id={review_id}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

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
