from enum import Enum


class SentimentLabel(Enum):
    """
    Enum class for multi-label sentiment analysis in FlightSense project.
    Each label represents a specific aspect of airline customer experience.
    """
    FLIGHT_DELAY_CANCELLATION = "flight_delay_cancellation"
    CHECKIN_BOARDING_PROCESS = "checkin_boarding_process"
    BAGGAGE_ISSUES = "baggage_issues"
    INFLIGHT_EXPERIENCE = "inflight_experience"
    PRICING_FEES = "pricing_fees"
    ONLINE_BOOKING = "online_booking"


class StatusSuffix(Enum):
    POSITIVE = 1
    NEGATIVE = -1


class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    FLIGHT_DELAY = "flight_delay"
    CHECKIN_BOARDING_PROCESS = "checkin_boarding_process"
    BAGGAGE = "baggage"
    INFLIGHT_EXPERIENCE = "inflight_experience"
    PRICING_FEES = "pricing_fees"
    ONLINE_BOOKING = "online_booking"
