from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd

from services.db_service.db_service import DbService
from models.labels import ALL_LABELS,PRIORITY_LABELS,SENTIMENT_LABELS

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

    def __init__(
        self,
        db_service: DbService,
        routing_path: str = "models/artifacts/department_routing.json",
    ):
        self.db = db_service
        self.label_to_department, self.department_labels = self._load_routing(
            routing_path
        )

    def get_department_distribution(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict [str, Any]:
        """
        Manager view: how many reviews mapped to each department,
        plus weekly history.
        """
        base_df = self._load_processed_df(date_from, date_to)
        exploded = self._explode_labels(base_df)

        if exploded.empty:
            return {
                "total_reviews": 0,
                "department_counts": {},
                "department_percentages": {},
            }

        dept_counts_series = exploded.groupby("department")["id"].nunique()
        department_counts = dept_counts_series.to_dict()
        total_reviews = exploded["id"].nunique()

        department_percentages = (
            {
                dept: (cnt / total_reviews) * 100.0
                for dept, cnt in department_counts.items()
            }
            if total_reviews > 0
            else {dept: 0.0 for dept in department_counts}
        )
        return {
            "total_reviews": total_reviews,
            "department_counts": department_counts,
            "department_percentages": department_percentages,
        }

    def get_within_department_distribution(self, department_name: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict [str, Any]:
        """
        Ratio of labels WITHIN a given department.
        """
        base_df = self._load_processed_df(date_from, date_to)
        exploded = self._explode_labels(base_df)

        if exploded.empty:
            return {
                "department": department_name,
                "total_reviews": 0,
                "label_counts": {},
                "label_percentages": {},
            }

        dept_df = exploded[exploded["department"] == department_name]

        if dept_df.empty:
            return {
                "department": department_name,
                "total_reviews": 0,
                "label_counts": {},
                "label_percentages": {},
            }
        total_reviews = dept_df["id"].nunique()

        label_counts_series = dept_df.groupby("label")["id"].nunique()
        label_counts = label_counts_series.to_dict()
        label_percentages = (
            {
                label: (cnt / total_reviews) * 100.0
                for label, cnt in label_counts.items()
            }
            if total_reviews > 0
            else {label: 0.0 for label in label_counts}
        )

        return {
            "department": department_name,
            "total_reviews": total_reviews,
            "label_counts": label_counts,
            "label_percentages": label_percentages,
        }

    def get_distribution_of_priority(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict [str, Any]:
        """
        Manager view: high/medium/low distribution across ALL departments,
        restricted to reviews that touch PRIORITY_LABELS.
        """
        return self._priority_distribution(department_name = None, date_from=date_from, date_to=date_to)

    def get_distribution_of_priority_within_department(self, department_name: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Priority distribution within a single department.
        """
        return self._priority_distribution(department_name=department_name, date_from=date_from, date_to=date_to)

    def get_distribution_of_pos_neg(self,  date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Manager view: positive/negative distribution across ALL departments,
        restricted to reviews that touch SENTIMENT_LABELS.
        """
        return self._sentiment_distribution(department_name=None, date_from=date_from, date_to=date_to)

    def get_distribution_of_pos_neg_within_department(self, department_name: str,  date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Positive/negative distribution within a single department.
        """
        return self._sentiment_distribution(department_name=department_name, date_from=date_from, date_to=date_to)

    def get_label_distribution(self,  date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Overall: how many reviews per label.
        """
        base_df = self._load_processed_df(date_from, date_to)
        exploded = self._explode_labels(base_df)

        if exploded.empty:
            return {
                "total_reviews": 0,
                "label_counts": {},
                "label_percentages": {},
            }

        total_reviews = exploded["id"].nunique()
        label_counts_series = exploded.groupby("label")["id"].nunique()
        label_counts = label_counts_series.to_dict()

        label_percentages = (
            {
                label: (cnt / total_reviews) * 100.0
                for label, cnt in label_counts.items()
            }
            if total_reviews > 0
            else {label: 0.0 for label in label_counts}
        )

        return {
            "total_reviews": total_reviews,
            "label_counts": label_counts,
            "label_percentages": label_percentages,
        }

    def _priority_distribution(self, department_name: Optional[str], date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Shared logic for priority distribution.
        department_name=None  -> overall (manager)
        department_name=...   -> specific department
        """
        scope = "overall" if department_name is None else "department"

        base_df = self._load_processed_df(date_from, date_to)
        if base_df.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "priority_counts": {},
                "priority_percentages": {},
            }

        exploded = self._explode_labels(base_df, restrict_labels=PRIORITY_LABELS)
        if exploded.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "priority_counts": {},
                "priority_percentages": {},
            }

        if department_name is not None:
            exploded = exploded[exploded["department"] == department_name]

        if exploded.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "priority_counts": {},
                "priority_percentages": {},
            }

        review_ids = exploded["id"].unique()
        df = base_df[base_df["id"].isin(review_ids)].copy()

        if df.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "priority_counts": {},
                "priority_percentages": {},
            }

        df["priority"] = df["priority"].fillna("unknown")
        valid = df[df["priority"].isin(["high", "medium", "low"])]

        if valid.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "priority_counts": {},
                "priority_percentages": {},
            }

        priority_counts = valid["priority"].value_counts().to_dict()
        total_reviews = len(valid)
        priority_percentages = self._to_percentage(priority_counts)

        return {
            "scope": scope,
            "department": department_name,
            "total_reviews": total_reviews,
            "priority_counts": priority_counts,
            "priority_percentages": priority_percentages,
        }

    def _sentiment_distribution(self, department_name: Optional[str], date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Shared logic for sentiment distribution.
        department_name=None  -> overall (manager)
        department_name=...   -> specific department
        """
        scope = "overall" if department_name is None else "department"

        base_df = self._load_processed_df(date_from, date_to)
        if base_df.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "sentiment_counts": {},
                "sentiment_percentages": {},
            }

        exploded = self._explode_labels(base_df, restrict_labels=SENTIMENT_LABELS)
        if exploded.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "sentiment_counts": {},
                "sentiment_percentages": {},
            }

        if department_name is not None:
            exploded = exploded[exploded["department"] == department_name]

        if exploded.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "sentiment_counts": {},
                "sentiment_percentages": {},
            }

        review_ids = exploded["id"].unique()
        df = base_df[base_df["id"].isin(review_ids)].copy()

        if df.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "sentiment_counts": {},
                "sentiment_percentages": {},
            }

        df["sentiment"] = df["sentiment"].fillna("unknown")
        valid = df[df["sentiment"].isin(["positive", "negative"])]

        if valid.empty:
            return {
                "scope": scope,
                "department": department_name,
                "total_reviews": 0,
                "sentiment_counts": {},
                "sentiment_percentages": {},
            }

        sentiment_counts = valid["sentiment"].value_counts().to_dict()
        total_reviews = len(valid)
        sentiment_percentages = self._to_percentage(sentiment_counts)

        return {
            "scope": scope,
            "department": department_name,
            "total_reviews": total_reviews,
            "sentiment_counts": sentiment_counts,
            "sentiment_percentages": sentiment_percentages,
        }

    # =============== HELPERS =============== #
    def _load_routing(
        self, routing_path: str
    ) -> tuple[Dict[str, str], Dict[str, list[str]]]:
        """
        Load label → department routing configuration from JSON.
        {
          "label_to_department": { "label": "DepartmentName", ... },
          "department_labels": { "DepartmentName": ["label1", "label2", ...], ... }
        }
        """
        path = Path(routing_path)
        if not path.exists():
            logger.warning(
                f"Department routing config not found at {path}. "
                f"Using empty mappings."
            )
            return {}, {}

        with path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        label_to_department = cfg.get("label_to_department", {})
        department_labels = cfg.get("department_labels", {})

        return label_to_department, department_labels

    def _load_processed_df(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load processed_data with optional date filtering and normalize
        missing columns (priority, sentiment).
        """
        df = self.db.get_processed_data(
            limit=None,
            label_type=None,
            date_from=date_from,
            date_to=date_to,
        )

        if df.empty:
            return df

        # Normalize expected columns if missing
        for col in ["priority", "sentiment"]:
            if col not in df.columns:
                df[col] = None

        return df

    def _explode_labels(
        self,
        df: pd.DataFrame,
        restrict_labels: Optional[set[str]] = None,
    ) -> pd.DataFrame:
        """
        Turn each review row into multiple rows: one per (review, label).
        Adds:
          - label: fine-grained label string
          - department: mapped from label_to_department, or 'UNKNOWN'
        If restrict_labels is provided, keep only rows whose label is in that set.
        """
        if df.empty:
            return df

        df = df.copy()
        df["labels"] = df["labels"].fillna("")
        df = df[df["labels"] != ""]

        # split comma-separated labels into list
        df["label"] = df["labels"].str.split(",")
        # explode list into separate rows
        df = df.explode("label")
        df["label"] = df["label"].str.strip()

        # Keep only canonical labels
        df = df[df["label"].isin(ALL_LABELS)]

        if restrict_labels is not None:
            df = df[df["label"].isin(restrict_labels)]

        # Map label -> department
        df["department"] = df["label"].map(self.label_to_department).fillna(
            "UNKNOWN"
        )

        return df

    @staticmethod
    def _to_percentage(counts: Dict[str, int]) -> Dict[str, float]:
        total = sum(counts.values())
        if total == 0:
            return {k: 0.0 for k in counts}
        return {k: (v / total) * 100.0 for k, v in counts.items()}

    # trend functions?
    #
    # @staticmethod
    # def _week_key(series: pd.Series) -> pd.Series:
    #     """
    #     Group dates weekly using ISO calendar week: YYYY-Www
    #     Example: 2025-11-20 -> "2025-W47"
    #     """
    #     return pd.to_datetime(series).dt.strftime("%G-W%V")
