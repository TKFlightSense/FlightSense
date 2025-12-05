import streamlit as st
import mysql.connector
import os
from datetime import date

# Database connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "flightsense"),
        password=os.getenv("MYSQL_PASSWORD", "flightsense123"),
        database=os.getenv("MYSQL_DATABASE", "flightsense")
    )

st.title("FlightSense Review Entry")

with st.form("review_form"):
    review_text = st.text_area("Review Text", height=150)
    review_date = st.date_input("Date", value=date.today())
    flight_number = st.text_input("Flight Number (e.g., TK1234)")
    pnr = st.text_input("PNR (e.g., ABC1234)")
    
    submitted = st.form_submit_button("Submit Review")

    if submitted:
        if not review_text:
            st.error("Review text is required.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                query = """
                INSERT INTO reviews (review, date, flight_number, pnr)
                VALUES (%s, %s, %s, %s)
                """
                values = (review_text, review_date, flight_number, pnr)
                
                cursor.execute(query, values)
                conn.commit()
                
                st.success("Review submitted successfully!")
                
                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"Error submitting review: {e}")
