from __future__ import annotations
from typing import List, Dict

from models.roles import VALID_ROLES
from models.labels import ALL_LABELS


class AccessControlService:
    """
    Handles role-based access:
      - which pages a role can access
      - which fine-grained labels a role can see

    Roles and labels are plain strings.
    Labels correspond to the fine-grained labels from models.labels.ALL_LABELS.
    """

    def __init__(self) -> None:
        # Role - pages user can access in the dashboard
        self.role_to_pages: Dict[str, List[str]] = {
            "admin": [
                "dashboard",
                "flight_delay",
                "checkin_boarding",
                "baggage",
                "inflight_experience",
                "pricing_fees",
                "online_booking",
                "customer_support",
            ],
            "manager": [
                "dashboard",
                "flight_delay",
                "checkin_boarding",
                "baggage",
                "inflight_experience",
                "pricing_fees",
                "online_booking",
                "customer_support",
            ],
            "viewer": ["dashboard"],

            # subject-specific roles
            "flight_delay": ["flight_delay"],              # coarse only for now
            "checkin_boarding": ["checkin_boarding"],
            "baggage": ["baggage"],
            "inflight_experience": ["inflight_experience"],
            "pricing_fees": ["pricing_fees"],
            "online_booking": ["online_booking"],
            "customer_support": ["customer_support"],
        }

        # Role -> allowed fine-grained labels
        # (all labels are from models.labels.ALL_LABELS)
        self.role_to_labels: Dict[str, List[str]] = {
            # baggage team sees baggage labels
            "baggage": [
                "baggage_lost",
                "baggage_damaged",
            ],

            # inflight team sees only inflight experience sublabels
            "inflight_experience": [
                "inflight_experience_food_beverage",
                "inflight_experience_seats_comfort",
                "inflight_experience_entertainment",
                "inflight_experience_cabin_service",
                "inflight_experience_cleanliness",
            ],

            # pricing / loyalty
            "pricing_fees": [
                "pricing_and_loyalty",
            ],

            # online booking
            "online_booking": [
                "booking_and_ticketing",
            ],

            # generic customer support
            "customer_support": [
                "customer_support",
            ],

            # Ground ops style roles – if you later split, you can route these too
            "checkin_boarding": [
                "checkin_process",
                "boarding_process",
            ],
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
        """
        Returns list of fine-grained labels a role can see.
        Full access roles (admin/manager) get [] here, meaning "no restriction".
        """
        if self.is_full_access_role(role):
            # full access – treat as unrestricted
            return []
        return self.role_to_labels.get(role, [])

    def can_access_label(self, role: str, label: str) -> bool:
        """
        Returns True if the given role is allowed to interact with this label.
        """
        if self.is_full_access_role(role):
            return True

        allowed = self.get_allowed_labels(role)

        # if no explicit mapping for the role, we can either:
        #   - treat as no restriction, or
        #   - treat as "cannot access anything".
        # Here we treat "no mapping" as "no restriction" to keep it flexible.
        if not allowed:
            return True

        return label in allowed
    