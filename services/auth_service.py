from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import logging

import bcrypt
import jwt

from services.db_service.db_service import DbService
from services.access_control_service import AccessControlService
from models.roles import VALID_ROLES

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication: register, login, token generation/verification.

    Roles are simple strings validated against VALID_ROLES.
    """

    def __init__(
        self,
        db_service: DbService,
        secret_key: str,
        access_control: AccessControlService,
        token_expiry_hours: int = 24,
    ):
        self.db = db_service
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self.access_control = access_control

    # ---------- public API ----------

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str,
        department: Optional[str] = None,
    ) -> Dict:
        """Register a new user with hashed password."""
        try:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters")

            if role not in VALID_ROLES:
                raise ValueError(f"Invalid role. Must be one of: {VALID_ROLES}")

            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            user_id = self.db.create_user(
                username, email, password_hash, role, department
            )

            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "message": "User registered successfully",
            }
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": "Registration failed"}

    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and return JWT token + metadata."""
        try:
            user = self.db.get_user_by_username(username)

            if not user:
                return {"success": False, "error": "Invalid credentials"}

            if not bcrypt.checkpw(
                password.encode("utf-8"), user["password_hash"].encode("utf-8")
            ):
                return {"success": False, "error": "Invalid credentials"}

            self.db.update_last_login(username)
            token = self._generate_token(user)
            allowed_pages = self.access_control.get_allowed_pages(user["role"])

            return {
                "success": True,
                "token": token,
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "department": user["department"],
                    "allowed_pages": allowed_pages,
                },
            }
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "error": "Login failed"}

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info (payload) or None."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    # ---------- internal ----------

    def _generate_token(self, user: Dict) -> str:
        payload = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=self.token_expiry_hours),
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
