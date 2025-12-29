from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class SentimentLabel(str, Enum):
    """
    These should match the *column names* in your processed_data table.
    """
    FLIGHT_DELAY_CANCELLATION = "flight_delay_cancellation"
    CHECKIN_BOARDING_PROCESS = "checkin_boarding_process"
    BAGGAGE_ISSUES = "baggage_issues"
    INFLIGHT_EXPERIENCE = "inflight_experience"
    PRICING_FEES = "pricing_fees"
    ONLINE_BOOKING = "online_booking"


class StatusSuffix(str, Enum):
    """
    High-level status used in filters / API: 'POSITIVE' / 'NEGATIVE'.
    """
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class StatusNumericalVal(int, Enum):
    """
    Actual values stored in DB: -1 / 0 / 1.
    """
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

class Departments(str, Enum):
    IUIUB = "IUIUB"
    BMCOGM = "BMCOGM"
    KHB = "KHB"
    TGS = "TGS"
    RVBCM = "RVBCM"
    CMYM = "CMYM"
    GYB = "GYB"


class LabelToDepartment(str, Enum):
    """
    Label to department mapping
    """
    inflight_experience_food_beverage = "IUIUB"
    inflight_experience_entertainment = "IUIUB"
    inflight_experience_seats_comfort = "KHB"
    inflight_experience_cabin_service = "KHB"
    inflight_experience_cleanliness = "KHB"
    checkin_process = "TGS"
    boarding_process = "TGS"
    baggage_lost = "BMCOGM"
    baggage_damaged = "BMCOGM"
    booking_and_ticketing = "RVBCM"
    customer_support = "CMYM"
    pricing_and_loyalty = "GYB"


class DepartmentToLabels(Enum):
    IUIUB = [
        "inflight_experience_food_beverage",
        "inflight_experience_entertainment",
    ]
    KHB = [
        "inflight_experience_seats_comfort",
        "inflight_experience_cabin_service",
        "inflight_experience_cleanliness",
    ]
    TGS = [
        "checkin_process",
        "boarding_process",
    ]
    BMCOGM = [
        "baggage_lost",
        "baggage_damaged",
    ]
    RVBCM = [
        "booking_and_ticketing",
    ]
    CMYM = [
        "customer_support",
    ]
    GYB = [
        "pricing_and_loyalty",
    ]

class DepartmentTables(str, Enum):
    KHB = "kabin_hizmetleri"
    IUIUB = "ikram_ucak_ici"
    BMCOGM = "yer_isletme_bagaj"
    TGS = "tgs"
    RVBCM = "rez_biletleme"
    CMYM = "cagri_merkezi"
    GYB = "gelir_yonetimi"
