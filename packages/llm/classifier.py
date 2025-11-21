from __future__ import annotations
from typing import List, Dict, Any, Optional
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


class FeedbackClassifier:
    """
    High-level service for classifying airline passenger feedback.
    - Builds prompts with fine-grained labels from label_map.json
    - Calls LLM to segment and label feedback
    - Returns DataFrame ready for database insertion
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
        Label a single review and return segments with fine-grained labels.
        
        Args:
            review: Customer feedback text
            max_segments: Maximum number of segments to extract (default from config)
            
        Returns:
            {"segments": [{"start": int, "length": int, "label": str}, ...]}
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

    def classify_batch(
        self,
        feedbacks: List[str],
        dates: Optional[List[date]] = None,
    ) -> pd.DataFrame:
        """
        Classify a batch of feedback strings and return a DataFrame ready to insert
        into the processed_data table.

        Args:
            feedbacks: List of customer feedback text
            dates: Optional list of dates corresponding to each feedback
            
        Returns:
            DataFrame with columns: review, labels, date
        """
        rows: List[Dict[str, Any]] = []
        today = date.today()

        for idx, text in enumerate(feedbacks):
            # Get segments with fine-grained labels (single LLM call)
            segments_result = self.label_review(text, max_segments=5)
            segments = segments_result.get("segments", [])
            
            # Extract unique fine-grained labels from segments
            fine_labels = list(set(seg["label"] for seg in segments))
            labels_str = ",".join(fine_labels)

            row_date = dates[idx] if dates and idx < len(dates) else today

            row: Dict[str, Any] = {
                "review": text,
                "labels": labels_str,
                "date": row_date.isoformat(),
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        return df
