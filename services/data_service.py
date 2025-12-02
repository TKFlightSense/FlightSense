from __future__ import annotations
from typing import Dict, Union
import logging

import pandas as pd

from services.db_service.db_service import DbService
from services.orchestrator.filter import DataFilter
from services.access_control_service import AccessControlService

logger = logging.getLogger(__name__)


class DataService:
    """
    Handles data retrieval / analytics with role-based filtering.
    Uses plain-string roles and labels.
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
        Users can only see data for their assigned labels/categories.
        """
        try:
            role = user_info["role"]

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

            if data_filter.label_type:
                if not self.access.can_access_label(role, data_filter.label_type):
                    return {
                        "success": False,
                        "error": f"You don't have permission to access {data_filter.label_type} data",
                    }

            # If no label specified and user is NOT admin/manager, try to restrict to a single label
            if (
                not data_filter.label_type
                and not self.access.is_full_access_role(role)
            ):
                allowed_labels = self.access.get_allowed_labels(role)
                if len(allowed_labels) == 1:
                    data_filter.label_type = allowed_labels[0]

            # Query database
            df = self.db.get_processed_data(
                limit=data_filter.limit,
                label_type=data_filter.label_type,
                date_from=data_filter.date_from,
                date_to=data_filter.date_to,
            )

            return {
                "success": True,
                "data": df.to_dict("records"),
                "count": len(df),
                "user_role": role,
                "filters_applied": {
                    "limit": data_filter.limit,
                    "label_type": data_filter.label_type,
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
        - admin/manager: can access all pages and see all data
        - others: only see their relevant category/labels.
        """
        try:
            role = user_info["role"]

            if not self.access.can_access_page(role, page):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {page} page",
                }

            if self.access.is_full_access_role(role):
                sentiment_dist = self.db.get_sentiment_distribution()
                total_reviews = self.db._get_row_count("processed_data")
            else:
                # For non-full roles, you can either:
                #  - filter by a coarse column, or
                #  - just show global stats but indicate limited view.
                # For now, reuse global stats.
                sentiment_dist = self.db.get_sentiment_distribution()
                total_reviews = self.db._get_row_count("processed_data")

            recent_stats = self.db.get_statistics_data(limit=10)
            allowed_labels = self.access.get_allowed_labels(role)

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
                    "allowed_labels": allowed_labels,
                    "user": {
                        "username": user_info["username"],
                        "role": role,
                        "is_full_access": self.access.is_full_access_role(role),
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {"success": False, "error": str(e)}

    def get_category_analytics(self, user_info: Dict, label: str) -> Dict:
        """
        Get detailed analytics for a specific label/category.
        Only accessible if user has permission for that label.
        """
        try:
            role = user_info["role"]

            if not self.access.can_access_label(role, label):
                return {
                    "success": False,
                    "error": f"You don't have permission to access {label} analytics",
                }

            # Here we assume label maps to a column or is used in SQL.
            df = self.db.get_processed_data(label_type=label)

            # Very simple analytics: count rows + maybe more later
            total = len(df)

            return {
                "success": True,
                "label": label,
                "analytics": {
                    "total_reviews": total,
                },
                "recent_reviews": df.head(20).to_dict("records"),
            }
        except Exception as e:
            logger.error(f"Error getting category analytics: {e}")
            return {"success": False, "error": str(e)}

    def push_processed_data(self, user_info: Dict, data) -> Dict:
        """Push processed data (admin only)."""
        try:
            role = user_info["role"]
            if role != "admin":
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
