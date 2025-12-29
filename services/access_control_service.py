from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json

from models.enums.enums import Departments


def _load_access_control_config() -> Dict[str, Any]:
    """Load access control configuration from JSON file."""
    config_path = Path("models/artifacts/access_control_config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Access control config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load configuration from JSON file
_ACCESS_CONFIG = _load_access_control_config()
VALID_ROLES = _ACCESS_CONFIG["valid_roles"]
FULL_ACCESS_ROLES = _ACCESS_CONFIG["full_access_roles"]


class AccessControlService:
    """
    Handles role-based access:
      - which pages a role can access
      - which fine-grained labels a role can see

    Roles and labels are plain strings.
    Labels correspond to the fine-grained labels from models.labels.ALL_LABELS.
    All configurations are loaded from models/artifacts/access_control_config.json.
    """

    def __init__(self) -> None:
        # Load configurations from the global config
        self.valid_roles: List[str] = VALID_ROLES
        self.full_access_roles: List[str] = FULL_ACCESS_ROLES
        self.role_to_departments: Dict[str, List[str]] = _ACCESS_CONFIG[
            "role_to_departments"
        ]
        self.department_to_labels: Dict[str, List[str]] = _ACCESS_CONFIG[
            "department_to_labels"
        ]

    # ---------- roles ----------

    def is_valid_role(self, role: str) -> bool:
        return role in self.valid_roles

    def is_full_access_role(self, role: str) -> bool:
        return role in self.full_access_roles

    # ---------- departments ----------

    def get_allowed_departments(self, role: str, user_department: Optional[str]) -> List[str]:
        if self.is_full_access_role(role):
            return list(self.role_to_departments.get(role, []))
        if user_department:
            return [user_department]
        return []

    def can_access_department(self, role: str, user_department: Optional[str]) -> bool:
        if self.is_full_access_role(role):
            return True
        return user_department == department
    # ---------- labels ----------

    def get_allowed_labels(self, role: str, user_department: Optional[str]) -> List[str]:
        """
        Returns list of fine-grained labels a role can see.
        Full access roles (admin/manager) get [] here, meaning "no restriction".
        """
        if self.is_full_access_role(role):
            # full access – treat as unrestricted
            return []
        if not user_department:
            return []
        return self.department_to_labels.get(user_department, [])

    def can_access_label(self, role: str, user_department: Optional[str], label: str) -> bool:
        """
        Returns True if the given role is allowed to interact with this label.
        """
        if self.is_full_access_role(role):
            return True

        if not user_department:
            return False

        return label in self.department_to_labels.get(user_department, [])
    