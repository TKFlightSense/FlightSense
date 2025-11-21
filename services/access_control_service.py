from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json

from models.labels import ALL_LABELS


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
        self.role_to_pages: Dict[str, List[str]] = _ACCESS_CONFIG["role_to_pages"]
        self.role_to_labels: Dict[str, List[str]] = _ACCESS_CONFIG["role_to_labels"]
        self.valid_roles: List[str] = VALID_ROLES
        self.full_access_roles: List[str] = FULL_ACCESS_ROLES

    # ---------- roles ----------

    def is_valid_role(self, role: str) -> bool:
        return role in self.valid_roles

    def is_full_access_role(self, role: str) -> bool:
        return role in self.full_access_roles

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
    