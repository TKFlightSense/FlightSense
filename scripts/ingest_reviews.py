import os
import sys
import argparse
import pandas as pd
import requests
import numpy as np
from dotenv import load_dotenv

# Add parent directory to path to allow importing services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service.mysql_db_service import MySQLDbService

# Load environment variables from .env file
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def ingest_reviews(csv_file, username, password):
    print(f"--- FlightSense Review Ingestion Tool ---")
    
    # 1. Read CSV
    if not os.path.exists(csv_file):
        print(f"[ERROR] File not found: {csv_file}")
        return

    print(f"[1] Reading CSV file: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return

    # Validate columns
    required_col = 'review'
    if required_col not in df.columns:
        print(f"[ERROR] CSV must contain a '{required_col}' column.")
        return

    # Fill missing optional columns
    if 'date' not in df.columns:
        print("    [INFO] Generating random dates for the last 7 days...")
        
        # 1. Define the time window
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=7)
        
        # 2. Calculate the total range in seconds
        time_range_seconds = (end_date - start_date).total_seconds()
        
        # 3. Generate random seconds for each row
        random_seconds = np.random.randint(0, int(time_range_seconds), size=len(df))
        
        # 4. Add random seconds to the start_date
        random_dates = start_date + pd.to_timedelta(random_seconds, unit='s')
        
        # 5. Assign to dataframe (formatting as YYYY-MM-DD strings)
        df['date'] = random_dates.strftime('%Y-%m-%d')    
    if 'flight_number' not in df.columns:
            df['flight_number'] = None
    if 'pnr' not in df.columns:
        df['pnr'] = "TSTPNR"

    print(f"    Found {len(df)} reviews to ingest.")

    # 2. Push to Database
    print("[2] Pushing reviews to database...")
    try:
        db = MySQLDbService()
        count = db.push_processed_data(df)
        print(f"    [SUCCESS] Inserted {count} rows into 'reviews' table.")
        db.close()
    except Exception as e:
        print(f"    [ERROR] Database operation failed: {e}")
        return

    # 3. Authenticate with API
    print("[3] Authenticating with API...")
    login_url = f"{API_URL}/api/auth/login"
    try:
        resp = requests.post(login_url, json={"username": username, "password": password})
        if resp.status_code != 200:
            print(f"    [ERROR] Login failed: {resp.status_code} - {resp.text}")
            return
        
        token = resp.json().get("token")
        print("    [SUCCESS] Authenticated successfully.")
    except Exception as e:
        print(f"    [ERROR] Failed to connect to API: {e}")
        return

    # 4. Trigger Listener
    print("[4] Triggering Review Listener...")
    run_url = f"{API_URL}/api/listener/run"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.post(run_url, headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            processed = result.get("processed_this_batch", 0)
            print(f"    [SUCCESS] Listener triggered successfully.")
            print(f"    Processed {processed} new reviews.")
        elif resp.status_code == 503:
             print(f"    [WARNING] Listener not available (Service Unavailable). Check server logs.")
        else:
            print(f"    [ERROR] Listener trigger failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"    [ERROR] Failed to call listener endpoint: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest reviews from CSV and trigger listener")
    parser.add_argument("csv_file", help="Path to the CSV file containing reviews")
    parser.add_argument("--username", required=True, help="API Username for authentication")
    parser.add_argument("--password", required=True, help="API Password for authentication")
    
    args = parser.parse_args()
    
    ingest_reviews(args.csv_file, args.username, args.password)