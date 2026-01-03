from __future__ import annotations

import logging
from typing import Dict, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional
from models.enums.enums import LabelToDepartment, DepartmentToLabels, Departments

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

    def __init__(self, db_service: Optional[MySQLDbService] = None):
        self.db = db_service if db_service is not None else MySQLDbService()
        self.departments = Departments
        self.label_to_department = LabelToDepartment

    @staticmethod
    def _to_percentage(counts: Dict[str, int]) -> Dict[str, float]:
        total = sum(counts.values())
        if total == 0:
            return {k: 0.0 for k in counts}
        return {k: round((v / total) * 100.0) for k, v in counts.items()}

    def get_label_sentiment_distribution(self, label: str, date_from: datetime, date_to: datetime):
        department_name = self.label_to_department[label].value
        positive_counts = self.db.get_label_positive_counts(label, department_name, date_from, date_to)
        negative_counts = self.db.get_label_negative_counts(label, department_name, date_from, date_to)
        neutral_counts = self.db.get_label_neutral_counts(label, department_name, date_from, date_to)

        sentiment_counts_dict = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}
        sentiment_percentage_dict = self._to_percentage(sentiment_counts_dict)
        return {
            "counts": sentiment_counts_dict,
            "percentage": sentiment_percentage_dict
        }
    
    def get_label_priority_distribution(self, label: str, date_from: datetime, date_to: datetime):
        department_name = self.label_to_department[label].value
        high_counts = self.db.get_label_high_counts(label, department_name, date_from, date_to)
        low_counts = self.db.get_label_low_counts(label, department_name, date_from, date_to)
        medium_counts = self.db.get_label_medium_counts(label, department_name, date_from, date_to)

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

    def get_department_label_distribution (self, department_name:str,date_from: datetime, date_to: datetime):
        label_distribution = {}
        for label in DepartmentToLabels[department_name].value:
            label_distribution[label] = self.get_label_sentiment_distribution(label, date_from, date_to)
        return label_distribution

    def get_department_weekly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2025-12-01 00:00:00
        date_to: 2025-12-08 00:00:00 #anlaması kolay olsun diye
        """
        weekly_stats_dict = {}
        labels = DepartmentToLabels[department_name].value
        for i in range(7):
            key = f"day_{i+1}"
            internal_date_from = date_from + relativedelta(days=i)
            internal_date_to = date_from + relativedelta(days=i+1)
            counts = self.db.get_sentiment_counts_by_review_date(
                internal_date_from,
                internal_date_to,
                labels=labels,
            )
            weekly_stats_dict[key] = counts

        return weekly_stats_dict

    def get_department_monthly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2025-11-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        monthly_stats_dict = {}
        labels = DepartmentToLabels[department_name].value
        for i in range(4):
            key = f"week_{i+1}"
            internal_date_from = date_from + relativedelta(weeks=i)
            internal_date_to = date_from + relativedelta(weeks=i+1)
            counts = self.db.get_sentiment_counts_by_review_date(
                internal_date_from,
                internal_date_to,
                labels=labels,
            )
            monthly_stats_dict[key] = counts

        return monthly_stats_dict

    def get_department_yearly_stats(self, department_name: str, date_from: datetime):
        """
        date_from: 2024-12-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        yearly_stats_dict = {}
        labels = DepartmentToLabels[department_name].value
        for i in range(12):
            key = f"month_{i+1}"
            internal_date_from = date_from + relativedelta(months=i)
            internal_date_to = date_from + relativedelta(months=i+1)
            counts = self.db.get_sentiment_counts_by_review_date(
                internal_date_from,
                internal_date_to,
                labels=labels,
            )
            yearly_stats_dict[key] = counts

        return yearly_stats_dict

    def get_manager_sentiment_distribution(self, date_from: datetime, date_to: datetime):
        department_sentiment_distributions = {}
        for department in self.departments:
            department_sentiment_distribution = self.get_department_sentiment_distribution(department.name, date_from, date_to)
            department_sentiment_distributions[department.value] = {"sentiment": department_sentiment_distribution}
        
        positive_counts = 0
        negative_counts = 0
        neutral_counts = 0

        for department_stats in department_sentiment_distributions.values():
            positive_counts += department_stats["sentiment"]["counts"]["positive"]
            negative_counts += department_stats["sentiment"]["counts"]["negative"]
            neutral_counts += department_stats["sentiment"]["counts"]["neutral"]

        sentiment_counts_dict = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}
        sentiment_percentage_dict = self._to_percentage(sentiment_counts_dict)
        return {
            "counts": sentiment_counts_dict,
            "percentage": sentiment_percentage_dict,
            "department_sentiment_distribution": department_sentiment_distributions
        }

    def get_manager_review_count_distribution(self, date_from: datetime, date_to: datetime):
        department_review_counts = {}
        total_count = 0
        for department in self.departments:
            department_total_count = self.get_department_total_review_count(department.name, date_from, date_to)
            department_review_counts[department.value] = department_total_count
            total_count += department_total_count

        department_review_percentages = self._to_percentage(department_review_counts)
        return {
            "department_counts": department_review_counts,
            "department_percentages": department_review_percentages,
            "total_count": total_count
        }

    def get_manager_priority_distribution(self, date_from: datetime, date_to: datetime):
        department_priority_distributions = {}
        for department in self.departments:
            department_priority_distribution = self.get_department_priority_distribution(department.name, date_from, date_to)
            department_priority_distributions[department.value] = {"priority": department_priority_distribution}
        
        high_counts = 0
        medium_counts = 0
        low_counts = 0

        for department_stats in department_priority_distributions.values():
            high_counts += department_stats["priority"]["counts"]["high"]
            medium_counts += department_stats["priority"]["counts"]["medium"]
            low_counts += department_stats["priority"]["counts"]["low"]

        priority_counts_dict = {"high": high_counts, "medium": medium_counts, "low": low_counts}
        priority_percentage_dict = self._to_percentage(priority_counts_dict)
        return {
            "counts": priority_counts_dict,
            "percentage": priority_percentage_dict,
            "department_priority_distribution": department_priority_distributions
        }

    def get_manager_positive_negative_neutral_counts(self, date_from: datetime, date_to: datetime):
        counts = self.db.get_sentiment_counts_by_review_date(date_from, date_to)
        return counts["positive"], counts["negative"], counts["neutral"]

    def get_manager_weekly_stats(self, date_from: datetime):
        """
        date_from: 2025-12-01 00:00:00
        date_to: 2025-12-08 00:00:00 #anlaması kolay olsun diye
        """
        weekly_stats_dict = {}
        for i in range(7):
            key = f"day_{i + 1}"
            internal_date_from = date_from + relativedelta(days=i)
            internal_date_to = date_from + relativedelta(days=i + 1)
            positive_counts, negative_counts, neutral_counts = self.get_manager_positive_negative_neutral_counts(internal_date_from, internal_date_to)
            weekly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}

        return weekly_stats_dict

    def get_manager_monthly_stats(self, date_from: datetime):
        """
        date_from: 2025-11-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        monthly_stats_dict = {}
        for i in range(4):
            key = f"week_{i + 1}"
            internal_date_from = date_from + relativedelta(weeks=i)
            internal_date_to = date_from + relativedelta(weeks=i + 1)
            positive_counts, negative_counts, neutral_counts = self.get_manager_positive_negative_neutral_counts(internal_date_from, internal_date_to)
            monthly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}

        return monthly_stats_dict

    def get_manager_yearly_stats(self, date_from: datetime):
        """
        date_from: 2024-12-01 00:00:00
        date_to: 2025-12-01 00:00:00
        """
        yearly_stats_dict = {}
        for i in range(12):
            key = f"month_{i + 1}"
            internal_date_from = date_from + relativedelta(months=i)
            internal_date_to = date_from + relativedelta(months=i + 1)
            positive_counts, negative_counts, neutral_counts = self.get_manager_positive_negative_neutral_counts(internal_date_from, internal_date_to)
            yearly_stats_dict[key] = {"positive": positive_counts, "negative": negative_counts, "neutral": neutral_counts}

        return yearly_stats_dict

