from __future__ import annotations
from typing import List, Dict

from models.roles import VALID_ROLES


class AccessControlService:
    """
    Handles role-based access:
      - which pages a role can access
      - which labels a role can see

    Roles and labels are plain strings.
    Labels correspond to your label_map labels and/or processed_data columns.
    """

    def __init__(self) -> None:
        # Role → pages user can access in the dashboard
        self.role_to_pages: Dict[str, List[str]] = {
            "admin": [
                "dashboard",
                "flight_delay",
                "checkin_boarding",
                "baggage",
                "inflight_experience",
                "pricing_fees",
                "online_booking",
            ],
            "manager": [
                "dashboard",
                "flight_delay",
                "checkin_boarding",
                "baggage",
                "inflight_experience",
                "pricing_fees",
                "online_booking",
            ],
            "viewer": ["dashboard"],

            # subject-specific roles
            "flight_delay": ["flight_delay"],
            "checkin_boarding": ["checkin_boarding"],
            "baggage": ["baggage"],
            "inflight_experience": ["inflight_experience"],
            "pricing_fees": ["pricing_fees"],
            "online_booking": ["online_booking"],
            "customer_support": ["dashboard"],  # you can expand later
        }

        # Role → allowed labels (fine-grained)
        # You can adjust these to exactly match your label_map.json.
        self.role_to_labels: Dict[str, List[str]] = {
            "baggage": [
                "baggage_lost",
                "baggage_damaged",
            ],
            "inflight_experience": [
                "inflight_experience_food_beverage",
                "inflight_experience_seats_comfort",
                "inflight_experience_entertainment",
                "inflight_experience_cabin_service",
                "inflight_experience_cleanliness",
            ],
            "pricing_fees": [
                "pricing_and_loyalty",
            ],
            "online_booking": [
                "booking_and_ticketing",
            ],
            "customer_support": [
                "customer_support",
            ],
            # admins & managers: full access handled separately
        }

    # ---------- roles ----------

    def is_valid_role(self, role: str) -> bool:
        return role in VALID_ROLES

    def is_full_access_role(self, role: str) -> bool:
        return role in ("admin", "manager")

    # ---------- pages ----------

    def get_allowed_pages(self, role: str) -> List[str]:
        return self.role_to_pages.get(role, [])

    def can_access_page(self, role: str, page: str) -> bool:
        return page in self.get_allowed_pages(role)

    # ---------- labels ----------

    def get_allowed_labels(self, role: str) -> List[str]:
        if self.is_full_access_role(role):
            # full access – don't restrict by label here
            return []
        return self.role_to_labels.get(role, [])

    def can_access_label(self, role: str, label: str) -> bool:
        if self.is_full_access_role(role):
            return True
        allowed = self.get_allowed_labels(role)
        # if no explicit labels configured for the role, treat as no restriction
        return not allowed or (label in allowed)
