"""
FlightSense Review Status Tracker
=================================
Streamlit UI for demoing review processing status in real-time.

Behavior:
- Polls only when tracking_enabled flag is true in review_status.
- Each poll reads the latest row from review_status (review_id + status).
- When status reaches terminal, tracking stops automatically by clearing flag.

Tables:
- review_status (review_id FK -> reviews.id, status INT)
- review_status (id=1, tracking_enabled)
- reviews (id, review, flight_number, pnr, date)
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh 
import mysql.connector
from mysql.connector import Error
import os
import time
from typing import Optional, Dict, Any

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            database=os.getenv("MYSQL_DATABASE", "flightsense"),
            user=os.getenv("MYSQL_USER", "flightsense"),
            password=os.getenv("MYSQL_PASSWORD", "flightsense123")
        )
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None


# =============================================================================
# DATABASE QUERIES
# =============================================================================

def get_tracking_flag() -> bool:
    query = "SELECT tracking_enabled FROM review_status WHERE id = 1 LIMIT 1"
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        return bool(row[0]) if row else False
    except Error as e:
        st.error(f"Query error: {e}")
        return False
    finally:
        conn.close()


def set_tracking_flag(value: bool) -> None:
    query = "UPDATE review_status SET tracking_enabled = %s WHERE id = 1"
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(query, (1 if value else 0,))
        conn.commit()
        cursor.close()
    except Error as e:
        st.error(f"Update error: {e}")
    finally:
        conn.close()


def get_latest_review_status() -> Optional[Dict[str, Any]]:
    query = """
    SELECT
        rs.review_id,
        rs.status,
        rs.tracking_enabled,
        r.review,
        r.flight_number,
        r.pnr,
        r.date
    FROM review_status rs
    JOIN reviews r ON r.id = rs.review_id
    WHERE rs.id = 1
    LIMIT 1
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        return row
    except Error as e:
        st.error(f"Query error: {e}")
        return None
    finally:
        conn.close()



# =============================================================================
# STATUS DISPLAY
# =============================================================================

STATUS_MAP = {
    0: {"label": "Arrived", "color": "#6b7280", "description": "Review received."},
    1: {"label": "Segmented and Labeled", "color": "#f59e0b", "description": "LLM processing complete."},
    2: {"label": "Relevant department obtained", "color": "#3b82f6", "description": "Routed to department."},
    3: {"label": "Completed", "color": "#22c55e", "description": "Processing finished."},
}

TERMINAL_STATUS = 3


def render_status_timeline(current_status: int):
    stages = [0, 1, 2, 3]
    for s in stages:
        meta = STATUS_MAP.get(s, STATUS_MAP[0])
        if s < current_status:
            state = "completed"
        elif s == current_status:
            state = "active"
        else:
            state = "pending"

        st.markdown(
            f"<div class='timeline-step {state}'>"
            f"<strong>{meta['label']}</strong> - {meta['description']}"
            f"</div>",
            unsafe_allow_html=True,
        )


# =============================================================================
# PAGE STYLING
# =============================================================================

def apply_thy_branding():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        .status-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .timeline-step {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            color: #cbd5e1;
        }
        .timeline-step.active {
            color: #b7312c;
            font-weight: bold;
        }
        .timeline-step.completed {
            color: #22c55e;
        }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    st.set_page_config(
        page_title="FlightSense - Review Status",
        page_icon="Гo^Лў?",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    poll_seconds = int(os.getenv("REVIEW_STATUS_POLL_SECONDS", "2"))
    st_autorefresh(interval=poll_seconds * 1000, key="status_autorefresh")

    apply_thy_branding()

    st.title("Review Status Tracker")
    st.markdown("Tracks the latest review status from the database.")

    tracking_enabled = get_tracking_flag()  

    if tracking_enabled:
        status_row = get_latest_review_status()
        if not status_row:
            st.warning("No status found yet.")
            return

        status_code = int(status_row.get("status", 0))
        status_meta = STATUS_MAP.get(status_code, STATUS_MAP[0])

        st.markdown(
            f"<div class='status-card'>"
            f"<h3>Current Status: {status_meta['label']}</h3>"
            f"<p>{status_meta['description']}</p>"
            f"</div>",
            unsafe_allow_html=True
        )

        st.write("Review details")
        st.write(f"Review ID: {status_row.get('review_id')}")
        st.write(f"PNR: {status_row.get('pnr')}")
        st.write(f"Flight: {status_row.get('flight_number')}")
        st.write(f"Date: {status_row.get('date')}")
        st.write(f"Text: {status_row.get('review')}")

        st.markdown("---")
        render_status_timeline(status_code)

        if status_code >= TERMINAL_STATUS:
            st.success("Processing completed. Tracking stopped.")
            # set_tracking_flag(False)
    else:
        st.info("Waiting for tracking flag to turn on...")

if __name__ == "__main__":
    main()
