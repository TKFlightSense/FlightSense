from __future__ import annotations
from typing import List, Dict, Any, Optional
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
        - Provides helpers to convert LLM segment output into a tabular form
            (`segments_to_table`) which the orchestrator will call when new rows
            appear in the `reviews` table.
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



    def segments_to_table(self, review_id: int, segments: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert LLM segments for a single review into a DataFrame table.

        Output columns (in this order): review_id, label, index, sentiment, priority

        - index is formatted as "start:end" where end = start + length
        - sentiment and priority default to 'NONE' / 'unknown' if missing
        """
        rows: List[Dict[str, Any]] = []
        for seg in segments:
            start = seg.get("start")
            length = seg.get("length")
            if isinstance(start, int) and isinstance(length, int):
                index_str = f"{start}:{start + length}"
            else:
                # If start/length missing or non-int, fall back to empty string
                index_str = ""

            rows.append({
                "review_id": review_id,
                "label": seg.get("label"),
                "index": index_str,
                "sentiment": seg.get("sentiment", "NONE"),
                "priority": seg.get("priority", "unknown"),
            })

        df = pd.DataFrame(rows)
        # Ensure column order: id then label, per your request
        cols = ["review_id", "label", "index", "sentiment", "priority"]
        for c in cols:
            if c not in df.columns:
                df[c] = None
        return df[cols]
