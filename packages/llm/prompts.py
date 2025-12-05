from __future__ import annotations
from pathlib import Path
from typing import Dict
import json
from models.labels import SENTIMENT_LABELS

CLASSIFICATION_PROMPT_TEMPLATE = """
You are a precise data labeling assistant for AIRLINE PASSENGER FEEDBACK.
Use ONLY the labels from the provided list. Follow instructions STRICTLY.
Do NOT add any extra text beyond the requested JSON output.

Review (original text):
{review}

ALLOWED LABELS (exact strings + explanations + priority explanations)
---------------------------------------------------------------------
{labels_block}


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
- Analyze the tone and assign "POSITIVE", "NEGATIVE", or "NEUTRAL".
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

SUMMARIZATION_PROMPT_TEMPLATE = """
You are an expert summarizer for the {department} department of an airline.
Your goal is to summarize the following customer reviews for the purpose of: {purpose}.

IMPORTANT:
- Do NOT include specific flight numbers or PNRs in the summary text.
- Focus on the issues, feedback, and sentiment.

Here are some examples of how to summarize for your department:
{examples_block}

Now, summarize the following reviews:
{reviews_block}

Summary:
""".strip()

DEPARTMENT_EXAMPLES = {
    "BMCOGM": """
Example 1:
Reviews:
- "My suitcase arrived with a broken handle and a large crack on the side after flight TK1983."
- "I waited for over 2 hours at the carousel in Istanbul, and my bag never showed up. The staff had no information."
- "My luggage was completely soaked when I retrieved it, ruining my clothes inside."
Summary:
Passengers reported severe issues with baggage handling, including damaged luggage (broken handles, cracks, water damage) and significant delays in baggage delivery at Istanbul, with a lack of information from staff regarding lost items.

Example 2:
Reviews:
- "Baggage delivery was surprisingly fast today, got my bags in 15 minutes."
- "No issues with my luggage, everything arrived safe and sound."
Summary:
Passengers reported a positive experience with efficient and safe baggage delivery.
""",
    "IUIB": """
Example 1:
Reviews:
- "The pasta served on the flight was cold and tasteless. Very disappointed with the meal quality."
- "The in-flight entertainment system at seat 12A was frozen for the entire 8-hour flight."
- "They ran out of the vegetarian option before reaching row 20."
Summary:
Passengers expressed dissatisfaction with the in-flight product, specifically citing poor food quality (cold, tasteless), insufficient stock of special meals (vegetarian), and malfunctioning in-flight entertainment systems.

Example 2:
Reviews:
- "The new movie selection is fantastic, kept me entertained the whole way."
- "The breakfast was delicious, fresh fruit and hot coffee were perfect."
Summary:
Passengers praised the in-flight entertainment content and the quality of the breakfast service.
""",
    "TGS": """
Example 1:
Reviews:
- "The check-in line was moving extremely slowly, only two counters were open for economy class."
- "Boarding was a mess, there was no zone enforcement and people were pushing."
- "Ground staff at the gate were rude when I asked about the delay."
Summary:
Passengers reported operational inefficiencies and poor service from ground staff, highlighting long wait times at check-in, chaotic boarding processes due to lack of zone enforcement, and unprofessional behavior from gate agents.

Example 2:
Reviews:
- "Check-in was a breeze with the self-service kiosks."
- "Boarding started on time and was very organized."
Summary:
Passengers reported a smooth and efficient ground experience, praising the self-service check-in options and organized boarding process.
""",
    "KHB": """
Example 1:
Reviews:
- "The tray table was sticky and had coffee stains from the previous flight."
- "The lavatory was in a terrible state, no paper towels and very dirty."
- "There was trash in the seat pocket when I boarded."
Summary:
Passengers raised serious concerns about cabin cleanliness, reporting dirty tray tables, uncleaned seat pockets, and poor hygiene in the lavatories.

Example 2:
Reviews:
- "The cabin was spotless when we boarded."
- "Toilets were kept clean throughout the long flight."
Summary:
Passengers complimented the high standards of cabin cleanliness and hygiene maintenance during the flight.
""",
    "RVBCM": """
Example 1:
Reviews:
- "I tried to change my flight online but the system kept crashing."
- "The ticket price was very high for such a short flight."
Summary:
Passengers reported technical issues with the online booking system and dissatisfaction with ticket pricing.
""",
    "CMYM": """
Example 1:
Reviews:
- "I called customer service and waited on hold for 45 minutes."
- "The agent was helpful but couldn't resolve my issue."
Summary:
Passengers reported long wait times for customer service, though some agents were helpful.
""",
    "GYB": """
Example 1:
Reviews:
- "The loyalty points I earned were not credited to my account."
- "I didn't receive the discount I was promised."
Summary:
Passengers reported issues with loyalty program credits and missing discounts.
""",
    "default": """
Example 1:
Reviews:
- "The service was generally poor and the flight was delayed by 3 hours."
- "Not the standard I expect from this airline."
Summary:
Passengers reported general dissatisfaction with the service standards and significant flight delays.
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
