from __future__ import annotations
from typing import List
from models.enums.enums import UserRole, SentimentLabel


class AccessControlService:
    """
    Handles role-based access: which pages and which sentiment categories
    each role can see.
    """

    def __init__(self) -> None:
        # TODO: update mapping to your new labels if needed
        self.role_to_category = {
            # Example:
            # UserRole.FLIGHT_DELAY: [SentimentLabel.FLIGHT_DELAY_CANCELLATION],
            # UserRole.BAGGAGE: [SentimentLabel.BAGGAGE_ISSUES],
        }

    # ---------- pages ----------

    def get_allowed_pages(self, role: str) -> List[str]:
        """Get list of pages user can access based on their role."""
        try:
            user_role = UserRole(role)

            if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
                return [
                    "dashboard",  # Aggregated view
                    "flight_delay",
                    "checkin_boarding",
                    "baggage",
                    "inflight_experience",
                    "pricing_fees",
                    "online_booking",
                ]
            else:
                page_mapping = {
                    UserRole.FLIGHT_DELAY: ["flight_delay"],
                    UserRole.CHECKIN_BOARDING_PROCESS: ["checkin_boarding"],
                    UserRole.BAGGAGE: ["baggage"],
                    UserRole.INFLIGHT_EXPERIENCE: ["inflight_experience"],
                    UserRole.PRICING_FEES: ["pricing_fees"],
                    UserRole.ONLINE_BOOKING: ["online_booking"],
                }
                return page_mapping.get(user_role, [])
        except ValueError:
            return []

    def can_access_page(self, user_role: str, page: str) -> bool:
        return page in self.get_allowed_pages(user_role)

    # ---------- categories ----------

    def can_access_category(self, user_role: str, category: SentimentLabel) -> bool:
        try:
            role_enum = UserRole(user_role)
            allowed_categories = self.role_to_category.get(role_enum, [])
            return category in allowed_categories
        except ValueError:
            return False

    def get_allowed_categories(self, user_role: str) -> List[SentimentLabel]:
        try:
            role_enum = UserRole(user_role)
            return self.role_to_category.get(role_enum, [])
        except ValueError:
            return []

    def is_full_access_role(self, user_role: str) -> bool:
        try:
            role_enum = UserRole(user_role)
            return role_enum in [UserRole.ADMIN, UserRole.MANAGER]
        except ValueError:
            return False
