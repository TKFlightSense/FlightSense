from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"

    # Subject-specific dashboards
    FLIGHT_DELAY = "flight_delay"
    CHECKIN_BOARDING_PROCESS = "checkin_boarding_process"
    BAGGAGE = "baggage"
    INFLIGHT_EXPERIENCE = "inflight_experience"
    PRICING_FEES = "pricing_fees"
    ONLINE_BOOKING = "online_booking"


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
    """
    Full department names
    """
    IUIUB = "İkram ve Uçak İçi Ürünler Bşk."
    BMCOGM = "Yer İşletme Bşk - Bagaj"
    KABIN = "Kabin Hizmetleri Bşk."
    TGS = "TGS - Yer Hizmetleri"