"""
Canonical fine-grained labels used by LLM segmentation and routing.
"""

ALL_LABELS = [
    "inflight_experience_food_beverage",
    "inflight_experience_seats_comfort",
    "inflight_experience_entertainment",
    "inflight_experience_cabin_service",
    "inflight_experience_cleanliness",
    "checkin_process",
    "boarding_process",
    "baggage_lost",
    "baggage_damaged",
    "booking_and_ticketing",
    "customer_support",
    "pricing_and_loyalty",
]

# ---------------------------
# which labels participate in which segmentations
# ---------------------------

SENTIMENT_LABELS = [
    "inflight_experience_food_beverage",
    "inflight_experience_seats_comfort",
    "inflight_experience_entertainment",
    "inflight_experience_cabin_service",
    "inflight_experience_cleanliness",
    "checkin_process",
    "boarding_process",
    "booking_and_ticketing",
    "customer_support",
    "pricing_and_loyalty",
]

PRIORITY_LABELS = [
    "inflight_experience_food_beverage",
    "inflight_experience_seats_comfort",
    "inflight_experience_entertainment",
    "inflight_experience_cabin_service",
    "inflight_experience_cleanliness",
    "checkin_process",
    "boarding_process",
    "baggage_lost",
    "baggage_damaged",
    "booking_and_ticketing",
]
