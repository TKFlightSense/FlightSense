"""
ReviewListener: Monitors the reviews table for new entries and delegates
processing to the orchestrator.

This listener is synchronous and event-driven, not thread-based.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Callable, Optional
import logging

from services.db_service.mysql_db_service import MySQLDbService

if TYPE_CHECKING:
    from services.orchestrator.orchestrator import FlightSenseOrchestrator

logger = logging.getLogger(__name__)


class ReviewListener:
    """
    Listener that checks the reviews table for unprocessed rows and delegates
    processing to the orchestrator.
    
    This is a synchronous, on-demand utility (not background polling).
    Call check_and_process() manually when you want to process new reviews.
    
    Supports registering callbacks that are triggered when new reviews are detected.
    
    Usage:
        listener = ReviewListener(db_service, orchestrator)
        listener.on_new_reviews(my_callback)  # Register a callback
        listener.check_and_process()          # Process reviews on-demand
    """

    def __init__(
        self,
        db_service: MySQLDbService,
        orchestrator: FlightSenseOrchestrator,
        batch_size: int = 10,
    ):
        """
        Initialize the ReviewListener.

        Args:
            db_service: MySQLDbService instance for DB access
            orchestrator: FlightSenseOrchestrator instance to handle processing
            batch_size: Max reviews to process per call (default: 10)
        """
        self.db = db_service
        self.orchestrator = orchestrator
        self.batch_size = batch_size
        self.processed_count = 0
        
        # Callback functions to notify when new reviews are detected
        self.callbacks: List[Callable[[List[Dict[str, Any]]], None]] = []

        logger.info(
            f"ReviewListener initialized (batch_size={batch_size})"
        )

    def on_new_reviews(self, callback: Callable[[List[Dict[str, Any]]], None]) -> None:
        """
        Register a callback function to be called when new reviews are detected.
        
        The callback will be invoked with a list of newly detected review rows.
        Example:
            def my_callback(reviews):
                print(f"New reviews detected: {len(reviews)}")
            
            listener.on_new_reviews(my_callback)
        
        Args:
            callback: Function that accepts a list of review dicts
        """
        self.callbacks.append(callback)
        logger.info(f"Registered callback: {callback.__name__}")

    def _invoke_callbacks(self, unprocessed_reviews: List[Dict[str, Any]]) -> None:
        """Invoke all registered callbacks with the new reviews."""
        if not self.callbacks:
            return
        
        for callback in self.callbacks:
            try:
                callback(unprocessed_reviews)
            except Exception as e:
                logger.error(f"Error invoking callback {callback.__name__}: {e}", exc_info=True)

    def check_and_process(self) -> int:
        """
        Check for new reviews and process them (on-demand, synchronous).
        
        Returns:
            Number of reviews processed in this call
        """
        try:
            # Get unprocessed reviews (reviews with no corresponding row in processed_reviews)
            unprocessed = self._get_unprocessed_reviews()

            if not unprocessed:
                return 0

            logger.info(f"Found {len(unprocessed)} unprocessed reviews")

            # Invoke registered callbacks to notify listeners of new data
            self._invoke_callbacks(unprocessed)

            processed_this_batch = 0
            for review_row in unprocessed:
                try:
                    self._process_single_review(review_row)
                    self.processed_count += 1
                    processed_this_batch += 1
                except Exception as e:
                    logger.error(
                        f"Error processing review id={review_row.get('id')}: {e}",
                        exc_info=True,
                    )

            return processed_this_batch

        except Exception as e:
            logger.error(f"Error checking for unprocessed reviews: {e}", exc_info=True)
            return 0

    def _get_unprocessed_reviews(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get reviews that don't have corresponding entries in processed_reviews.
        Uses a LEFT JOIN to find unprocessed rows, and skips rows that have been
        marked as completed/failed in review_status.
        """
        limit = limit or self.batch_size

        query = f"""
        SELECT r.id, r.review, r.date, r.flight_number, r.pnr
        FROM reviews r
        LEFT JOIN processed_reviews pr ON r.id = pr.review_id
        LEFT JOIN review_status rs ON r.id = rs.review_id
        WHERE pr.id IS NULL
          AND (rs.status IS NULL OR rs.status = 0)
        LIMIT {limit}
        """

        try:
            # Use execute_query from db_service (if available) or fallback
            # For MySQLDbService, we need to build a custom query runner
            import mysql.connector
            from mysql.connector import Error

            conn = self.db._get_connection()
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query)
                rows = cursor.fetchall()
                cursor.close()
                return rows if rows else []
            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error querying unprocessed reviews: {e}")
            return []

    def _process_single_review(self, review_row: Dict[str, Any]) -> None:
        """
        Process a single review by delegating to the orchestrator.

        Args:
            review_row: Dict with keys: id, review, date, flight_number, pnr
        """
        review_id = review_row.get("id")
        review_text = review_row.get("review", "")

        if not review_text:
            logger.warning(f"Review {review_id} has empty text, skipping")
            return

        # Delegate all processing to orchestrator
        logger.info(f"Delegating review id={review_id} to orchestrator for processing")
        try:
            result = self.orchestrator.process_review(review_row)
            if isinstance(result, dict) and not result.get("success", False):
                raise RuntimeError(result.get("error") or "Orchestrator returned success=false")
        except Exception as e:
            logger.error(f"Error processing review id={review_id} via orchestrator: {e}", exc_info=True)
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Return listener statistics."""
        return {
            "processed_count": self.processed_count,
            "batch_size": self.batch_size,
            "callbacks_registered": len(self.callbacks),
        }
