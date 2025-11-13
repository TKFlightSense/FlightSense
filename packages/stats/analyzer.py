# core/analyzer.py

import json
import os
import re
from collections import defaultdict
from typing import Dict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

JSON_PATH = os.path.join(PROJECT_ROOT, "models", "artifacts", "subtopics.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    SUBTOPICS = json.load(f)

def _keyword_hit(text: str, keywords):
    """Return True if any keyword matches the text."""
    return any(re.search(rf"\b{kw}\b", text) for kw in keywords)


def _process_label(text, sentiments, label, subtopics, results, only_negative=False):
    """
    Generic handler for each label.
    - text: review text (lowercased)
    - sentiments: dict of label → -1/0/1
    - label: "inflight_experience" etc.
    - subtopics: SUBTOPICS[label]
        Supports both formats:
        1. {"food_beverage": {"neutral": [...], "negative": [...]}}
        2. {"delayed": ["delay", "late", ...]}
    - results: defaultdict
    - only_negative: if True → only process when sentiment == -1
    """

    sentiment_value = sentiments.get(label, 0)

    # Skip if not relevant
    if only_negative and sentiment_value != -1:
        return
    if not only_negative and sentiment_value == 0:
        return

    matched = set()

    for subtopic, terms in subtopics.items():
        if isinstance(terms, dict):
            all_keywords = []
            for key in ["neutral", "positive", "negative"]:
                all_keywords.extend(terms.get(key, []))

        elif isinstance(terms, list):
            all_keywords = terms

        else:
            continue

        if _keyword_hit(text, all_keywords):
            results[label][subtopic]["count"] += 1
            matched.add(subtopic)

    if not matched:
        results[label]["others"]["count"] += 1


def analyze_review(text: str, sentiments: Dict[str, int]):
    """
    Analyze text according to label sentiments and subtopic rules.
    """
    text_lower = text.lower()
    results = defaultdict(lambda: defaultdict(lambda: {"count": 0}))

    LABEL_RULES = {
        "inflight_experience": {"only_negative": True},
        "checkin_boarding_process": {"only_negative": True},
        "flight_delay_cancellation": {"only_negative": False},
        "baggage_issues": {"only_negative": False},
        "pricing_fees": {"only_negative": False},
        "online_booking": {"only_negative": False},
    }

    for label, config in LABEL_RULES.items():
        _process_label(
            text=text_lower,
            sentiments=sentiments,
            label=label,
            subtopics=SUBTOPICS[label],
            results=results,
            only_negative=config["only_negative"]
        )

    return results
