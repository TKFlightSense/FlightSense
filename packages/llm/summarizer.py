from __future__ import annotations
from typing import List
import logging

from packages.llm.client import LLMClient
from packages.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)








class Summarizer:
    """
    Summarizes customer reviews using LLM with in-context learning.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()
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
            return self.llm_client.complete(prompt)
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Failed to generate summary."