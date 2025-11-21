from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import logging

import pandas as pd

from packages.llm.client import LLMClient
from packages.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)


def _load_llm_config() -> Dict[str, Any]:
    """Load LLM configuration from JSON file."""
    config_path = Path("models/artifacts/llm_config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"LLM config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load configuration from JSON file
_LLM_CONFIG = _load_llm_config()


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

    def __init__(self, llm_client: Optional[LLMClient] = None, prompt_builder: Optional[PromptBuilder] = None):
        try:
            self.llm_client = llm_client or LLMClient()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}")
            self.llm_client = None
        self.prompt_builder = prompt_builder or PromptBuilder()

    def label_review(self, review: str, max_segments: Optional[int] = None) -> Dict[str, Any]:
        """
        Label a single review and return segments with labels.
        Returns: {"segments": [{"start": int, "length": int, "label": str}, ...]}
        """
        if self.llm_client is None:
            logger.error("LLM client not initialized")
            return {"segments": []}
        
        if max_segments is None:
            max_segments = _LLM_CONFIG["max_segments"]
        
        prompt = self.prompt_builder.build_classification_messages(review, max_segments)
        raw = self.llm_client.complete(prompt).strip()
        
        try:
            data = json.loads(raw)
            return data
        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON. Raw response: %s", raw)
            return {"segments": []}

    def _call_llm(self, feedback: str) -> ClassificationResult:
        """
        Internal method for batch classification.
        Calls label_review and extracts labels from segments.
        """
        segments_result = self.label_review(feedback, max_segments=5)
        segments = segments_result.get("segments", [])
        
        # Extract unique labels from segments
        labels = list(set(seg["label"] for seg in segments))
        
        # Map fine-grained labels to coarse categories
        # Initialize all categories to 0
        categories = {col: 0 for col in MAIN_CATEGORY_COLUMNS}
        
        # Simple mapping logic
        for label in labels:
            if "delay" in label or "cancellation" in label:
                categories["flight_delay_cancellation"] = -1
            elif "checkin" in label or "boarding" in label:
                categories["checkin_boarding_process"] = -1
            elif "baggage" in label:
                categories["baggage_issues"] = -1
            elif "inflight_experience" in label:
                categories["inflight_experience"] = -1
            elif "pricing" in label or "loyalty" in label:
                categories["pricing_fees"] = -1
            elif "booking" in label or "ticketing" in label:
                categories["online_booking"] = -1
        
        # Determine overall sentiment based on presence of negative labels
        sentiment = "negative" if any(v == -1 for v in categories.values()) else "neutral"
        
        return ClassificationResult(
            categories=categories,
            sentiment=sentiment,
            subcategories={},
            summary="",
        )

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
            # Get segments with fine-grained labels
            segments_result = self.label_review(text, max_segments=5)
            segments = segments_result.get("segments", [])
            
            # Extract unique fine-grained labels from segments
            fine_labels = list(set(seg["label"] for seg in segments))
            labels_str = ",".join(fine_labels)
            
            # Get coarse categories for the category columns
            result = self._call_llm(text)
            cat_values: Dict[str, int] = {
                col: int(result.categories.get(col, 0)) for col in MAIN_CATEGORY_COLUMNS
            }

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
