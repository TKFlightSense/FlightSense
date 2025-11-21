from __future__ import annotations
from typing import List, Dict, Optional, Literal, Any
from pathlib import Path
import os
import json
import logging

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from vllm import LLM, SamplingParams
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False

logger = logging.getLogger(__name__)

LLMProvider = Literal["openai", "vllm"]


def _load_llm_config() -> Dict[str, Any]:
    """Load LLM configuration from JSON file."""
    config_path = Path("models/artifacts/llm_config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"LLM config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load configuration from JSON file
_LLM_CONFIG = _load_llm_config()


class LLMClient:
    """
    Unified LLM client supporting both OpenAI and vLLM backends.
    
    Environment variables:
        - OPENAI_API_KEY: API key for OpenAI
        - OPENAI_BASE_URL: Optional custom base URL for OpenAI-compatible APIs
        - LLM_PROVIDER: "openai" or "vllm" (default: "openai")
        - LLM_MODEL: Model name/path
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.provider = provider or os.getenv("LLM_PROVIDER") or _LLM_CONFIG["provider"]
        self.temperature = temperature if temperature is not None else _LLM_CONFIG["temperature"]
        self.max_tokens = max_tokens if max_tokens is not None else _LLM_CONFIG["max_tokens"]
        self.system_prompt = _LLM_CONFIG["system_prompt"]
        
        if self.provider == "openai":
            self._init_openai(model, api_key, base_url)
        elif self.provider == "vllm":
            self._init_vllm(model)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _init_openai(self, model: Optional[str], api_key: Optional[str], base_url: Optional[str]):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )
        
        self.model = model or os.getenv("LLM_MODEL") or _LLM_CONFIG["models"]["openai"]
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Get base URL (optional, for OpenAI-compatible APIs)
        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"Initialized OpenAI client with custom base URL: {base_url}")
        else:
            self.client = OpenAI(api_key=api_key)
            logger.info("Initialized OpenAI client")
        
        logger.info(f"Using OpenAI model: {self.model}")

    def _init_vllm(self, model: Optional[str]):
        """Initialize vLLM client for local model inference."""
        if not VLLM_AVAILABLE:
            raise ImportError(
                "vLLM library not installed. Install with: pip install vllm"
            )
        
        self.model = model or os.getenv("LLM_MODEL") or _LLM_CONFIG["models"]["vllm"]
        
        logger.info(f"Initializing vLLM with model: {self.model}")
        self.client = LLM(model=self.model)
        self.sampling_params = SamplingParams(
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=0.95,
        )
        logger.info("vLLM client initialized")

    def complete(self, prompt: str) -> str:
        """
        Takes the full prompt string and returns the model's response as raw text.
        
        Args:
            prompt: The prompt text to send to the model
            
        Returns:
            The model's response as a string
        """
        if self.provider == "openai":
            return self._complete_openai(prompt)
        elif self.provider == "vllm":
            return self._complete_vllm(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _complete_openai(self, prompt: str) -> str:
        """Complete using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _complete_vllm(self, prompt: str) -> str:
        """Complete using vLLM local inference."""
        try:
            # Format prompt for chat models
            formatted_prompt = (
                f"<|system|>\n{self.system_prompt}\n"
                f"<|user|>\n{prompt}\n<|assistant|>\n"
            )
            
            outputs = self.client.generate([formatted_prompt], self.sampling_params)
            return outputs[0].outputs[0].text.strip()
        except Exception as e:
            logger.error(f"vLLM error: {e}")
            raise
