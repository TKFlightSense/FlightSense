# services/data_service.py
from __future__ import annotations
from typing import Dict, Union, Optional, List
import logging

import pandas as pd

from services.db_service.db_service import DbService
from services.orchestrator.filter import DataFilter
from services.access_control_service import AccessControlService
from models.enums.enums import SentimentLabel, UserRole

logger = logging.getLogger(__name__)


class DataService:
    """
    Handles data retrieval / analytics with role-based filtering.
    """

    def __init__(self, db_service: DbService, access_control: AccessControlService):
        self.db = db_service
        self.access = access_control

    # ============ DATA RETRIEVAL WITH ROLE-BASED FILTERING ============

    def get_processed_data_filtered(
        self,
        user_info: Dict,
        filters: Union[Dict, DataFilter],
    ) -> Dict:
        """
        Get processed data with filters and role-based access control.
        Users can only see data for their assigned category.
        """
        try:
            if isinstance(filters, dict):
                data_filter = DataFilter.from_dict(filters)
            else:
                data_filter = filters

            validation_errors = data_filter.validate()
            if validation_errors:
                return {
                    "success": False,
                    "error": "Validation failed",
                    "details": validation_errors,
                }

            data_filter.to_enum()

            # Check category access
            if data_filter.label_type:
                if not self.access.can_access_category(
                    user_info["role"], data_filter.label_type
                ):
                    return {
                        "success": False,
                        "error": f"You don't have permission to access {data_filter.label_type.value} data",
                    }

            # If no category specified and user is NOT admin/manager, restrict to their category
            if not data_filter.label_type and not self.access.is_full_access_role(
                user_info["role"]
            ):
                allowed_categories = self.access.get_allowed_categories(
                    user_info["role"]
                )
                if len(allowed_categories) == 1:
                    data_filter.label_type = allowed_categories[0]

            # Query database
            df = self.db.get_processed_data(
                limit=data_filter.limit,
                label_type=data_filter.label_type,
                label_status=data_filter.label_status,
                date_from=data_filter.date_from,
                date_to=data_filter.date_to,
            )

            return {
                "success": True,
                "data": df.to_dict("records"),
                "count": len(df),
                "user_role": user_info["role"],
                "filters_applied": {
                    "limit": data_filter.limit,
                    "label_type": (
                        data_filter.label_type.value if data_filter.label_type else None
                    ),
                    "label_status": (
                        data_filter.label_status.value
                        if data_filter.label_status
                        else None
                    ),
                    "date_from": data_filter.date_from,
                    "date_to": data_filter.date_to,
                },
            }
        except Exception as e:
            logger.error(f"Error getting processed data: {e}")
            return {"success": False, "error": str(e)}

    def get_dashboard_summary(self, user_info: Dict, page: str = "dashboard") -> Dict:
        """
        Get dashboard summary based on user role and requested page.
        - ADMIN/MANAGER: Can access all pages and see all data
        - Subject-specific: Only see their category's data
        """
        try:
            if not self.access.can_access_page(user_info["role"], page):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {page} page",
                }

            allowed_categories = self.access.get_allowed_categories(user_info["role"])
            if not allowed_categories and not self.access.is_full_access_role(
                user_info["role"]
            ):
                return {
                    "success": False,
                    "error": "No data access configured for this role",
                }

            # Get sentiment distribution (filtered by role)
            if self.access.is_full_access_role(user_info["role"]):
                sentiment_dist = self.db.get_sentiment_distribution()
                total_reviews = self.db._get_row_count("processed_data")
            else:
                category = allowed_categories[0]
                df = self.db.get_processed_data(label_type=category)
                total_reviews = len(df)
                sentiment_dist = self._calculate_category_distribution(df, category)

            recent_stats = self.db.get_statistics_data(limit=10)

            return {
                "success": True,
                "data": {
                    "page": page,
                    "total_reviews": total_reviews,
                    "sentiment_distribution": (
                        sentiment_dist.to_dict("records")[0]
                        if hasattr(sentiment_dist, "to_dict")
                        else sentiment_dist
                    ),
                    "recent_statistics": recent_stats.to_dict("records"),
                    "allowed_categories": [cat.value for cat in allowed_categories],
                    "user": {
                        "username": user_info["username"],
                        "role": user_info["role"],
                        "is_full_access": self.access.is_full_access_role(
                            user_info["role"]
                        ),
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {"success": False, "error": str(e)}

    def get_category_analytics(self, user_info: Dict, category: str) -> Dict:
        """
        Get detailed analytics for a specific category.
        Only accessible if user has permission for that category.
        """
        try:
            try:
                category_enum = SentimentLabel[category.upper()]
            except KeyError:
                return {"success": False, "error": f"Invalid category: {category}"}

            if not self.access.can_access_category(user_info["role"], category_enum):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {category} analytics",
                }

            df = self.db.get_processed_data(label_type=category_enum)
            distribution = self._calculate_category_distribution(df, category_enum)

            return {
                "success": True,
                "category": category,
                "analytics": distribution,
                "recent_reviews": df.head(20).to_dict("records"),
            }
        except Exception as e:
            logger.error(f"Error getting category analytics: {e}")
            return {"success": False, "error": str(e)}

    def push_processed_data(self, user_info: Dict, data) -> Dict:
        """Push processed data (admin only)."""
        try:
            if UserRole(user_info["role"]) != UserRole.ADMIN:
                return {"success": False, "error": "Admin privileges required"}

            rows_inserted = self.db.push_processed_data(data)

            return {
                "success": True,
                "rows_inserted": rows_inserted,
                "message": f"Successfully inserted {rows_inserted} rows",
            }
        except Exception as e:
            logger.error(f"Error pushing data: {e}")
            return {"success": False, "error": str(e)}

    # ---------- internal helpers ----------

    @staticmethod
    def _calculate_category_distribution(
        df: pd.DataFrame, category: SentimentLabel
    ) -> Dict:
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
