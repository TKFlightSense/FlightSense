LABELS = [
    "flight_delay_cancellation_negative",
    "flight_delay_cancellation_positive",
    "checkin_boarding_process_negative",
    "checkin_boarding_process_positive",
    "baggage_issues_negative",
    "baggage_issues_positive",
    "inflight_experience_negative",
    "inflight_experience_positive",
    "pricing_fees_negative",
    "pricing_fees_positive",
    "online_booking_negative",
    "online_booking_positive",
]

DEPT_PAIRS = {
    "flight_delay_cancellation": (
        "flight_delay_cancellation_negative",
        "flight_delay_cancellation_positive",
    ),
    "checkin_boarding_process": (
        "checkin_boarding_process_negative",
        "checkin_boarding_process_positive",
    ),
    "baggage_issues": ("baggage_issues_negative", "baggage_issues_positive"),
    "inflight_experience": (
        "inflight_experience_negative",
        "inflight_experience_positive",
    ),
    "pricing_fees": ("pricing_fees_negative", "pricing_fees_positive"),
    "online_booking": ("online_booking_negative", "online_booking_positive"),
}
