from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import logging

import bcrypt
import jwt
from mysql.connector import Error as MySQLError

from services.db_service.mysql_db_service import MySQLDbService 
from services.access_control_service import AccessControlService
from models.roles import VALID_ROLES
from models.enums.enums import Departments

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication: register, login, token generation/verification.

    Roles are simple strings validated against VALID_ROLES.
    """

    def __init__(
        self,
        db_service: MySQLDbService,
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

            if role == "viewer" and department is None:
                raise ValueError("Viewer users must have a department")

            if department is not None and department not in Departments.__members__:
                raise ValueError(f"Invalid department: {department}")

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
        except MySQLError as e:
            # Handle duplicate username/email (MySQL error code 1062)
            if e.errno == 1062:
                if "username" in str(e):
                    return {"success": False, "error": "Username already exists"}
                elif "email" in str(e):
                    return {"success": False, "error": "Email already exists"}
                return {"success": False, "error": "User already exists"}
            logger.error(f"Database error during registration: {e}")
            return {"success": False, "error": "Registration failed"}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": "Registration failed"}

    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and return JWT token + metadata."""
        try:
            user = self.db.get_user_by_username(username)

            if not user:
                return {"success": False, "error": "Invalid credentials"}

            # Check if user is active
            if not user.get("is_active", True):
                return {"success": False, "error": "Account is deactivated"}

            if not bcrypt.checkpw(
                password.encode("utf-8"), user["password_hash"].encode("utf-8")
            ):
                return {"success": False, "error": "Invalid credentials"}

            self.db.update_last_login(username)
            token = self._generate_token(user)
            allowed_departments = self.access_control.get_allowed_departments(user["role"], user.get("department"))

            return {
                "success": True,
                "token": token,
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "department": user.get("department"),
                    "allowed_departments": allowed_departments,
                },
            }
        except MySQLError as e:
            logger.error(f"Database error during login: {e}")
            return {"success": False, "error": "Login failed"}
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
            "department": user.get("department"),
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=self.token_expiry_hours),
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
