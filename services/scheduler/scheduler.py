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
