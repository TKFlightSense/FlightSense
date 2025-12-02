import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from services.orchestrator.orchestrator import FlightSenseOrchestrator

logger = logging.getLogger(__name__)

class StatisticsScheduler:
    """
    Simple background scheduler to run statistics aggregation jobs.
    """
    def __init__(self, orchestrator: FlightSenseOrchestrator, interval_seconds: int = 3600):
        self.orchestrator = orchestrator
        self.interval_seconds = interval_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"StatisticsScheduler started (interval={self.interval_seconds}s)")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("StatisticsScheduler stopped")

    async def _loop(self):
        while self.running:
            try:
                # Calculate the last hour window
                now = datetime.now()
                # Round down to the nearest hour for cleaner buckets
                end_dt = now.replace(minute=0, second=0, microsecond=0)
                start_dt = end_dt - timedelta(hours=1)
                
                logger.info(f"Running scheduled statistics job for {start_dt} - {end_dt}")
                
                # Run the job in a separate thread to avoid blocking the event loop
                await asyncio.to_thread(self.orchestrator.run_statistics_job, start_dt, end_dt)
                
            except Exception as e:
                logger.error(f"Error in statistics scheduler loop: {e}", exc_info=True)
            
            # Wait for next interval
            await asyncio.sleep(self.interval_seconds)


class ReviewListenerScheduler:
    """
    Background scheduler that continuously polls for new reviews and processes them.
    Runs the review listener at a configurable interval to ensure new reviews
    are processed automatically without manual intervention.
    """
    def __init__(self, orchestrator: FlightSenseOrchestrator, poll_interval_seconds: int = 30):
        """
        Initialize the ReviewListenerScheduler.
        
        Args:
            orchestrator: FlightSenseOrchestrator instance
            poll_interval_seconds: How often to check for new reviews (default: 30 seconds)
        """
        self.orchestrator = orchestrator
        self.poll_interval_seconds = poll_interval_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.total_processed = 0

    async def start(self):
        """Start the background review listener."""
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"ReviewListenerScheduler started (poll_interval={self.poll_interval_seconds}s)")

    async def stop(self):
        """Stop the background review listener."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"ReviewListenerScheduler stopped (total processed: {self.total_processed})")

    async def _loop(self):
        """Main polling loop that checks for and processes new reviews."""
        while self.running:
            try:
                # Run the review processing in a separate thread to avoid blocking
                result = await asyncio.to_thread(self.orchestrator.process_new_reviews)
                
                if result.get("success"):
                    processed = result.get("processed_this_batch", 0)
                    if processed > 0:
                        self.total_processed += processed
                        logger.info(f"ReviewListener processed {processed} new reviews (total: {self.total_processed})")
                else:
                    error = result.get("error", "Unknown error")
                    if error != "ReviewListener not available":
                        logger.warning(f"ReviewListener error: {error}")
                        
            except Exception as e:
                logger.error(f"Error in review listener loop: {e}", exc_info=True)
            
            # Wait before next poll
            await asyncio.sleep(self.poll_interval_seconds)

    def get_stats(self) -> dict:
        """Get scheduler statistics."""
        return {
            "running": self.running,
            "poll_interval_seconds": self.poll_interval_seconds,
            "total_processed": self.total_processed,
        }
