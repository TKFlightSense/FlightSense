"""
Test Script to Add Reviews to the Database

This script inserts sample reviews into the reviews table for testing.
Usage: python scripts/add_test_reviews.py [--count N] [--days N]

For local development (outside Docker), set environment variables:
  export MYSQL_HOST=localhost
  export MYSQL_PORT=3306
  export MYSQL_DATABASE=flightsense
  export MYSQL_USER=flightsense
  export MYSQL_PASSWORD=rootroot

Or run inside Docker:
  docker exec -it flightsense-app python scripts/add_test_reviews.py --count 20
"""

import os
import sys
import argparse
from datetime import date, datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set default MySQL credentials for local development if not set
# These match the docker-compose.yml defaults
if not os.getenv("MYSQL_HOST"):
    os.environ["MYSQL_HOST"] = "localhost"
if not os.getenv("MYSQL_PORT"):
    os.environ["MYSQL_PORT"] = "3306"
if not os.getenv("MYSQL_DATABASE"):
    os.environ["MYSQL_DATABASE"] = "flightsense"
if not os.getenv("MYSQL_USER"):
    os.environ["MYSQL_USER"] = "flightsense"
if not os.getenv("MYSQL_PASSWORD"):
    os.environ["MYSQL_PASSWORD"] = "rootroot"

from services.db_service.mysql_db_service import MySQLDbService

# Sample reviews covering different labels
SAMPLE_REVIEWS = [
    # Inflight Experience - Food & Beverage
    "The food was absolutely delicious! Best airline meal I've ever had. The Turkish coffee was perfect.",
    "The meal was cold and tasteless. Very disappointed with the catering service.",
    "Loved the wide selection of beverages. The wine collection was impressive.",
    
    # Inflight Experience - Seats & Comfort  
    "The business class seats were incredibly comfortable. Slept like a baby on my 10-hour flight.",
    "Economy seats are too cramped. My knees were touching the seat in front the whole flight.",
    "The legroom in premium economy is excellent. Would definitely pay extra for this again.",
    
    # Inflight Experience - Entertainment
    "Great movie selection on the entertainment system. Watched three new releases!",
    "The entertainment screen was broken and crew couldn't fix it. Very boring 8-hour flight.",
    "WiFi worked perfectly throughout the flight. Was able to join my work meeting.",
    
    # Inflight Experience - Cabin Service
    "The cabin crew was exceptional. So friendly and attentive to all passengers.",
    "Flight attendants seemed rushed and uninterested. Had to ask multiple times for water.",
    "Crew handled a medical emergency professionally. Very impressed with their training.",
    
    # Inflight Experience - Cleanliness
    "Aircraft was spotless. Toilets were clean even after a long flight.",
    "Found crumbs and trash in my seat pocket from previous flight. Disgusting!",
    "The blankets smelled fresh and the cabin was very clean.",
    
    # Check-in Process
    "Online check-in was smooth and easy. Took less than 2 minutes.",
    "Check-in counter had only 2 staff for 200 passengers. Waited over an hour!",
    "The mobile app check-in crashed three times before finally working.",
    
    # Boarding Process
    "Boarding was organized and efficient. Loved the priority boarding for families.",
    "Boarding was chaotic. No one followed the zone system and crew didn't enforce it.",
    "Gate change announced 5 minutes before boarding with no explanation.",
    
    # Baggage - Lost
    "My luggage was lost for 3 days. No one could tell me where it was.",
    "Bag didn't arrive but staff were helpful and delivered it to my hotel next day.",
    
    # Baggage - Damaged
    "My suitcase arrived with a broken wheel. No compensation offered.",
    "Handle of my bag was torn off during transit. Very careless baggage handling.",
    
    # Booking and Ticketing
    "Website booking was simple and prices were transparent. No hidden fees.",
    "Tried to change my flight and was charged an outrageous fee.",
    "Got a great deal through the mobile app. Easy payment process.",
    
    # Customer Support
    "Called customer service and waited 45 minutes before anyone answered.",
    "The support team resolved my issue quickly. Very professional and helpful.",
    "Chat support was useless. Bot couldn't understand my question and no human available.",
    
    # Pricing and Loyalty
    "Miles program is excellent. Redeemed my points for a free upgrade!",
    "Ticket prices keep changing every hour. Impossible to plan a budget.",
    "Elite status benefits are great. Lounge access makes layovers bearable.",
]

def add_reviews(count: int = 10, days_back: int = 7):
    """
    Add sample reviews to the database.
    
    Args:
        count: Number of reviews to add
        days_back: Spread reviews over this many days back from today
    """
    print("=" * 60)
    print("  Adding Test Reviews to Database")
    print("=" * 60)
    
    # Initialize database
    print("\n[1] Connecting to database...")
    try:
        db = MySQLDbService()
        print("    Connected successfully.")
    except Exception as e:
        print(f"    [ERROR] Failed to connect: {e}")
        return
    
    # Generate flight numbers
    airlines = ["TK"]
    
    # Add reviews
    print(f"\n[2] Inserting {count} reviews...")
    inserted_ids = []
    
    for i in range(count):
        # Random review from samples
        review_text = random.choice(SAMPLE_REVIEWS)
        
        # Random date within the last N days
        days_ago = random.randint(0, days_back)
        review_date = (datetime.now() - timedelta(days=days_ago)).date()
        
        # Random flight number
        flight_num = f"{random.choice(airlines)}{random.randint(100, 999)}"
        
        # Random PNR
        pnr = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        
        try:
            review_id = db.insert_processed_data_row(
                review=review_text,
                date=review_date.isoformat(),
                flight_number=flight_num,
                pnr=pnr
            )
            inserted_ids.append(review_id)
            print(f"    [{i+1}/{count}] ID={review_id} | {flight_num} | {review_date} | {review_text[:50]}...")
        except Exception as e:
            print(f"    [ERROR] Failed to insert review {i+1}: {e}")
    
    print(f"\n[3] Summary:")
    print(f"    Total inserted: {len(inserted_ids)}")
    print(f"    Review IDs: {inserted_ids}")
    
    # Check current table counts
    print("\n[4] Current table counts:")
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM reviews")
        reviews_count = cursor.fetchone()[0]
        print(f"    reviews: {reviews_count}")
        
        cursor.execute("SELECT COUNT(*) FROM processed_reviews")
        processed_count = cursor.fetchone()[0]
        print(f"    processed_reviews: {processed_count}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"    [ERROR] Failed to get counts: {e}")
    
    print("\n" + "=" * 60)
    print("  Done! Reviews added to 'reviews' table.")
    print("  The ReviewListener will process them automatically.")
    print("=" * 60)
    
    return inserted_ids

def main():
    parser = argparse.ArgumentParser(description='Add test reviews to the database')
    parser.add_argument('--count', '-c', type=int, default=10, help='Number of reviews to add (default: 10)')
    parser.add_argument('--days', '-d', type=int, default=7, help='Spread reviews over this many days (default: 7)')
    args = parser.parse_args()
    
    add_reviews(count=args.count, days_back=args.days)

if __name__ == "__main__":
    main()
