from __future__ import annotations

from pathlib import Path
from typing import Dict
import json

from models.labels import SENTIMENT_LABELS

CLASSIFICATION_PROMPT_TEMPLATE = """
You are a strict classification engine for AIRLINE PASSENGER FEEDBACK.
Follow the rules exactly and output ONLY JSON.

REVIEW (length={review_len}; indices refer to this exact string)
<<<REVIEW_START>>>
{review}
<<<REVIEW_END>>>

ALLOWED LABELS (exact strings)
{allowed_labels_json}

LABEL DEFINITIONS + PRIORITY RULES (use these for disambiguation)
{labels_block}

TASK
- Segment the review into at most {max_segments} NON-OVERLAPPING spans.
- Assign EXACTLY ONE label per span (must be one of the allowed labels).
- Assign priority and sentiment per span.

SEGMENT RULES
- Use 0-based character offsets: start >= 0, length > 0, start+length <= {review_len}
- start and length MUST be integers (no strings, no floats).
- Segments MUST be sorted by start ascending and MUST NOT overlap.
- Only segment text that clearly matches one of the allowed labels.
- If the review mentions a delay/cancellation, use "flight_delay_cancellation" (do NOT map it to check-in/boarding).
- If a sentence contains multiple labeled topics, create multiple segments.
- Prefer fewer, longer segments per topic (avoid tiny fragments).
- Each segment MUST include the explicit evidence words for its label (e.g., \"delayed\", \"food\", \"dirty\", \"expensive\"). Do NOT select spans that exclude the evidence.

PRIORITY
- Use ONLY: LOW, MEDIUM, HIGH
- Follow the PRIORITY guidance inside each label definition.
- If uncertain, choose the LOWER priority.

SENTIMENT
- Use ONLY: POSITIVE, NEGATIVE, NEUTRAL, NONE
- POSITIVE: praise/satisfaction about the segment topic
- NEGATIVE: complaint/dissatisfaction about the segment topic
- NEUTRAL: factual/mixed/ambiguous about the segment topic
- NONE: only if sentiment truly cannot be inferred (rare)

SEGMENT LIMIT
- If more than {max_segments} segments are possible, keep the most severe/actionable:
  HIGH > MEDIUM > LOW, then NEGATIVE > NEUTRAL > POSITIVE.

OUTPUT FORMAT (JSON ONLY)
-------------------------
Return ONLY valid JSON with this exact structure and no other keys:
{{
  "segments": [
    {{"start": int, "length": int, "label": "<one_of_the_allowed_labels>", "priority": "<LOW, MEDIUM, OR HIGH>", "sentiment": "<POSITIVE, NEGATIVE, NEUTRAL, or NONE>"}},
    ...
  ]
}}
If nothing clearly matches any label, return: {"segments": []}
""".strip()

SUMMARIZATION_PROMPT_TEMPLATE = """
You are an expert summarizer for the {department} department of an airline.
Your goal is to summarize the following customer reviews for the purpose of: {purpose}.

CRITICAL OUTPUT RULES:
- Output ONLY plain text. Do NOT output JSON, code blocks, or structured data.
- Do NOT include specific flight numbers or PNRs in the summary.
- Keep the summary concise (2-4 sentences max).
- Focus on: what happened, severity, and recommended action.
- Write in professional third-person tone (e.g., "Passenger reported...")

Here are examples of correct summaries for your department:
{examples_block}

Now, summarize the following reviews:
{reviews_block}

Summary (plain text only, no JSON):
""".strip()

