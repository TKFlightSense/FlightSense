from __future__ import annotations
from pathlib import Path
from typing import Dict
import json
from FlightSense.models.labels import SENTIMENT_LABELS

CLASSIFICATION_PROMPT_TEMPLATE = """
You are a precise data labeling assistant for AIRLINE PASSENGER FEEDBACK.
Use ONLY the labels from the provided list. Follow instructions STRICTLY.
Do NOT add any extra text beyond the requested JSON output.

Review (original text):
{review}

ALLOWED LABELS (exact strings + explanations + priority explanations)
---------------------------------------------------------------------
{labels_block}

SENTIMENT LABELS (positive or neutral or negative)
---------------------------------------
{sentiment_labels_block}

TASK
----
Analyze the review and provide segmentation with classification.

For each segment:
1. Identify CONTIGUOUS text spans that clearly express one of the topics
2. Assign EXACTLY ONE label from the list ABOVE to each segment
3. Assign priority to each segment according to priority explanations of the label in the above list
4. Do POSITIVE/NEUTRAL/NEGATIVE analysis for the segment
5. Provide character-level position (start index and length)

Segmentation rules:
- Use 0-based character indexes into the ORIGINAL review string
- Each segment: {{"start": int, "length": int, "label": "label_name", "priority": "priority_level", "sentiment": "label_sentiment"}}
- Segments MUST NOT overlap
- Only segment text that clearly relates to a label
- If a sentence has multiple issues, create separate segments for each
- Keep segments concise while capturing the complete thought
- Return AT MOST {max_segments} segments
- If nothing fits any label, return empty segments list

Labeling rules:
- Use ONLY the exact label strings provided (no variations, no typos)
- Choose the MOST specific label that fits the text
- Do NOT force labels - empty segments list is valid
- If multiple labels could apply, choose the ONE that best reflects the main focus

Priority assignment rules:
- Assign only the appropriate priority according to the specific "PRIORITY" instructions found within the label definition.
- DO NOT assign priorities different than LOW, MEDIUM, HIGH
- DO NOT assign HIGH frequently, pay attention to the priority explanations in the label.
- If a situation falls between categories, default to the LOWER priority (e.g., if unclear between LOW and MEDIUM, choose LOW).

Sentiment analysis rules:
- CHECK if the segment's label is in the provided SENTIMENT LABELS list.
- IF label is NOT in the list: Set sentiment to "NONE".
- IF label IS in the list: Analyze the tone and assign "POSITIVE", "NEGATIVE", or "NEUTRAL".
    - Use "NEUTRAL" for purely factual descriptions (e.g., "Dinner was served at 6pm") or ambivalent statements.
    - Use "NEGATIVE" for complaints, sarcasm, or dissatisfaction.
    - Use "POSITIVE" for praise, gratitude, or satisfaction.

OUTPUT FORMAT (JSON ONLY)
-------------------------
Return ONLY valid JSON with this exact structure:

{{
  "segments": [
    {{"start": int, "length": int, "label": "<one_of_the_allowed_labels>", "priority": "<LOW, MEDIUM, OR HIGH>", "sentiment": "<POSITIVE, NEGATIVE, NEUTRAL, or NONE>"}},
    ...
  ]
}}

Do NOT include explanations, comments, or any extra fields.
Return ONLY the JSON object.

Example of a valid output (for a different review):
{{"segments": [{{"start": 0, "length": 42, "label": "baggage_lost", "priority": "HIGH", "sentiment": "NONE"}}]}}
""".strip()


class PromptBuilder:
    """
    Builds prompts for segmenting and labeling airline feedback
    using the label definitions in models/artifacts/label_map.json.
    """

    def __init__(self, label_map_path: Path | None = None) -> None:
        if label_map_path is None:
            label_map_path = Path("models/artifacts/label_map.json")
        self.label_map_path = label_map_path
        self.labels: Dict[str, str] = self._load_labels()

    def _load_labels(self) -> Dict[str, str]:
        if not self.label_map_path.exists():
            raise FileNotFoundError(f"Label map not found: {self.label_map_path}")
        with self.label_map_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_labels_block(self) -> str:
        """
        Renders the 'ALLOWED LABELS' section from label_map.json,
        like:
        - inflight_experience_food_beverage:
          <description>
        """
        lines = []
        for label, desc in self.labels.items():
            lines.append(f"- {label}:")
            lines.append(f"  {desc}")
            lines.append("")  # blank line between labels
            #priority ekle
        return "\n".join(lines).strip()

    def _build_sentiment_labels_block(self) -> str:
        """
        Renders the 'SENTIMENT LABELS' section from labels.py
        """
        return "\n".join(SENTIMENT_LABELS).strip()

    def build_classification_messages(self, review: str, max_segments: int = 3) -> str:
        """Build prompt for classification with labeled segments."""
        labels_block = self._build_labels_block()
        sentiment_labels_block = self._build_sentiment_labels_block()
        return CLASSIFICATION_PROMPT_TEMPLATE.format(
            review=review,
            labels_block=labels_block,
            sentiment_labels_block=sentiment_labels_block,
            max_segments=max_segments,
        )
