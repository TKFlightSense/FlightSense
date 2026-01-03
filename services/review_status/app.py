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
        EXISTS(
            SELECT 1
            FROM processed_reviews pr
            WHERE pr.review_id = rs.review_id
              AND UPPER(pr.priority) = 'HIGH'
        ) AS is_high_priority,
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
    0: {"label": "Arrived", "description": "Review received."},
    1: {"label": "Segmented and Labeled", "description": "LLM processing complete."},
    2: {"label": "Relevant department obtained", "description": "Routed to department."},
    3: {"label": "Completed", "description": "Processing finished."},
}

TERMINAL_STATUS = 3


def render_status_boxes(current_status: int) -> None:
    """Render 4 status boxes; each box turns green when reached."""
    stages = [0, 1, 2, 3]
    cols = st.columns(len(stages))

    for col, stage in zip(cols, stages):
        meta = STATUS_MAP.get(stage, STATUS_MAP[0])
        reached = current_status >= stage
        state_class = "reached" if reached else "pending"

        with col:
            st.markdown(
                """
                <div class="status-box {state_class}">
                  <div class="status-box-title">{title}</div>
                  <div class="status-box-desc">{desc}</div>
                </div>
                """.format(
                    state_class=state_class,
                    title=meta["label"],
                    desc=meta["description"],
                ),
                unsafe_allow_html=True,
            )


# =============================================================================
# PAGE STYLING
# =============================================================================

def apply_thy_branding():
    st.markdown("""
    <style>
        /* Professional silver background */
        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
        }

        /* Hide Streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .page-title {
            text-align: center;
            margin: 0.25rem 0 0.75rem 0;
            font-size: 1.6rem;
            font-weight: 500;
            color: #111827;
            letter-spacing: -0.02em;
        }

        .status-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 1.25rem 1.25rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 10px 28px rgba(17, 24, 39, 0.06);
        }

        .status-box {
            border-radius: 14px;
            padding: 1.1rem 1.05rem;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            min-height: 110px;
            box-shadow: 0 8px 18px rgba(17, 24, 39, 0.05);
        }
        .status-box-title {
            font-size: 0.95rem;
            font-weight: 500;
            color: #111827;
            margin-bottom: 0.35rem;
        }
        .status-box-desc {
            font-size: 0.75rem;
            color: #6b7280;
            line-height: 1.2;
        }

        .status-box.pending {
            background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
            border-color: #e5e7eb;
        }

        /* Green when step reached */
        .status-box.reached {
            background: linear-gradient(180deg, #ecfdf5 0%, #f0fdf4 100%);
            border-color: rgba(22, 163, 74, 0.35);
        }
        .status-box.reached .status-box-title,
        .status-box.reached .status-box-desc {
            color: #065f46;
        }

        .meta-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            padding: 1.05rem 1.0rem;
            gap: 0.5rem 1rem;
            margin-top: 0.75rem;
            min-height: 110px;
        }
        .meta-item {
            font-size: 0.9rem;
            color: #111827;
        }
        .meta-item span {
            color: #6b7280;
            font-weight: 500;
            margin-right: 0.35rem;
        }

        .current-line {
            text-align: center;
            margin: 0.75rem 0 0.25rem 0;
            color: #4b5563;
            font-size: 0.92rem;
            font-weight: 500;
        }

        .priority-alert {
            margin-top: 0.75rem;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(185, 28, 28, 0.25);
            background: linear-gradient(180deg, #fef2f2 0%, #fff1f2 100%);
            box-shadow: 0 10px 26px rgba(185, 28, 28, 0.08);
        }
        .priority-alert-title {
            font-size: 0.95rem;
            font-weight: 500;
            color: #7f1d1d;
            margin: 0;
        }
        .priority-alert-desc {
            margin-top: 0.25rem;
            font-size: 0.85rem;
            color: #991b1b;
        }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    st.set_page_config(
        page_title="FlightSense - Review Status",
        page_icon="✈️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    poll_seconds = int(os.getenv("REVIEW_STATUS_POLL_SECONDS", "2"))
    st_autorefresh(interval=poll_seconds * 1000, key="status_autorefresh")

    apply_thy_branding()

    logo_path = os.path.join(os.path.dirname(__file__), "images", "tklogo.png")
    if os.path.exists(logo_path):
        c1, c2, c3 = st.columns([1, 1.2, 1])
        with c2:
            st.image(logo_path, use_container_width=True)
    else:
        st.warning("Logo file not found in container: images/tklogo.png")

    st.markdown('<div class="page-title">FlightSense Review Status</div>', unsafe_allow_html=True)

    tracking_enabled = get_tracking_flag()  

    if tracking_enabled:
        status_row = get_latest_review_status()
        if not status_row:
            st.warning("No status found yet.")
            return

        status_code = int(status_row.get("status", 0))
        status_meta = STATUS_MAP.get(status_code, STATUS_MAP[0])
        is_high_priority = bool(status_row.get("is_high_priority"))

        # Main focus: status boxes
        render_status_boxes(status_code)

        st.markdown(
            '<div class="current-line">Current: {label} — {desc}</div>'.format(
                label=status_meta["label"],
                desc=status_meta["description"],
            ),
            unsafe_allow_html=True,
        )

        if is_high_priority:
            st.markdown(
                """
                <div class="priority-alert">
                  <p class="priority-alert-title">High Priority — Immediate action taken</p>
                  <div class="priority-alert-desc">
                    This review was flagged as high priority and has been routed for immediate attention.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="meta-row">
              <div class="meta-item"><span>Review ID</span>{review_id}</div>
              <div class="meta-item"><span>Date</span>{date}</div>
              <div class="meta-item"><span>PNR</span>{pnr}</div>
              <div class="meta-item"><span>Flight</span>{flight}</div>
            </div>
            """.format(
                review_id=status_row.get("review_id") or "–",
                date=status_row.get("date") or "–",
                pnr=status_row.get("pnr") or "–",
                flight=status_row.get("flight_number") or "–",
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")

        if status_code >= TERMINAL_STATUS:
            st.success("Processing completed. Tracking stopped.")
            # set_tracking_flag(False)
    else:
        st.info("Waiting for tracking flag to turn on...")

if __name__ == "__main__":
    main()
