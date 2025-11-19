from __future__ import annotations
from pathlib import Path
from typing import Dict
import json


SEGMENTATION_PROMPT_TEMPLATE = """
You are a precise data segmenting and labeling assistant for AIRLINE PASSENGER FEEDBACK.
Use ONLY the labels from the provided list. Follow instructions STRICTLY.
Do NOT add any extra text beyond the requested JSON output.

Review (original text):
{review}

ALLOWED LABELS (exact strings + explanations)
---------------------------------------------
{labels_block}

TASK
----
Split the review into 0 or more CONTIGUOUS segments and assign EXACTLY ONE label from the list ABOVE to EACH segment that clearly expresses that topic.

Segmentation rules:
- Use 0-based character indexes into the ORIGINAL review string (the exact text shown above).
- Each segment is defined by:
  - "start": the index of the FIRST character of the segment.
  - "length": the NUMBER of characters in the segment.
- Segments MUST NOT overlap.
- Segments should only cover parts of the text that clearly relate to one of the labels.
- If a sentence talks about multiple different issues (e.g., baggage and cabin service), create separate segments for the parts that relate to each label.
- Keep segments as short as possible while still clearly matching their label.
- Return AT MOST {max_segments} segments.
- If NO part of the review fits any label, return an empty list: {{"segments": []}}.

Labeling rules:
- Use ONLY these label strings (no new labels, no typos).
- Choose the MOST specific label that fits the text.
- Do NOT force a label when nothing fits; it is valid to return {{"segments": []}}.
- If multiple labels could apply, choose the ONE that best reflects the main focus of that text span.

OUTPUT FORMAT (JSON ONLY)
-------------------------
Return ONLY valid JSON with this exact structure:

{{
  "segments": [
    {{"start": int, "length": int, "label": "<one_of_the_allowed_labels>"}},
    ...
  ]
}}

Do NOT include explanations, comments, or any extra fields.
Return ONLY the JSON object.

Example of a valid output (for a different review):
{{"segments": [{{"start": 0, "length": 42, "label": "baggage_lost"}}]}}
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
        return "\n".join(lines).strip()

    def build_segmentation_prompt(self, review: str, max_segments: int = 3) -> str:
        labels_block = self._build_labels_block()
        return SEGMENTATION_PROMPT_TEMPLATE.format(
            review=review,
            labels_block=labels_block,
            max_segments=max_segments,
        )
