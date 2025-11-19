from __future__ import annotations
from typing import List, Dict
# from openai import OpenAI

class LLMClient:
    # def __init__(self, model: str = "gpt-4.1-mini"):
    #     self.client = OpenAI()
    #     self.model = model

    def complete(self, prompt: str) -> str:
        """
        Takes the full prompt string and returns the model's response as raw text.
        """
        # Example with a chat-style API (pseudo-code):
        #
        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {"role": "system", "content": "You are a precise labeling assistant."},
        #         {"role": "user", "content": prompt},
        #     ],
        #     temperature=0.0,
        # )
        # return response.choices[0].message.content.strip()
        raise NotImplementedError("Wire this to your actual LLM provider.")
