from __future__ import annotations

import logging
from typing import Dict
from datetime import datetime, timedelta

from services.db_service.mysql_db_service import MySQLDbService

logger = logging.getLogger(__name__)

class StatisticsService:
    """
    Computes analytics from the processed_data table.

    - works with fine-grained labels (comma-separated in 'labels' column)
    - routes labels to departments using department_routing.json
    - supports priority and sentiment segmentations if columns exist:
        processed_data.priority   in ('high', 'medium', 'low')
        processed_data.sentiment  in  ('positive', 'negative')
    """

    def __init__(self, db_service: MySQLDbService):
        self.db = db_service


    @staticmethod
    def _to_percentage(counts: Dict[str, int]) -> Dict[str, float]:
        total = sum(counts.values())
        if total == 0:
            return {k: 0.0 for k in counts}
        return {k: (v / total) * 100.0 for k, v in counts.items()}

    def get_label_sentiment_distribution(self, label: str, date_from: datetime, date_to: datetime):
        positive_counts = self.db.get_label_positive_counts(label, date_from, date_to)
        negative_counts = self.db.get_label_negative_counts(label, date_from, date_to)
        neutral_counts = self.db.get_label_neutral_counts(label, date_from, date_to)

        sentiment_counts_dict = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}
        sentiment_percentage_dict = self._to_percentage(sentiment_counts_dict)
        return {
            "counts": sentiment_counts_dict,
            "percentage": sentiment_percentage_dict
        }
    
    def get_label_priority_distribution(self, label: str, date_from: datetime, date_to: datetime):
        high_counts = self.db.get_label_high_counts(label, date_from, date_to)
        low_counts = self.db.get_label_low_counts(label, date_from, date_to)
        medium_counts = self.db.get_label_medium_counts(label, date_from, date_to)

        priority_counts_dict = {"high": high_counts, "medium": medium_counts, "low": low_counts}
        priority_percentage_dict = self._to_percentage(priority_counts_dict)
        return {
            "counts": priority_counts_dict,
            "percentage": priority_percentage_dict
        }
    
    def get_department_sentiment_distribution(self, department_name: str, date_from: datetime, date_to: datetime):
        positive_counts = self.db.get_department_positive_counts(department_name, date_from, date_to)
        negative_counts = self.db.get_department_negative_counts(department_name, date_from, date_to)
        neutral_counts = self.db.get_department_neutral_counts(department_name, date_from, date_to)

        sentiment_counts_dict = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}
        sentiment_percentage_dict = self._to_percentage(sentiment_counts_dict)
        return {
            "counts": sentiment_counts_dict,
            "percentage": sentiment_percentage_dict
        }
    
    def get_department_priority_distribution(self, department_name: str, date_from: datetime, date_to: datetime):
        high_counts = self.db.get_department_high_counts(department_name, date_from, date_to)
        medium_counts = self.db.get_department_medium_counts(department_name, date_from, date_to)
        low_counts = self.db.get_department_low_counts(department_name, date_from, date_to)

        priority_counts_dict = {"high": high_counts, "medium": medium_counts, "low": low_counts}
        priority_percentage_dict = self._to_percentage(priority_counts_dict)
        return {
            "counts": priority_counts_dict,
            "percentage": priority_percentage_dict
        }
    
    def get_department_total_review_count(self, department_name: str, date_from: datetime, date_to: datetime):
        return self.db.get_department_total_count(department_name, date_from, date_to)
    
    def get_department_weekly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2025-12-01 00:00:00
        date_to: 2025-12-08 00:00:00 #anlaması kolay olsun diye
        """
        weekly_stats_dict = {}
        for i in range(7):
            key = f"day_{i+1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i+1)
            positive_counts = self.db.get_department_positive_counts(department_name, internal_date_from, internal_date_to)
            negative_counts = self.db.get_department_negative_counts(department_name, internal_date_from, internal_date_to)
            weekly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return weekly_stats_dict

    def get_department_monthly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2025-11-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        monthly_stats_dict = {}
        for i in range(4):
            key = f"week_{i+1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i+1)
            positive_counts = self.db.get_department_positive_counts(department_name, internal_date_from, internal_date_to)
            negative_counts = self.db.get_department_negative_counts(department_name, internal_date_from, internal_date_to)
            monthly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return monthly_stats_dict

    def get_department_yearly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2024-12-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        yearly_stats_dict = {}
        for i in range(12):
            key = f"month_{i+1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i+1)
            positive_counts = self.db.get_department_positive_counts(department_name, internal_date_from, internal_date_to)
            negative_counts = self.db.get_department_negative_counts(department_name, internal_date_from, internal_date_to)
            yearly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return yearly_stats_dict

    def get_manager_sentiment_distribution(self, date_from: datetime, date_to: datetime):
        positive_counts = self.db.get_manager_positive_counts(date_from, date_to)
        negative_counts = self.db.get_manager_negative_counts(date_from, date_to)
        neutral_counts = self.db.get_manager_neutral_counts(date_from, date_to)

        sentiment_counts_dict = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}
        sentiment_percentage_dict = self._to_percentage(sentiment_counts_dict)
        return {
            "counts": sentiment_counts_dict,
            "percentage": sentiment_percentage_dict
        }

    def get_manager_priority_distribution(self, date_from: datetime, date_to: datetime):
        high_counts = self.db.get_manager_high_counts(date_from, date_to)
        medium_counts = self.db.get_manager_medium_counts(date_from, date_to)
        low_counts = self.db.get_manager_low_counts(date_from, date_to)

        priority_counts_dict = {"high": high_counts, "medium": medium_counts, "low": low_counts}
        priority_percentage_dict = self._to_percentage(priority_counts_dict)
        return {
            "counts": priority_counts_dict,
            "percentage": priority_percentage_dict
        }

    def get_manager_total_review_count(self, date_from: datetime, date_to: datetime):
        return self.db.get_manager_total_count(date_from, date_to)

    def get_manager_weekly_stats(self, date_from: datetime):
        """
        date_from: 2025-12-01 00:00:00
        date_to: 2025-12-08 00:00:00 #anlaması kolay olsun diye
        """
        weekly_stats_dict = {}
        for i in range(7):
            key = f"day_{i + 1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i + 1)
            positive_counts = self.db.get_manager_positive_counts(internal_date_from, internal_date_to)
            negative_counts = self.db.get_manager_negative_counts(internal_date_from, internal_date_to)
            weekly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return weekly_stats_dict

    def get_manager_monthly_stats(self,date_from: datetime):
        """
        date_from: 2025-11-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        monthly_stats_dict = {}
        for i in range(4):
            key = f"week_{i + 1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i + 1)
            positive_counts = self.db.get_manager_positive_counts(internal_date_from, internal_date_to)
            negative_counts = self.db.get_manager_negative_counts(internal_date_from, internal_date_to)
            monthly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return monthly_stats_dict

    def get_manager_yearly_stats(self, date_from: datetime):
        """
        date_from: 2024-12-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        yearly_stats_dict = {}
        for i in range(12):
            key = f"month_{i + 1}"
            internal_date_from = date_from + timedelta(days=i)
            internal_date_to = date_from + timedelta(days=i + 1)
            positive_counts = self.db.get_manager_positive_counts(internal_date_from, internal_date_to)
            negative_counts = self.db.get_manager_negative_counts(internal_date_from, internal_date_to)
            yearly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts}

        return yearly_stats_dict
