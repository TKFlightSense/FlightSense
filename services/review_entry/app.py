import streamlit as st
import mysql.connector
import os
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TKFlightSense | Review Entry",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS - Turkish Airlines Branding
# ─────────────────────────────────────────────────────────────────────────────
THY_RED = "#b7312c"
THY_RED_DARK = "#8f2521"
THY_GRAY = "#111827"
THY_LIGHT_GRAY = "#f3f4f6"

st.markdown(f"""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(180deg, #f8fafc 0%, {THY_LIGHT_GRAY} 100%);
    }}

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Header container */
    .header-container {{
        text-align: center;
        padding: 1.5rem 0 1.25rem 0;
        margin-bottom: 0.75rem;
    }}

    .brand-kicker {{
        font-size: 0.75rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #6b7280;
        margin: 0;
    }}
    
    /* Logo placeholder */
    .logo-placeholder {{
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, {THY_RED} 0%, {THY_RED_DARK} 100%);
        border-radius: 50%;
        margin: 0 auto 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(232, 25, 50, 0.3);
    }}
    
    .logo-placeholder span {{
        font-size: 2rem;
    }}
    
    /* Main title */
    .main-title {{
        font-size: 1.65rem;
        font-weight: 800;
        color: {THY_GRAY};
        margin: 0.25rem 0 0.15rem 0;
        letter-spacing: -0.5px;
    }}

    .main-title .accent {{
        color: {THY_RED};
    }}
    
    .subtitle {{
        font-size: 0.92rem;
        color: #4b5563;
        margin-top: 0.25rem;
        font-weight: 400;
    }}
    
    /* Card container */
    .form-card {{
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 14px 34px rgba(17, 24, 39, 0.06);
        border: 1px solid #e5e7eb;
    }}
    
    /* Section headers */
    .section-header {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {THY_RED};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {THY_RED};
        display: inline-block;
    }}
    
    /* Form labels */
    .stTextArea label, .stTextInput label, .stDateInput label {{
        font-weight: 500 !important;
        color: {THY_GRAY} !important;
        font-size: 0.875rem !important;
    }}
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 10px !important;
        border: 1.5px solid #d1d5db !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {THY_RED} !important;
        box-shadow: 0 0 0 3px rgba(232, 25, 50, 0.1) !important;
    }}
    
    /* Submit button */
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {THY_RED} 0%, {THY_RED_DARK} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(232, 25, 50, 0.3) !important;
    }}
    
    .stFormSubmitButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(232, 25, 50, 0.4) !important;
    }}
    
    /* Success message */
    .stSuccess {{
        background-color: #E8F5E9 !important;
        border-left: 4px solid #4CAF50 !important;
        border-radius: 8px !important;
    }}
    
    /* Error message */
    .stError {{
        background-color: #FFEBEE !important;
        border-left: 4px solid {THY_RED} !important;
        border-radius: 8px !important;
    }}
    
    /* Info box */
    .info-box {{
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-top: 1.5rem;
        border-left: 4px solid {THY_RED};
    }}
    
    .info-box p {{
        margin: 0;
        font-size: 0.85rem;
        color: #555;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #999;
        font-size: 0.75rem;
    }}
    
    /* Columns spacing */
    .row-widget.stHorizontalBlock {{
        gap: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "flightsense"),
        password=os.getenv("MYSQL_PASSWORD", "flightsense123"),
        database=os.getenv("MYSQL_DATABASE", "flightsense")
    )

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "images", "tklogo.png")

st.markdown(
    """
    <div class="header-container">
      <p class="brand-kicker">Turkish Airlines</p>
      <h1 class="main-title"><span class="accent">Customer</span> Feedback Portal</h1>
      <p class="subtitle">Quality Assurance · Review Intake</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.image(logo_path, use_container_width=True)
except Exception:
    # If the image isn't available in some environments, continue gracefully.
    pass

# ─────────────────────────────────────────────────────────────────────────────
# FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Submit New Review</p>', unsafe_allow_html=True)

with st.form("review_form", clear_on_submit=True):
    # Review text
    review_text = st.text_area(
        "Customer Feedback",
        height=150,
        placeholder="Enter the customer's feedback here..."
    )
    
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    
    # Flight details in columns - Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        flight_number = st.text_input(
            "Flight Number",
            value="TK000",
            placeholder="e.g., TK1234"
        )
    
    with col2:
        pnr = st.text_input(
            "PNR Code",
            value="TSTPNR",
            placeholder="e.g., ABC123"
        )
    
    # Route is defaulted automatically for demo consistency.
    
    # Date
    review_date = st.date_input(
        "Feedback Date",
        value=date.today()
    )
    
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    
    # Submit button
    submitted = st.form_submit_button("Submit Review", use_container_width=True)

    if submitted:
        if not review_text.strip():
            st.error("⚠️ Please enter the customer feedback before submitting.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Build route strings (default both endpoints to TST)
                origin = "TST"
                destination = "TST"
                
                route = None
                bidirectional_route = None
                if origin and destination:
                    route = f"{origin}{destination}"
                    # Bidirectional route: sorted alphabetically
                    bidirectional_route = "".join(sorted([origin, destination])) + "".join(sorted([origin, destination], reverse=True))
                
                query = """
                INSERT INTO reviews (review, date, flight_number, pnr, origin_iata, destination_iata, route, bidirectional_route)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    review_text.strip(),
                    review_date,
                    flight_number.strip() if flight_number else None,
                    pnr.strip() if pnr else None,
                    origin,
                    destination,
                    route,
                    bidirectional_route
                )
                
                cursor.execute(query, values)
                conn.commit()
                review_id = cursor.lastrowid  # <-- define it here

                st.success("✅ Review submitted successfully! It will be processed automatically.")
                # Enable tracking in review_status
                cursor.execute(
                    """
                    INSERT INTO review_status (id, review_id, status, tracking_enabled)
                    VALUES (1, %s, 0, 1)
                    ON DUPLICATE KEY UPDATE
                        review_id = VALUES(review_id),
                        status = VALUES(status),
                        tracking_enabled = VALUES(tracking_enabled)
                    """,
                    (review_id,),
                )

                conn.commit()

                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"❌ Error submitting review: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
      <p>TKFlightSense • Turkish Airlines</p>
    </div>
    """,
    unsafe_allow_html=True,
)
