import json
from typing import Any, Dict
from packages.llm.prompts import PromptBuilder
from packages.llm.client import LLMClient


class SegmentationService:
    def __init__(self, llm_client: LLMClient | None = None):
        self.prompt_builder = PromptBuilder()
        self.llm_client = llm_client or LLMClient()

    def segment_review(self, review: str, max_segments: int = 3) -> Dict[str, Any]:
        prompt = self.prompt_builder.build_segmentation_prompt(
            review=review,
            max_segments=max_segments,
        )
        raw = self.llm_client.complete(prompt)
        # you can keep it as str and validate/parse elsewhere if you prefer
        return json.loads(raw)
