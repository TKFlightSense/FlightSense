"""
Central definition of valid user roles for FlightSense.
Roles are simple strings, used across auth and access control.
"""

VALID_ROLES = [
    "admin",
    "manager",
    "viewer",               # default, very limited

    # subject-specific roles
    "flight_delay",
    "checkin_boarding",
    "baggage",
    "inflight_experience",
    "pricing_fees",
    "online_booking",
    "customer_support",
]