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
    handlers=[logging.StreamHandler(sys.stdout)]
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

    # Track last stats update time
    last_stats_update = datetime.min

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
            if now - last_stats_update > timedelta(hours=1):
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

        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        
        # Sleep for a short interval to simulate "immediate" processing
        # 10 seconds is a reasonable balance between latency and load
        time.sleep(10)

if __name__ == "__main__":
    main()
