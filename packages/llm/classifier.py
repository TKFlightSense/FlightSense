from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import date
import json
import logging

import pandas as pd

from packages.llm.client import LLMClient
from packages.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)


MAIN_CATEGORY_COLUMNS = [
    "flight_delay_cancellation",
    "checkin_boarding_process",
    "baggage_issues",
    "inflight_experience",
    "pricing_fees",
    "online_booking",
]


@dataclass
class ClassificationResult:
    """
    Typed representation of the LLM response.
    """

    categories: Dict[str, int]
    sentiment: str
    subcategories: Dict[str, List[str]]
    summary: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClassificationResult":
        # Basic validation + defaults
        categories = data.get("categories", {})
        sentiment = data.get("sentiment", "neutral")
        subcategories = data.get("subcategories", {})
        summary = data.get("summary", "")
        return cls(
            categories=categories,
            sentiment=sentiment,
            subcategories=subcategories,
            summary=summary,
        )


class FeedbackClassifier:
    """
    High-level service:
    - builds prompts,
    - calls LLM,
    - parses JSON,
    - returns DataFrame matching processed_data schema.
    """

    def __init__(self, llm_client: LLMClient, prompt_builder: Optional[PromptBuilder] = None):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder or PromptBuilder()

    def _call_llm(self, feedback: str) -> ClassificationResult:
        messages = self.prompt_builder.build_classification_messages(feedback)
        raw = self.llm_client.complete(messages).strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON. Raw response: %s", raw)
            # Fallback: mark everything as 0/neutral
            data = {
                "categories": {col: 0 for col in MAIN_CATEGORY_COLUMNS},
                "sentiment": "neutral",
                "subcategories": {},
                "summary": "",
            }

        return ClassificationResult.from_dict(data)

    def classify_batch(
        self,
        feedbacks: List[str],
        dates: Optional[List[date]] = None,
    ) -> pd.DataFrame:
        """
        Classify a batch of feedback strings and return a DataFrame ready to insert
        into the processed_data table.

        processed_data schema (from your DbService):
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            labels TEXT,
            flight_delay_cancellation INTEGER,
            checkin_boarding_process INTEGER,
            baggage_issues INTEGER,
            inflight_experience INTEGER,
            pricing_fees INTEGER,
            online_booking INTEGER,
            date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """
        rows: List[Dict[str, Any]] = []
        today = date.today()

        for idx, text in enumerate(feedbacks):
            result = self._call_llm(text)

            # Ensure all main columns exist; default to 0
            cat_values: Dict[str, int] = {
                col: int(result.categories.get(col, 0)) for col in MAIN_CATEGORY_COLUMNS
            }

            # labels text = comma-separated active main categories
            active_labels = [k for k, v in cat_values.items() if v != 0]
            labels_str = ",".join(active_labels)

            row_date = dates[idx] if dates and idx < len(dates) else today

            row: Dict[str, Any] = {
                "review": text,
                "labels": labels_str,
                "date": row_date.isoformat(),
                # main category columns:
                **cat_values,
                # (optional) you can persist sentiment/subcategories in extra columns
                # or in a separate table later if you want.
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        return df
