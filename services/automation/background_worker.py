import time
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from services.db_service.mysql_db_service import MySQLDbService
from services.orchestrator.orchestrator import FlightSenseOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("BackgroundWorker")

def main():
    logger.info("Starting FlightSense Background Worker...")
    
    # Initialize services
    try:
        db_service = MySQLDbService()
        secret_key = os.getenv("JWT_SECRET", "default-secret-key")
        orchestrator = FlightSenseOrchestrator(db_service, secret_key)
        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize services: {e}")
        sys.exit(1)

    # Track last stats update time and weekly report time
    last_weekly_run = datetime.min
    last_stats_update = datetime.min

    # Weekly schedule (default: Monday 06:00)
    weekly_run_weekday = int(os.getenv("WEEKLY_REPORT_WEEKDAY", "0"))  # 0 = Monday
    weekly_run_hour = int(os.getenv("WEEKLY_REPORT_HOUR", "6"))
    weekly_run_minute = int(os.getenv("WEEKLY_REPORT_MINUTE", "0"))
    # Main loop
    while True:
        try:
            # 1. Process New Reviews (Immediate)
            logger.debug("Checking for new reviews...")
            result = orchestrator.process_new_reviews()
            
            if result.get("success") and result.get("processed_count", 0) > 0:
                count = result["processed_count"]
                logger.info(f"Successfully processed {count} new reviews.")
            
            # 2. Periodic Statistics Update (Hourly)
            now = datetime.now()
            if now - last_stats_update > timedelta(seconds=10):
                logger.info("Running scheduled hourly statistics update...")
                
                # Calculate the last full hour window
                end_dt = now.replace(minute=0, second=0, microsecond=0)
                start_dt = end_dt - timedelta(hours=1)
                
                stats_result = orchestrator.run_statistics_job(start_dt, end_dt)
                
                if stats_result.get("success"):
                    logger.info(f"Hourly statistics updated: {stats_result.get('message')}")
                    last_stats_update = now
                else:
                    logger.error(f"Failed to update statistics: {stats_result.get('error')}")

            # 3. Weekly Reports (Configurable)
            weekly_scheduled = now.replace(
                hour=weekly_run_hour,
                minute=weekly_run_minute,
                second=0,
                microsecond=0,
            )
            weekly_scheduled -= timedelta(
                days=(weekly_scheduled.weekday() - weekly_run_weekday) % 7
            )

            if now >= weekly_scheduled and last_weekly_run < weekly_scheduled:
                logger.info("Running scheduled weekly reports...")
                last_weekly_run = weekly_scheduled  # mark before sending to avoid repeats
                weekly_result = orchestrator.run_weekly_reporting()

                if weekly_result.get("success"):
                    logger.info(f"Weekly reports sent: {weekly_result.get('message')}")
                    last_weekly_run = now
                else:
                    logger.error(f"Failed to send weekly reports: {weekly_result.get('error')}")

        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        
        # Sleep for a short interval to simulate "immediate" processing
        # 10 seconds is a reasonable balance between latency and load
        time.sleep(10)
        ## TODO Wire weekly trigger: extend background_worker.py to track last-weekly-run and, e.g., fire every Monday at 06:00 (configurable), calling a new reporting entrypoint.
if __name__ == "__main__":
    main()
