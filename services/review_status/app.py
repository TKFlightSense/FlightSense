"""
FlightSense Review Status Tracker
=================================
A Streamlit dashboard for tracking review processing status in real-time.

This page allows users to:
- Enter their PNR code to track their review
- See the current processing stage of their feedback
- View classification results (label, sentiment, priority)
- Check if a Jira ticket was created for high-priority reviews

Database Tables Used:
- reviews: Original submitted reviews (id, review, flight_number, pnr, created_at, processed)
- processed_reviews: Classification results (review_id, label, sentiment, priority, summary, created_at)
- jira_tickets: Ticket tracking (review_id, ticket_key, ticket_url, created_at)

Processing Stages:
1. SUBMITTED - Review received, waiting for processing
2. PROCESSING - Currently being classified by LLM
3. CLASSIFIED - Classification complete (label, sentiment, priority assigned)
4. TICKET_CREATED - High priority: Jira ticket created
5. COMPLETED - Processing finished
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    """
    Create MySQL database connection using environment variables.
    Same configuration as review_entry service.
    """
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

def get_review_by_pnr(pnr: str) -> Optional[Dict[str, Any]]:
    """
    Fetch review from 'reviews' table by PNR code.
    Returns: dict with id, review, flight_number, pnr, created_at, processed
    """
    # TODO: Implement query
    # SELECT id, review, flight_number, pnr, created_at, processed 
    # FROM reviews WHERE pnr = %s ORDER BY created_at DESC LIMIT 1
    pass


def get_processed_segments(review_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all processed segments for a review from 'processed_reviews' table.
    Returns: list of dicts with label, sentiment, priority, summary, created_at
    """
    # TODO: Implement query
    # SELECT label, sentiment, priority, summary, created_at
    # FROM processed_reviews WHERE review_id = %s
    pass


def get_jira_ticket(review_id: int) -> Optional[Dict[str, Any]]:
    """
    Check if a Jira ticket was created for this review.
    Returns: dict with ticket_key, ticket_url, created_at or None
    """
    # TODO: Implement query
    # SELECT ticket_key, ticket_url, created_at
    # FROM jira_tickets WHERE review_id = %s
    pass


def get_all_reviews_by_pnr(pnr: str) -> List[Dict[str, Any]]:
    """
    Fetch all reviews for a PNR (in case of multiple submissions).
    Returns: list of review dicts ordered by created_at DESC
    """
    # TODO: Implement query
    pass


# =============================================================================
# STATUS DETERMINATION LOGIC
# =============================================================================

def determine_status(review: Dict, segments: List, ticket: Optional[Dict]) -> str:
    """
    Determine the current processing status of a review.
    
    Returns one of:
    - "SUBMITTED" - In reviews table, processed=0
    - "PROCESSING" - processed=1 but no segments yet
    - "CLASSIFIED" - Has segments in processed_reviews
    - "TICKET_CREATED" - Has entry in jira_tickets
    - "COMPLETED" - Fully processed
    """
    # TODO: Implement status logic
    pass


def get_status_display_info(status: str) -> Dict[str, str]:
    """
    Get display properties for each status.
    Returns: dict with icon, color, description
    """
    status_map = {
        "SUBMITTED": {
            "icon": "📥",
            "color": "#6b7280",  # gray
            "description": "Your feedback has been received and is queued for processing."
        },
        "PROCESSING": {
            "icon": "⚙️",
            "color": "#f59e0b",  # amber
            "description": "Your feedback is currently being analyzed by our AI system."
        },
        "CLASSIFIED": {
            "icon": "✅",
            "color": "#10b981",  # green
            "description": "Analysis complete. Your feedback has been categorized."
        },
        "TICKET_CREATED": {
            "icon": "🎫",
            "color": "#3b82f6",  # blue
            "description": "A support ticket has been created for your feedback."
        },
        "COMPLETED": {
            "icon": "🏁",
            "color": "#22c55e",  # green
            "description": "Processing complete. Thank you for your feedback!"
        }
    }
    return status_map.get(status, status_map["SUBMITTED"])


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_status_timeline(current_status: str):
    """
    Render a visual timeline showing processing stages.
    Highlights the current stage.
    """
    # TODO: Implement timeline visualization
    # Stages: SUBMITTED -> PROCESSING -> CLASSIFIED -> (TICKET_CREATED) -> COMPLETED
    pass


def render_classification_results(segments: List[Dict]):
    """
    Display classification results in expandable cards.
    Shows: label, sentiment (with color), priority (with badge), summary
    """
    # TODO: Implement segment display
    pass


def render_ticket_info(ticket: Dict):
    """
    Display Jira ticket information with link.
    """
    # TODO: Implement ticket display with clickable link
    pass


# =============================================================================
# PAGE STYLING
# =============================================================================

def apply_thy_branding():
    """
    Apply Turkish Airlines branding CSS.
    Same style as review_entry for consistency.
    """
    st.markdown("""
    <style>
        /* THY Red: #b7312c */
        /* TODO: Add custom CSS matching review_entry branding */
        
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        /* Status card styling */
        .status-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Timeline styling */
        .timeline-step {
            display: flex;
            align-items: center;
            padding: 0.75rem 0;
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
    """
    Main Streamlit application entry point.
    """
    st.set_page_config(
        page_title="FlightSense - Review Status",
        page_icon="✈️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    apply_thy_branding()
    
    # Header
    st.title("📋 Review Status Tracker")
    st.markdown("Track the status of your submitted feedback.")
    
    # PNR Input
    st.markdown("---")
    pnr_input = st.text_input(
        "Enter your PNR Code",
        placeholder="e.g., ABC123",
        max_chars=10
    )
    
    search_button = st.button("🔍 Track Status", type="primary", use_container_width=True)
    
    if search_button and pnr_input:
        # TODO: Implement search logic
        # 1. Call get_review_by_pnr(pnr_input)
        # 2. If found, get segments and ticket info
        # 3. Determine status
        # 4. Render results
        
        with st.spinner("Searching..."):
            # Placeholder for implementation
            st.info("🔧 Status tracking functionality to be implemented.")
            
            # Example structure:
            # review = get_review_by_pnr(pnr_input)
            # if review:
            #     segments = get_processed_segments(review['id'])
            #     ticket = get_jira_ticket(review['id'])
            #     status = determine_status(review, segments, ticket)
            #     
            #     render_status_timeline(status)
            #     
            #     if segments:
            #         render_classification_results(segments)
            #     
            #     if ticket:
            #         render_ticket_info(ticket)
            # else:
            #     st.warning("No review found with this PNR code.")
    
    # Footer with logo
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # TODO: Add Turkish Airlines logo (copy from review_entry/images/)
        st.markdown(
            "<p style='text-align: center; color: #888; font-size: 0.8rem;'>"
            "Powered by FlightSense AI</p>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
