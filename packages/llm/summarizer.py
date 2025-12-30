from __future__ import annotations
from typing import List
import logging
import json
from pathlib import Path

from packages.llm.client import LLMClient
from packages.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)

def _load_agents_llm_config() -> dict:
    config_path = Path("models/artifacts/llm_config_agents.json")
    if not config_path.exists():
        raise FileNotFoundError(f"LLM agents config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))








class Summarizer:
    """
    Summarizes customer reviews using LLM with in-context learning.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        if llm_client is not None:
            self.llm_client = llm_client
        else:
            cfg = _load_agents_llm_config()
            self.llm_client = LLMClient(
                provider=cfg.get("provider", "openai"),
                model=(cfg.get("models") or {}).get("openai"),
                max_tokens=cfg.get("max_tokens"),
                system_prompt=cfg.get("system_prompt"),
            )
        self.prompt_builder = PromptBuilder()

    def summarize(self, reviews: List[str], department: str, purpose: str) -> str:
        """
        Summarize a list of reviews for a specific department and purpose.
        
        Args:
            reviews: List of review texts to summarize.
            department: The department context (e.g., 'baggage', 'inflight_experience').
            purpose: The purpose of the summary (e.g., 'create jira task', 'email report').
            
        Returns:
            The generated summary string.
        """
        if not reviews:
            return "No reviews to summarize."

        prompt = self.prompt_builder.build_summarization_messages(reviews, department, purpose)
        
        try:
            return self.llm_client.complete(prompt, json_mode=False)
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Failed to generate summary."
