"""
Debug Script to Check Database State and Statistics

This script helps diagnose why reviews might not be showing on the dashboard.

For local development (outside Docker), set environment variables:
  export MYSQL_HOST=localhost
  export MYSQL_PORT=3306
  export MYSQL_DATABASE=flightsense
  export MYSQL_USER=flightsense
  export MYSQL_PASSWORD=rootroot

Or run inside Docker:
  docker exec -it flightsense-app python scripts/debug_database.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set default MySQL credentials for local development if not set
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

def debug_database():
    print("=" * 70)
    print("  FlightSense Database Debug")
    print("=" * 70)
    
    # Initialize database
    print("\n[1] Connecting to database...")
    try:
        db = MySQLDbService()
        print("    Connected successfully.")
    except Exception as e:
        print(f"    [ERROR] Failed to connect: {e}")
        return
    
    conn = db._get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check reviews table
    print("\n[2] Reviews table:")
    cursor.execute("SELECT COUNT(*) as count FROM reviews")
    result = cursor.fetchone()
    print(f"    Total reviews: {result['count']}")
    
    cursor.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 5")
    reviews = cursor.fetchall()
    if reviews:
        print("    Latest 5 reviews:")
        for r in reviews:
            print(f"      ID={r['id']} | Date={r['date']} | Flight={r['flight_number']} | Text={str(r['review'])[:40]}...")
    
    # Check processed_reviews table
    print("\n[3] Processed Reviews table:")
    cursor.execute("SELECT COUNT(*) as count FROM processed_reviews")
    result = cursor.fetchone()
    print(f"    Total processed segments: {result['count']}")
    
    cursor.execute("""
        SELECT label, sentiment, priority, COUNT(*) as count 
        FROM processed_reviews 
        GROUP BY label, sentiment, priority
        ORDER BY count DESC
        LIMIT 10
    """)
    segments = cursor.fetchall()
    if segments:
        print("    Top 10 label/sentiment/priority combinations:")
        for s in segments:
            print(f"      {s['label']:<35} | {s['sentiment']:<10} | {s['priority']:<8} | Count: {s['count']}")
    
    # Check unprocessed reviews
    print("\n[4] Unprocessed Reviews (reviews without segments):")
    cursor.execute("""
        SELECT r.id, r.review, r.date
        FROM reviews r
        LEFT JOIN processed_reviews pr ON r.id = pr.review_id
        WHERE pr.id IS NULL
        LIMIT 5
    """)
    unprocessed = cursor.fetchall()
    print(f"    Found {len(unprocessed)} unprocessed (showing up to 5):")
    for r in unprocessed:
        print(f"      ID={r['id']} | Date={r['date']} | Text={str(r['review'])[:50]}...")
    
    # Check department statistics tables
    print("\n[5] Department Statistics Tables:")
    dept_tables = ['kabin_hizmetleri', 'ikram_ucak_ici', 'yer_isletme_bagaj', 'tgs', 'rez_biletleme', 'cagri_merkezi']
    
    for table in dept_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            
            cursor.execute(f"""
                SELECT SUM(positive_count) as pos, SUM(negative_count) as neg, SUM(neutral_count) as neu
                FROM {table}
            """)
            sums = cursor.fetchone()
            pos = sums['pos'] or 0
            neg = sums['neg'] or 0
            neu = sums['neu'] or 0
            
            print(f"    {table:<25} | Rows: {count:>4} | Pos: {pos:>4} | Neg: {neg:>4} | Neu: {neu:>4}")
            
            # Show date ranges in the table
            if count > 0:
                cursor.execute(f"SELECT MIN(date_from) as min_date, MAX(date_to) as max_date FROM {table}")
                dates = cursor.fetchone()
                print(f"      Date range: {dates['min_date']} to {dates['max_date']}")
        except Exception as e:
            print(f"    {table}: [ERROR] {e}")
    
    # Check what the dashboard would query
    print("\n[6] Simulating Dashboard Query (Last 30 days):")
    now = datetime.now()
    date_to = now
    date_from = now - timedelta(days=30)
    print(f"    Query range: {date_from} to {date_to}")
    
    for table in dept_tables:
        try:
            # This is how the dashboard queries
            cursor.execute(f"""
                SELECT SUM(positive_count + negative_count + neutral_count) as total
                FROM {table}
                WHERE date_from >= %s AND date_to <= %s
            """, (date_from, date_to))
            result = cursor.fetchone()
            total = result['total'] or 0
            print(f"    {table:<25} | Total matching: {total}")
            
            # Debug: show what date ranges exist
            cursor.execute(f"""
                SELECT date_from, date_to, SUM(positive_count + negative_count + neutral_count) as total
                FROM {table}
                GROUP BY date_from, date_to
                ORDER BY date_from DESC
                LIMIT 3
            """)
            ranges = cursor.fetchall()
            if ranges:
                for r in ranges:
                    in_range = "✓" if r['date_from'] >= date_from and r['date_to'] <= date_to else "✗"
                    print(f"      {in_range} {r['date_from']} - {r['date_to']} | Total: {r['total']}")
        except Exception as e:
            print(f"    {table}: [ERROR] {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("  Debug Complete")
    print("=" * 70)

if __name__ == "__main__":
    debug_database()
