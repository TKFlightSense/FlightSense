from __future__ import annotations
from typing import Dict, Union, Optional, Any
import os
import logging

from dateutil.relativedelta import relativedelta
from datetime import datetime, date

from services.db_service.mysql_db_service import MySQLDbService
from services.orchestrator.filter import DataFilter
from services.orchestrator.review_listener import ReviewListener
from services.access_control_service import AccessControlService
from services.auth_service import AuthService
from services.data_service import DataService
from services.reporting_service import ReportingService
from packages.llm.classifier import FeedbackClassifier
from packages.tickets.client import MockTicketClient, RealJiraTicketClient
from services.agents.jira_agent import JiraTicketAgent
from services.agents.email_agent import EmailSummaryAgent
from services.statistics_service import StatisticsService
from models.enums.enums import DepartmentToLabels, LabelToDepartment

logger = logging.getLogger(__name__)


class FlightSenseOrchestrator:
    """
    Thin façade that composes domain services.
    """

    def __init__(self, db_service: MySQLDbService, secret_key: str):
        self.db = db_service

        self.access = AccessControlService()
        self.auth = AuthService(self.db, secret_key, self.access)
        self.data = DataService(self.db, self.access)
        self.classifier = FeedbackClassifier()
        self.stats = StatisticsService(self.db)
        
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
        
        self.jira_agent = JiraTicketAgent(ticket_client=ticket_client)
        self.email_agent = EmailSummaryAgent(db=self.db)

        self.reporting = ReportingService(
            self.db, self.access, self.classifier, self.jira_agent, self.email_agent, self.stats
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
        After processing, triggers an immediate statistics update so dashboard shows new data.
        
        Returns:
            Dict with success status and number of reviews processed
        """
        if not self.review_listener:
            return {"success": False, "error": "ReviewListener not available"}
        
        try:
            processed = self.review_listener.check_and_process()
            stats = self.review_listener.get_stats()
            
            # If we processed any reviews, update statistics immediately
            if processed > 0:
                logger.info(f"Triggering immediate statistics update after processing {processed} reviews")
                self._update_recent_statistics()
            
            return {
                "success": True,
                "processed_count": processed,
                "stats": stats,
            }
        except Exception as e:
            logger.error(f"Error processing new reviews: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _update_recent_statistics(self):
        """
        Update statistics for recent time windows to ensure dashboard shows latest data.
        This covers the current hour and the previous hour to catch edge cases.
        """
        try:
            now = datetime.now()
            # Current hour window
            current_hour_end = now.replace(minute=0, second=0, microsecond=0) + relativedelta(hours=1)
            current_hour_start = current_hour_end - relativedelta(hours=1)
            
            # Also update previous hour in case reviews span boundaries
            prev_hour_start = current_hour_start - relativedelta(hours=1)
            
            # Update current hour
            self.db.update_department_statistics(current_hour_start, current_hour_end)
            # Update previous hour
            self.db.update_department_statistics(prev_hour_start, current_hour_start)
            
            logger.info(f"Updated statistics for {prev_hour_start} - {current_hour_end}")
            self.db.upsert_review_status(3, None)
        except Exception as e:
            logger.error(f"Error updating recent statistics: {e}", exc_info=True)
            self.db.upsert_review_status(-1, None)

    def process_review(self, review_row: Dict[str, Any]) -> Dict:
        """
        Process a single review: classify it, persist segments, run automations,
        and update the single-row review_status tracker.

        Status conventions (single-row tracker, id=1):
          - 1: PROCESSING (work started)
          - 2: SEGMENTED (classification done)
          - 3: COMPLETED (automation done / no segments)
          - -1: FAILED
        """
        review_id = review_row.get("id")
        review_text = review_row.get("review", "")

        if not review_text:
            logger.warning(f"Review {review_id} has empty text, skipping")
            return {"success": False, "error": "Empty review text"}

        # Atomically claim the review for processing to prevent concurrent duplicates.
        if review_id is not None and hasattr(self.db, "claim_review_for_processing"):
            claimed = self.db.claim_review_for_processing(int(review_id))
            if not claimed:
                logger.info(
                    "Skipping review id=%s (already claimed or processed).",
                    review_id,
                )
                return {"success": True, "review_id": review_id, "skipped": True}

        # Mark as processing
        if review_id is not None and hasattr(self.db, "upsert_review_status"):
            try:
                self.db.upsert_review_status(1, int(review_id))  # PROCESSING
            except Exception as e:
                logger.warning(
                    "Failed to set review_status=PROCESSING for review id=%s: %s",
                    review_id,
                    e,
                )

        try:
            # Step 1: classify
            logger.info(f"Classifying review id={review_id}")
            result = self.classifier.label_review(review_text)
            if result.get("error"):
                if review_id is not None and hasattr(self.db, "upsert_review_status"):
                    try:
                        self.db.upsert_review_status(-1, int(review_id))  # FAILED
                    except Exception:
                        pass
                if review_id is not None and hasattr(self.db, "upsert_review_processing_status"):
                    try:
                        self.db.upsert_review_processing_status(int(review_id), -1)  # FAILED
                    except Exception:
                        pass
                return {"success": False, "error": result.get("error")}

            segments = result.get("segments", [])

            # No segments: treat as completed
            if not segments:
                logger.warning(f"No segments extracted from review id={review_id}")
                if review_id is not None and hasattr(self.db, "upsert_review_status"):
                    try:
                        self.db.upsert_review_status(3, int(review_id))  # COMPLETED
                    except Exception:
                        pass
                if review_id is not None and hasattr(self.db, "upsert_review_processing_status"):
                    try:
                        self.db.upsert_review_processing_status(int(review_id), 4)  # COMPLETED
                    except Exception:
                        pass
                return {"success": True, "review_id": review_id, "segments_inserted": 0}

            # Step 2: convert to DataFrame and guard for empty
            segments_df = self.classifier.segments_to_table(review_id, segments)
            if segments_df.empty:
                logger.warning(f"Segments DataFrame empty for review id={review_id}")
                if review_id is not None and hasattr(self.db, "upsert_review_status"):
                    try:
                        self.db.upsert_review_status(3, int(review_id))  # COMPLETED
                    except Exception:
                        pass
                if review_id is not None and hasattr(self.db, "upsert_review_processing_status"):
                    try:
                        self.db.upsert_review_processing_status(int(review_id), 4)  # COMPLETED
                    except Exception:
                        pass
                return {"success": True, "review_id": review_id, "segments_inserted": 0}

            # Step 3: persist segments
            inserted = self.db.insert_review_details_bulk(segments_df.to_dict("records"))

            if review_id is not None and hasattr(self.db, "upsert_review_status"):
                try:
                    self.db.upsert_review_status(2, int(review_id))  # SEGMENTED
                except Exception:
                    pass

            # Step 4: automation hooks
            self.reporting.handle_high_priority_automation(review_row, segments)

            if review_id is not None and hasattr(self.db, "upsert_review_status"):
                try:
                    self.db.upsert_review_status(3, int(review_id))  # COMPLETED
                except Exception:
                    pass
            if review_id is not None and hasattr(self.db, "upsert_review_processing_status"):
                try:
                    self.db.upsert_review_processing_status(int(review_id), 4)  # COMPLETED
                except Exception:
                    pass

            logger.info(f"Processed review id={review_id}: inserted {inserted} segments")
            return {
                "success": True,
                "review_id": review_id,
                "segments_inserted": inserted,
            }

        except Exception as e:
            logger.error(f"Error processing review id={review_id}: {e}", exc_info=True)
            if review_id is not None and hasattr(self.db, "upsert_review_status"):
                try:
                    self.db.upsert_review_status(-1, int(review_id))  # FAILED
                except Exception:
                    pass
            if review_id is not None and hasattr(self.db, "upsert_review_processing_status"):
                try:
                    self.db.upsert_review_processing_status(int(review_id), -1)  # FAILED
                except Exception:
                    pass
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

    def push_processed_data(self, token, data) -> Dict:
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
      
    def run_weekly_reporting(self) -> Dict:
        return self.reporting.run_weekly_reports()
    
    def run_monthly_anomaly_reports(self) -> Dict:
        return self.reporting.run_monthly_anomaly_reports()

      # ---------- STATISTICS wrappers ----------

    def get_manager_stats(self, token: str,period: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> Dict:
        """
        Manager dashboard: aggregates all top-level stats in one call.
        """
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}

        # Optionally enforce that only manager/administrator can access this
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
        
        # Get unique reviews count directly from reviews table
        unique_reviews_count = self.db.get_unique_reviews_count(date_from, date_to)
        processed_segments_count = self.db.get_processed_segments_count(date_from, date_to)

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
                "unique_reviews": unique_reviews_count,
                "processed_segments": processed_segments_count,
                "department_distribution": review_count_distribution["department_counts"],
                "sentiment_counts": sentiment["counts"],
                "sentiment_percentages": sentiment["percentage"],
                "priority_counts": priority["counts"],
                "priority_percentages": priority["percentage"],
                "department_sentiment_distribution": sentiment["department_sentiment_distribution"],
                "period_label": period_label,
                "historical_data": historical_data,
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
                "sentiment_counts": sentiment["counts"],
                "sentiment_percentages": sentiment["percentage"],
                "priority_counts": priority["counts"],
                "priority_percentages": priority["percentage"],
                "label_distribution": label_dist,
                "period_label": period_label,
                "historical_data": historical_data,
            },
        }
    
    # ---------- HIGH-PRIORITY wrappers ----------

    def get_department_high_priority_reviews(self, token: str, department: str,limit: int = 5):
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}

        role = user_info.get("role")
        user_dept = user_info.get("department")
        logger.info(
            "[DEBUG] role=%s department=%s",
            role,
            user_dept,
        )
        if not self.access.is_full_access_role(role):
            if user_dept != department:
                return {"success": False, "error": "Forbidden: wrong department"}

        rows = self.db.get_recent_high_priority_reviews_for_department(department_code=department, limit=limit)

        return {
            "success": True,
            "department": department,
            "items": rows,
        }
    
    def get_manager_high_priority_reviews(self, token: str, limit_per_department: int = 3):
        user_info = self.verify_token(token)
        if not user_info:
            return {"success": False, "error": "Unauthorized"}

        role = user_info.get("role")
        if not self.access.is_full_access_role(role):
            return {"success": False, "error": "Forbidden: manager access required"}

        data = self.db.get_manager_high_priority_overview(limit_per_department=limit_per_department)

        return {
            "success": True,
            "departments": data,
        }


    def run_statistics_job(self, start_dt: datetime, end_dt: datetime) -> Dict:
        """
        Run the statistics aggregation job for a specific time range.
        """
        if not hasattr(self.db, 'update_department_statistics'):
             return {"success": False, "error": "Database service does not support statistics update"}
        
        try:
            self.db.update_department_statistics(start_dt, end_dt)
            return {"success": True, "message": f"Statistics updated for {start_dt} - {end_dt}"}
        except Exception as e:
            logger.error(f"Error running statistics job: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.db.upsert_review_status(3, None)
