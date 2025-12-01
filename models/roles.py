"""
Central definition of valid user roles for FlightSense.
Roles are simple strings, used across auth and access control.
Configuration is loaded from models/artifacts/access_control_config.json.
"""
from pathlib import Path
import json


def _load_access_control_config():
    """Load access control configuration from JSON file."""
    config_path = Path("models/artifacts/access_control_config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Access control config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load valid roles from configuration file
_ACCESS_CONFIG = _load_access_control_config()
VALID_ROLES = _ACCESS_CONFIG["valid_roles"]