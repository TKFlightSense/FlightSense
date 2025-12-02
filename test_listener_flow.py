"""
Test Script for FlightSense Listener Flow

This script verifies the end-to-end flow:
1. Insert a raw review into the database.
2. Trigger the ReviewListener to process it.
3. Verify that segments were created in the processed_reviews table.
"""

import os
import sys
import logging
from datetime import date

# Add parent directory to path so we can import the project packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db_service.mysql_db_service import MySQLDbService
from services.orchestrator.orchestrator import FlightSenseOrchestrator
from services.orchestrator.review_listener import ReviewListener

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_flow() -> None:
    print("=" * 60)
    print("  FlightSense Listener Flow Test")
    print("=" * 60)

    # 1. Initialize Services
    print("\n[1] Initializing services...")
    try:
        db = MySQLDbService(
            host="localhost",
        port=3306,
        database="flightsense",
        user="flightsense",
        password="rootroot",
    )
        # Optional: show which DB we connected to
        try:
            print(
                f"    Using MySQL DB: {db.user}@{db.host}:{db.port}/{db.database}"
            )
        except Exception:
            # If attributes don't exist for some reason, just ignore
            pass

        # We need a dummy secret for orchestrator init
        orch = FlightSenseOrchestrator(db, "test-secret")
        listener = ReviewListener(db, orch)
        print("    Services initialized successfully.")
    except Exception as e:
        print(f"    [ERROR] Failed to initialize services: {e}")
        return

    # 2. Insert Raw Review
    print("\n[2] Inserting raw review...")
    test_review = (
        "The cabin crew was excellent, very attentive. "
        "However, the meal was cold and tasteless."
    )
    flight_num = "TEST-999"

    try:
        review_id = db.insert_processed_data_row(
            review=test_review,
            date=date.today().isoformat(),
            flight_number=flight_num,
            pnr="TESTPNR",
        )
        print(f"    Inserted review ID: {review_id}")
        print(f"    Content: '{test_review}'")
    except Exception as e:
        print(f"    [ERROR] Failed to insert review: {e}")
        return

    # 3. Trigger Listener
    print("\n[3] Triggering ReviewListener...")
    try:
        # Register a callback to see if it fires
        def on_new_reviews(reviews):
            print(f"    [CALLBACK] Listener detected {len(reviews)} new reviews!")

        listener.on_new_reviews(on_new_reviews)

        # Process
        count = listener.check_and_process()
        print(f"    Listener processed {count} reviews.")

        if count == 0:
            print("    [WARNING] Listener processed 0 reviews. Is the review already processed?")
    except Exception as e:
        print(f"    [ERROR] Listener failed: {e}")
        return

    # 4. Verify Results
    print("\n[4] Verifying results in DB...")
    try:
        # Query processed_reviews for this review_id
        conn = db._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM processed_reviews WHERE review_id = %s",
            (review_id,),
        )
        segments = cursor.fetchall()
        cursor.close()
        conn.close()

        if segments:
            print(f"    [SUCCESS] Found {len(segments)} segments for review {review_id}:")
            for seg in segments:
                print(
                    f"      - Label: {seg['label']:<30} | "
                    f"Sentiment: {seg['sentiment']:<10} | "
                    f"Priority: {seg['priority']}"
                )
        else:
            print("    [FAILURE] No segments found in processed_reviews table.")

    except Exception as e:
        print(f"    [ERROR] Verification failed: {e}")

    print("\n" + "=" * 60)
    print("  Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_flow()