DEPARTMENT_EXAMPLES = {
    "BMCOGM": """
Example 1:
Reviews:
- "My checked bag containing my heart medication has been missing for 48 hours. This is life-threatening."
- "You completely destroyed my custom wheelchair. I am stranded at the airport without mobility."
- "My suitcase arrived open with all valuables, including a laptop and jewelry, stolen."
Summary:
Passengers reported critical baggage incidents involving lost life-sustaining medication, destruction of essential mobility aids (wheelchair), and theft of high-value items from checked luggage.

Example 2:
Reviews:
- "Baggage claim was chaos, waited 3 hours."
- "Bag handle broken."
Summary:
Passengers reported significant delays and minor damage to luggage.
""",
    "IUIUB": """
Example 1:
Reviews:
- "I found a sharp piece of glass in my pasta meal. I almost swallowed it."
- "The seat 4A is broken and has a sharp metal edge that cut my leg."
- "Smoke started coming out of the IFE screen in row 15."
Summary:
Passengers reported severe safety hazards including foreign objects in food (glass), injury-causing seat defects, and potential fire hazards (smoking IFE screen).

Example 2:
Reviews:
- "Food was cold."
- "IFE selection is poor."
Summary:
Passengers expressed dissatisfaction with meal temperature and entertainment variety.
""",
    "TGS": """
Example 1:
Reviews:
- "The gate agent physically pushed an elderly passenger who was moving slowly."
- "My 8-year-old unaccompanied minor was left alone at the gate for 2 hours with no supervision."
- "Staff refused to let us board despite being at the gate 20 minutes before departure, causing us to miss a funeral."
Summary:
Passengers reported serious misconduct by ground staff, including physical aggression, negligence regarding unaccompanied minors, and unjust denied boarding causing severe personal distress.

Example 2:
Reviews:
- "Check-in was slow."
- "Boarding was disorganized."
Summary:
Passengers reported operational inefficiencies during check-in and boarding.
""",
    "KHB": """
Example 1:
Reviews:
- "A flight attendant ignored my call for help when the passenger next to me was having a seizure."
- "The crew member in the aft galley appeared visibly intoxicated and was slurring words."
- "I was verbally abused and threatened by a purser for asking for water."
Summary:
Passengers reported critical safety and conduct violations by cabin crew, including failure to respond to medical emergencies, working under the influence, and abusive behavior.

Example 2:
Reviews:
- "Crew was not friendly."
- "Service was slow."
Summary:
Passengers reported poor service attitude and slow response times.
""",
    "RVBCM": """
Example 1:
Reviews:
- "Your system charged my credit card 5 times for the same ticket, blocking $10,000 and leaving me with no funds."
- "My confirmed booking was cancelled without notice 2 hours before the flight, leaving me stranded."
Summary:
Passengers reported severe ticketing system errors resulting in massive financial holds and unnotified cancellations causing travel disruption.
""",
    "CMYM": """
Example 1:
Reviews:
- "The agent screamed at me and used profanity when I asked to speak to a supervisor."
- "I was given incorrect visa information by your call center, resulting in my deportation upon arrival."
Summary:
Passengers reported gross misconduct by call center agents (profanity) and critical misinformation leading to legal/immigration consequences.
""",
    "GYB": """
Example 1:
Reviews:
- "I am an Elite Plus member and was denied all priority services, causing me to miss my connection."
- "100,000 miles were deducted from my account without my authorization."
Summary:
Passengers reported unauthorized loss of loyalty points and denial of entitled elite status benefits causing travel disruption.
""",
    "default": """
Example 1:
Reviews:
- "The flight was delayed 5 hours and we were given no water."
- "Staff was rude and unhelpful."
Summary:
Passengers reported significant delays with lack of basic care and poor staff behavior.
"""
}

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
            # (Priority rules are embedded in each label definition.)
        return "\n".join(lines).strip()

    def _build_sentiment_labels_block(self) -> str:
        """
        Renders the 'SENTIMENT LABELS' section from labels.py
        """
        return "\n".join(SENTIMENT_LABELS).strip()

    def _build_allowed_labels_json(self) -> str:
        """
        Render allowed labels as a JSON array string to reduce typos.

        This is intended to be copy/paste-safe for the model and keeps
        labels case-sensitive and exact.
        """
        return json.dumps(list(self.labels.keys()), ensure_ascii=False)

    def build_classification_messages(self, review: str, max_segments: int = 3) -> str:
        """Build prompt for classification with labeled segments."""
        labels_block = self._build_labels_block()
        sentiment_labels_block = self._build_sentiment_labels_block()
        allowed_labels_json = self._build_allowed_labels_json()
        return CLASSIFICATION_PROMPT_TEMPLATE.format(
            review=review,
            review_len=len(review),
            allowed_labels_json=allowed_labels_json,
            labels_block=labels_block,
            sentiment_labels_block=sentiment_labels_block,
            max_segments=max_segments,
        )

    def build_summarization_messages(self, reviews: list[str], department: str, purpose: str) -> str:
        """Build prompt for summarization with in-context learning."""
        examples_block = DEPARTMENT_EXAMPLES.get(department, DEPARTMENT_EXAMPLES["default"])
        reviews_block = "\n".join([f"- {r}" for r in reviews])
        return SUMMARIZATION_PROMPT_TEMPLATE.format(
            department=department,
            purpose=purpose,
            examples_block=examples_block,
            reviews_block=reviews_block,
        )
