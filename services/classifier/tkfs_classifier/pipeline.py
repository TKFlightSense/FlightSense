from __future__ import annotations

from typing import Dict, List
import json
import os
from pathlib import Path

from tkfs_common.enums import DEPT_PAIRS
from tkfs_common.schemas import ReviewIn

LABEL_MAP_PATH = Path(os.getenv("LABEL_MAP_PATH", "models/artifacts/label_map.json"))
THRESHOLDS_PATH = Path(os.getenv("THRESHOLDS_PATH", "models/artifacts/thresholds.json"))
TOPK: int = int(os.getenv("CLASSIFIER_TOPK", "3"))

# Load labels / thresholds once at import time
if LABEL_MAP_PATH.exists():
    _label_map = json.loads(LABEL_MAP_PATH.read_text())
    LABELS: List[str] = list(_label_map.get("labels", []))
else:
    LABELS = []

if THRESHOLDS_PATH.exists():
    THRESH: Dict[str, float] = json.loads(THRESHOLDS_PATH.read_text())
else:
    THRESH = {lbl: 0.5 for lbl in LABELS}

__all__ = ["run_model", "postprocess_scores", "LABELS", "THRESH", "TOPK"]


def run_model(review: ReviewIn) -> Dict[str, float]:
    """
    Dummy model for wiring/CI. Replace with real inference.
    Returns a probability for each of the 12 labels.
    """
    # Example: give two labels higher scores so postprocess picks them.
    base = 0.10
    scores: Dict[str, float] = {lbl: base for lbl in LABELS}
    if "delay" in review.text.lower():
        for k in ("flight_delay_cancellation_negative",):
            if k in scores:
                scores[k] = 0.92
    if "online" in review.text.lower():
        for k in ("online_booking_negative",):
            if k in scores:
                scores[k] = 0.88
    return scores


def postprocess_scores(scores: Dict[str, float], topk: int = TOPK) -> List[str]:
    """
    Constraints:
      - At most one of {neg,pos} per department.
      - Keep labels >= per-label threshold.
      - Cap total selections to topk (default 3) by score.
    """
    selected: List[tuple[str, float]] = []
    for _, (neg, pos) in DEPT_PAIRS.items():
        s_neg = scores.get(neg, 0.0)
        s_pos = scores.get(pos, 0.0)
        pass_neg = s_neg >= THRESH.get(neg, 0.5)
        pass_pos = s_pos >= THRESH.get(pos, 0.5)
        if pass_neg and pass_pos:
            chosen = neg if s_neg >= s_pos else pos
            selected.append((chosen, scores[chosen]))
        elif pass_neg:
            selected.append((neg, s_neg))
        elif pass_pos:
            selected.append((pos, s_pos))
    selected.sort(key=lambda x: x[1], reverse=True)
    return [lbl for lbl, _ in selected[:topk]]
