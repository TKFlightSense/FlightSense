# orchestrator.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Union
import jwt
import bcrypt
import logging
from services.db_service.db_service import DbService
from models.enums.enums import SentimentLabel, StatusSuffix, UserRole
from services.orchestrator.filter import DataFilter

logger = logging.getLogger(__name__)


class FlightSenseOrchestrator:
    """
    Orchestrator layer for FlightSense project.
    Handles business logic, authentication, and authorization.
    """

    def __init__(self, db_service: DbService, secret_key: str):
        self.db = db_service
        self.secret_key = secret_key
        self.token_expiry_hours = 24

        # Map user roles to their allowed sentiment categories
        self.role_to_category = {
            UserRole.FLIGHT_DELAY: [SentimentLabel.FLIGHT_DELAY_CANCELLATION],
            UserRole.CHECKIN_BOARDING_PROCESS: [SentimentLabel.CHECKIN_BOARDING_PROCESS],
            UserRole.BAGGAGE: [SentimentLabel.BAGGAGE_ISSUES],
            UserRole.INFLIGHT_EXPERIENCE: [SentimentLabel.INFLIGHT_EXPERIENCE],
            UserRole.PRICING_FEES: [SentimentLabel.PRICING_FEES],
            UserRole.ONLINE_BOOKING: [SentimentLabel.ONLINE_BOOKING],
            UserRole.MANAGER: list(SentimentLabel),  # All categories
            UserRole.ADMIN: list(SentimentLabel)  # All categories
        }

    # ============ AUTHENTICATION (Same as before) ============

    def register_user(self, username: str, email: str, password: str,
                      role: str, department: Optional[str] = None) -> Dict:
        """Register a new user with hashed password."""
        try:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters")

            if isinstance(role, UserRole):
                role_str = role.value
            else:
                role_str = role
                valid_roles = [r.value for r in UserRole]
                if role_str not in valid_roles:
                    raise ValueError(f"Invalid role. Must be one of: {valid_roles}")

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = self.db.create_user(username, email, password_hash, role_str, department)

            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "message": "User registered successfully"
            }
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": "Registration failed"}

    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and return JWT token."""
        try:
            user = self.db.get_user_by_username(username)

            if not user:
                return {"success": False, "error": "Invalid credentials"}

            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {"success": False, "error": "Invalid credentials"}

            self.db.update_last_login(username)
            token = self._generate_token(user)

            return {
                "success": True,
                "token": token,
                "user": {
                    "username": user['username'],
                    "email": user['email'],
                    "role": user['role'],
                    "department": user['department'],
                    "allowed_pages": self._get_allowed_pages(user['role'])
                }
            }
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "error": "Login failed"}

    def _generate_token(self, user: Dict) -> str:
        """Generate JWT token for authenticated user."""
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.token_expiry_hours)
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    # ============ NEW AUTHORIZATION SYSTEM ============

    def _get_allowed_pages(self, role: str) -> List[str]:
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
                    "online_booking"
                ]
            else:
                # Subject-specific users only see their page
                page_mapping = {
                    UserRole.FLIGHT_DELAY: ["flight_delay"],
                    UserRole.CHECKIN_BOARDING_PROCESS: ["checkin_boarding"],
                    UserRole.BAGGAGE: ["baggage"],
                    UserRole.INFLIGHT_EXPERIENCE: ["inflight_experience"],
                    UserRole.PRICING_FEES: ["pricing_fees"],
                    UserRole.ONLINE_BOOKING: ["online_booking"]
                }
                return page_mapping.get(user_role, [])
        except ValueError:
            return []

    def can_access_page(self, user_role: str, page: str) -> bool:
        """Check if user can access a specific page."""
        allowed_pages = self._get_allowed_pages(user_role)
        return page in allowed_pages

    def can_access_category(self, user_role: str, category: SentimentLabel) -> bool:
        """Check if user can access a specific sentiment category."""
        try:
            role_enum = UserRole(user_role)
            allowed_categories = self.role_to_category.get(role_enum, [])
            return category in allowed_categories
        except ValueError:
            return False

    def get_allowed_categories(self, user_role: str) -> List[SentimentLabel]:
        """Get all categories a user can access."""
        try:
            role_enum = UserRole(user_role)
            return self.role_to_category.get(role_enum, [])
        except ValueError:
            return []

    def is_full_access_role(self, user_role: str) -> bool:
        """Check if user has full access (ADMIN or MANAGER)."""
        try:
            role_enum = UserRole(user_role)
            return role_enum in [UserRole.ADMIN, UserRole.MANAGER]
        except ValueError:
            return False

    # ============ DATA RETRIEVAL WITH ROLE-BASED FILTERING ============

    def get_processed_data_filtered(self, token: str, filters: Union[Dict, DataFilter]) -> Dict:
        """
        Get processed data with filters and role-based access control.
        Users can only see data for their assigned category.
        """
        try:
            user_info = self.verify_token(token)
            if not user_info:
                return {"success": False, "error": "Unauthorized"}

            # Convert dict to DataFilter if needed
            if isinstance(filters, dict):
                data_filter = DataFilter.from_dict(filters)
            else:
                data_filter = filters

            # Validate filters
            validation_errors = data_filter.validate()
            if validation_errors:
                return {"success": False, "error": "Validation failed", "details": validation_errors}

            # Convert strings to enums
            data_filter.to_enum()

            # Check category access
            if data_filter.label_type:
                if not self.can_access_category(user_info['role'], data_filter.label_type):
                    return {
                        "success": False,
                        "error": f"You don't have permission to access {data_filter.label_type.value} data"
                    }

            # If no category specified and user is NOT admin/manager, restrict to their category
            if not data_filter.label_type and not self.is_full_access_role(user_info['role']):
                allowed_categories = self.get_allowed_categories(user_info['role'])
                if len(allowed_categories) == 1:
                    data_filter.label_type = allowed_categories[0]


            # Query database
            df = self.db.get_processed_data(
                limit=data_filter.limit,
                label_type=data_filter.label_type,
                label_status=data_filter.label_status,
                date_from=data_filter.date_from,
                date_to=data_filter.date_to
            )

            return {
                "success": True,
                "data": df.to_dict('records'),
                "count": len(df),
                "user_role": user_info['role'],
                "filters_applied": {
                    "limit": data_filter.limit,
                    "label_type": data_filter.label_type.value if data_filter.label_type else None,
                    "label_status": data_filter.label_status.value if data_filter.label_status else None,
                    "date_from": data_filter.date_from,
                    "date_to": data_filter.date_to
                }
            }
        except Exception as e:
            logger.error(f"Error getting processed data: {e}")
            return {"success": False, "error": str(e)}

    def get_dashboard_summary(self, token: str, page: str = "dashboard") -> Dict:
        """
        Get dashboard summary based on user role and requested page.
        - ADMIN/MANAGER: Can access all pages and see all data
        - Subject-specific: Only see their category's data
        """
        try:
            user_info = self.verify_token(token)
            if not user_info:
                return {"success": False, "error": "Unauthorized"}

            # Check page access
            if not self.can_access_page(user_info['role'], page):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {page} page"
                }

            # Get allowed categories for this user
            allowed_categories = self.get_allowed_categories(user_info['role'])

            if not allowed_categories:
                return {"success": False, "error": "No data access configured for this role"}

            # Get sentiment distribution (filtered by role)
            if self.is_full_access_role(user_info['role']):
                # Full access - all sentiment data
                sentiment_dist = self.db.get_sentiment_distribution()
                total_reviews = self.db._get_row_count('processed_data')
            else:
                # Limited access - only their category
                category = allowed_categories[0]
                df = self.db.get_processed_data(label_type=category)
                total_reviews = len(df)

                # Calculate distribution for their category only
                sentiment_dist = self._calculate_category_distribution(df, category)

            # Get recent statistics
            recent_stats = self.db.get_statistics_data(limit=10)

            return {
                "success": True,
                "data": {
                    "page": page,
                    "total_reviews": total_reviews,
                    "sentiment_distribution": sentiment_dist.to_dict('records')[0] if hasattr(sentiment_dist,
                                                                                              'to_dict') else sentiment_dist,
                    "recent_statistics": recent_stats.to_dict('records'),
                    "allowed_categories": [cat.value for cat in allowed_categories],
                    "user": {
                        "username": user_info['username'],
                        "role": user_info['role'],
                        "is_full_access": self.is_full_access_role(user_info['role'])
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def _calculate_category_distribution(df, category: SentimentLabel) -> Dict:
        """Calculate sentiment distribution for a specific category."""
        col_name = category.value

        if not col_name or col_name not in df.columns:
            return {"total_reviews": 0, "positive": 0, "negative": 0, "neutral": 0}

        positive = len(df[df[col_name] == 1])
        negative = len(df[df[col_name] == -1])

        return {
            "category": category.value,
            "total_reviews": len(df),
            "positive": positive,
            "negative": negative,
        }

    def get_category_analytics(self, token: str, category: str) -> Dict:
        """
        Get detailed analytics for a specific category.
        Only accessible if user has permission for that category.
        """
        try:
            user_info = self.verify_token(token)
            if not user_info:
                return {"success": False, "error": "Unauthorized"}

            # Validate and check access
            try:
                category_enum = SentimentLabel[category.upper()]
            except KeyError:
                return {"success": False, "error": f"Invalid category: {category}"}

            if not self.can_access_category(user_info['role'], category_enum):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {category} analytics"
                }

            # Get data for this category
            df = self.db.get_processed_data(label_type=category_enum)

            # Calculate analytics
            distribution = self._calculate_category_distribution(df, category_enum)

            return {
                "success": True,
                "category": category,
                "analytics": distribution,
                "recent_reviews": df.head(20).to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error getting category analytics: {e}")
            return {"success": False, "error": str(e)}

    # ============ ADMIN-ONLY OPERATIONS ============

    def push_processed_data(self, token: str, data) -> Dict:
        """Push processed data (admin only)."""
        try:
            user_info = self.verify_token(token)
            if not user_info:
                return {"success": False, "error": "Unauthorized"}

            # Only ADMIN can push data
            if UserRole(user_info['role']) != UserRole.ADMIN:
                return {"success": False, "error": "Admin privileges required"}

            rows_inserted = self.db.push_processed_data(data)

            return {
                "success": True,
                "rows_inserted": rows_inserted,
                "message": f"Successfully inserted {rows_inserted} rows"
            }
        except Exception as e:
            logger.error(f"Error pushing data: {e}")
            return {"success": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    db = DbService()
    orchestrator = FlightSenseOrchestrator(db, secret_key="your-secret-key-here")  # TODO get secrets from env

    # Register users with different roles
    print("=== REGISTERING USERS ===")

    # Admin user
    orchestrator.register_user("admin", "admin@flightsense.com", "admin123", "admin")

    # Manager user
    orchestrator.register_user("manager", "manager@flightsense.com", "manager123", "manager")

    # Subject-specific users
    orchestrator.register_user("flight_user", "flight@flightsense.com", "flight123", "flight_delay")
    orchestrator.register_user("baggage_user", "baggage@flightsense.com", "baggage123", "baggage")

    print("\n=== TESTING PERMISSIONS ===")

    # Login as flight_delay user
    login_result = orchestrator.login("flight_user", "flight123")
    if login_result['success']:
        token = login_result['token']
        print(f"\nFlight Delay User - Allowed Pages: {login_result['user']['allowed_pages']}")

        # Try to access their own category (should work)
        data = orchestrator.get_processed_data_filtered(token, {'label_type': 'flight_delay_cancellation'})
        print(f"Access own category: {data['success']}")

        # Try to access baggage category (should fail)
        data = orchestrator.get_processed_data_filtered(token, {'label_type': 'baggage_issues'})
        print(f"Access baggage category: {data}")

    # Login as manager
    login_result = orchestrator.login("manager", "manager123")
    if login_result['success']:
        token = login_result['token']
        print(f"\nManager - Allowed Pages: {login_result['user']['allowed_pages']}")

        # Try to access all categories (should work)
        data = orchestrator.get_processed_data_filtered(token, {'label_type': 'flight_delay_cancellation'})
        print(f"Manager access flight_delay: {data['success']}")

        data = orchestrator.get_processed_data_filtered(token, {'label_type': 'baggage_issues_negative'})
        print(f"Manager access baggage: {data['success']}")

    db.close()
