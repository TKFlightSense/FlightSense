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

    def _normalize_segments(
        self,
        review: str,
        raw_segments: Any,
        max_segments: int,
    ) -> List[Dict[str, Any]]:
        """
        Best-effort validation/normalization for model output.

        Enforces:
          - list-of-dicts segments
          - valid bounds (0 <= start < len(review), 0 < length, start+length <= len(review))
          - allowed labels only (from label_map.json via PromptBuilder)
          - canonical sentiment/priority values
          - non-overlapping, start-sorted segments
          - max_segments cap (keeps most severe/actionable)
        """
        if not isinstance(raw_segments, list):
            return []

        allowed_labels = set(self.prompt_builder.labels.keys())
        review_len = len(review)

        def coerce_int(value: Any) -> Optional[int]:
            if isinstance(value, bool):  # bool is an int subclass; reject explicitly
                return None
            if isinstance(value, int):
                return value
            if isinstance(value, float) and value.is_integer():
                return int(value)
            if isinstance(value, str):
                value = value.strip()
                if value.isdigit():
                    try:
                        return int(value)
                    except Exception:
                        return None
            return None

        def normalize_priority(value: Any) -> str:
            if not isinstance(value, str):
                return "LOW"
            value = value.strip().upper()
            if value in {"HIGH", "MEDIUM", "LOW"}:
                return value
            # common variants
            if value == "MID":
                return "MEDIUM"
            return "LOW"

        def normalize_sentiment(value: Any) -> str:
            if not isinstance(value, str):
                return "NEUTRAL"
            value = value.strip().upper()
            if value in {"POSITIVE", "NEGATIVE", "NEUTRAL", "NONE"}:
                return value
            return "NEUTRAL"

        normalized: List[Dict[str, Any]] = []

        for seg in raw_segments:
            if not isinstance(seg, dict):
                continue

            raw_label = seg.get("label")
            if not isinstance(raw_label, str):
                continue
            label = raw_label.strip()
            if label not in allowed_labels:
                # Be tolerant to casing mistakes (labels are canonical lowercase)
                label_lower = label.lower()
                if label_lower in allowed_labels:
                    label = label_lower
                else:
                    continue

            start = coerce_int(seg.get("start"))
            length = coerce_int(seg.get("length"))
            if start is None or length is None:
                continue
            if start < 0 or length <= 0 or start + length > review_len:
                continue

            normalized.append(
                {
                    "start": start,
                    "length": length,
                    "label": label,
                    "priority": normalize_priority(seg.get("priority")),
                    "sentiment": normalize_sentiment(seg.get("sentiment")),
                }
            )

        # Sort and drop overlaps (keep earliest segments)
        normalized.sort(key=lambda s: (s["start"], -(s["length"])))
        non_overlapping: List[Dict[str, Any]] = []
        last_end = 0
        for seg in normalized:
            if seg["start"] < last_end:
                continue
            non_overlapping.append(seg)
            last_end = seg["start"] + seg["length"]

        # De-duplicate labels: keep at most one segment per label.
        # If the model returned multiple segments with the same label,
        # keep the most severe/actionable one.
        priority_weight = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        sentiment_weight = {"NEGATIVE": 3, "NEUTRAL": 2, "POSITIVE": 1, "NONE": 0}
        best_by_label: Dict[str, Dict[str, Any]] = {}
        for seg in non_overlapping:
            label = seg["label"]
            score = (
                priority_weight.get(seg["priority"], 0),
                sentiment_weight.get(seg["sentiment"], 0),
                seg["length"],
            )
            existing = best_by_label.get(label)
            if existing is None:
                best_by_label[label] = {**seg, "_score": score}
                continue
            if score > existing.get("_score", (0, 0, 0)):
                best_by_label[label] = {**seg, "_score": score}

        deduped = [{k: v for k, v in seg.items() if k != "_score"} for seg in best_by_label.values()]
        deduped.sort(key=lambda s: (s["start"], -(s["length"])))

        if len(deduped) <= max_segments:
            return deduped

        # Too many segments: keep the most severe/actionable, then re-sort by start
        ranked = sorted(
            deduped,
            key=lambda s: (
                priority_weight.get(s["priority"], 0),
                sentiment_weight.get(s["sentiment"], 0),
                s["length"],
            ),
            reverse=True,
        )[:max_segments]
        ranked.sort(key=lambda s: s["start"])
        return ranked

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
            return {"segments": [], "error": "LLM client not initialized"}
        
        if max_segments is None:
            max_segments = _LLM_CONFIG["max_segments"]
        
        prompt = self.prompt_builder.build_classification_messages(review, max_segments)
        logger.debug("Classification prompt length: %d chars", len(prompt))
        raw = self.llm_client.complete(prompt, json_mode=True).strip()
        
        if not raw:
            provider = getattr(self.llm_client, "provider", "unknown")
            model = getattr(self.llm_client, "model", "unknown")
            logger.error(
                "LLM returned empty response (provider=%s model=%s) for review: %s...",
                provider,
                model,
                review[:100],
            )
            return {"segments": [], "error": "LLM returned empty response"}
        
        try:
            data = json.loads(raw)
            segments = self._normalize_segments(
                review=review,
                raw_segments=data.get("segments"),
                max_segments=max_segments,
            )
            return {"segments": segments}
        except json.JSONDecodeError:
            logger.error("LLM returned invalid JSON. Raw response: %s", raw[:500])
            return {"segments": [], "error": "LLM returned invalid JSON"}



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
