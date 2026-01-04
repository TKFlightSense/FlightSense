import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service.mysql_db_service import MySQLDbService

load_dotenv()

print(f"--- FlightSense Airport Ingestion Tool ---")
    
db_service = MySQLDbService()
try:
    db_service.ingest_airport_coord()
    print(f"[SUCCESS] Airport ingestion completed.")
except Exception as e:
    print(f"[ERROR] Failed to ingest airports: {e}")