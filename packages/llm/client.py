from __future__ import annotations
from typing import List, Dict, Optional, Literal, Any
from pathlib import Path
import os
import json
import logging
import random
import time

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
        system_prompt: Optional[str] = None,
    ):
        self.provider = provider or os.getenv("LLM_PROVIDER") or _LLM_CONFIG["provider"]
        self.temperature = (
            temperature
            if temperature is not None
            else _LLM_CONFIG.get("temperature")  # may be None
        )
        self.max_tokens = max_tokens if max_tokens is not None else _LLM_CONFIG["max_tokens"]
        self.system_prompt = system_prompt if system_prompt is not None else _LLM_CONFIG["system_prompt"]
        
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
        api_key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
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

    def complete(self, prompt: str, *, json_mode: bool = True) -> str:
        """
        Takes the full prompt string and returns the model's response as raw text.
        
        Args:
            prompt: The prompt text to send to the model
            
        Returns:
            The model's response as a string
        """
        if self.provider == "openai":
            return self._complete_openai(prompt, json_mode=json_mode)
        elif self.provider == "vllm":
            return self._complete_vllm(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _extract_chat_content(self, response: Any) -> str:
        """
        Best-effort extraction of text content from Chat Completions responses.
        Returns empty string if no usable content is present.
        """
        try:
            choice = response.choices[0]
            msg = choice.message
        except Exception:
            return ""

        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content

        # Some SDKs/models may return content as a list of parts; try to extract text.
        if isinstance(content, list):
            parts: List[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    text = part.get("text") or part.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                else:
                    text = getattr(part, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
            return "".join(parts)

        # If the model refused, some SDKs expose msg.refusal.
        refusal = getattr(msg, "refusal", None)
        if isinstance(refusal, str) and refusal.strip():
            logger.warning("OpenAI refusal: %s", refusal[:200])
            return ""

        # If the model produced tool calls, content may be None.
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            try:
                # Sometimes the "arguments" field contains the JSON we want.
                for tc in tool_calls:
                    fn = getattr(tc, "function", None)
                    args = getattr(fn, "arguments", None) if fn is not None else None
                    if isinstance(args, str) and args.strip():
                        return args
            except Exception:
                pass

        return ""

    def _call_openai_chat(self, prompt: str, *, json_mode: bool, token_param: str) -> str:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            token_param: self.max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        response = self.client.chat.completions.create(**kwargs)
        text = self._extract_chat_content(response)
        return text.strip() if isinstance(text, str) else ""

    def _call_openai_responses(self, prompt: str, *, json_mode: bool) -> str:
        """
        Fallback for newer models/SDKs where chat.completions may not return content.

        We rely on the system prompt + prompt instructions to enforce JSON output.
        """
        if not hasattr(self.client, "responses"):
            raise RuntimeError("OpenAI Responses API not available in this SDK")

        # Prefer the simplest, most compatible Responses API shape:
        # - `instructions` carries system prompt
        # - `input` carries user prompt text
        #
        # NOTE: Some reasoning-heavy models (e.g., gpt-5*) may consume the entire
        # output budget on internal reasoning if max_output_tokens is large.
        # We cap output tokens and lower reasoning effort by default to ensure
        # we actually get a JSON answer back.
        reasoning_effort = os.getenv("LLM_REASONING_EFFORT", "low").strip().lower() or "low"
        max_out = self.max_tokens
        if self._is_responses_preferred_model():
            cap_raw = (os.getenv("LLM_GPT5_MAX_OUTPUT_TOKENS") or "").strip()
            if cap_raw:
                try:
                    cap = int(cap_raw)
                    max_out = min(max_out, cap)
                except ValueError:
                    logger.warning("Invalid LLM_GPT5_MAX_OUTPUT_TOKENS=%r; ignoring.", cap_raw)

        common_kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_output_tokens": max_out,
        }
        if self._is_responses_preferred_model():
            common_kwargs["reasoning"] = {"effort": reasoning_effort}
        # Some models (notably gpt-5*) reject temperature; avoid passing it there.
        if self.temperature is not None and not self._is_responses_preferred_model():
            common_kwargs["temperature"] = self.temperature
        if json_mode:
            # Supported by the Responses API (unlike chat.completions' response_format kwarg).
            common_kwargs["text"] = {"format": {"type": "json_object"}}

        # Some SDK versions may not accept `instructions`; we fall back below.
        try:
            resp = self.client.responses.create(
                instructions=self.system_prompt,
                input=prompt,
                **common_kwargs,
            )
        except TypeError:
            # Fallback for older SDKs: inline system prompt into the input.
            resp = self.client.responses.create(
                input=f"{self.system_prompt}\n\n{prompt}",
                **common_kwargs,
            )

        output_text = getattr(resp, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        def extract_from_dump(obj: Any) -> str:
            """
            Extract concatenated text from a Responses API payload in a way that
            tolerates different SDK return shapes (objects vs dicts).
            """
            if obj is None:
                return ""

            # Convert SDK object -> dict when possible.
            if not isinstance(obj, (dict, list)):
                if hasattr(obj, "model_dump"):
                    try:
                        obj = obj.model_dump()
                    except Exception:
                        pass
                elif hasattr(obj, "dict"):
                    try:
                        obj = obj.dict()
                    except Exception:
                        pass

            if isinstance(obj, dict):
                ot = obj.get("output_text")
                if isinstance(ot, str) and ot.strip():
                    return ot.strip()

                # Common: obj["output"][...]["content"][...]["text"]
                output = obj.get("output")
                if isinstance(output, list):
                    parts: List[str] = []
                    for item in output:
                        if not isinstance(item, dict):
                            continue
                        content = item.get("content")
                        if not isinstance(content, list):
                            continue
                        for c in content:
                            if isinstance(c, dict):
                                text = c.get("text")
                                if isinstance(text, str):
                                    parts.append(text)
                                elif isinstance(text, dict):
                                    v = text.get("value")
                                    if isinstance(v, str):
                                        parts.append(v)
                    joined = "".join(parts).strip()
                    if joined:
                        return joined

                # Fallback: walk the object and collect any "text" strings.
                parts: List[str] = []

                def walk(node: Any, depth: int = 0) -> None:
                    if depth > 12:
                        return
                    if isinstance(node, dict):
                        t = node.get("text")
                        if isinstance(t, str):
                            parts.append(t)
                        elif isinstance(t, dict):
                            v = t.get("value")
                            if isinstance(v, str):
                                parts.append(v)
                        for v in node.values():
                            walk(v, depth + 1)
                    elif isinstance(node, list):
                        for v in node:
                            walk(v, depth + 1)

                walk(obj)
                joined = "".join(parts).strip()
                return joined

            if isinstance(obj, list):
                # Rare: treat as output list
                parts: List[str] = []
                for v in obj:
                    s = extract_from_dump(v)
                    if s:
                        parts.append(s)
                return "".join(parts).strip()

            return ""

        extracted = extract_from_dump(resp)
        if extracted:
            return extracted

        return ""

    def _is_responses_preferred_model(self) -> bool:
        """
        Heuristic: some newer model families are primarily intended for the Responses API.
        Using chat.completions with these can return 400s or empty content.
        """
        model = (self.model or "").lower()
        return model.startswith(("gpt-5", "o1", "o3", "o4"))

    def _attempt_openai_completion(self, prompt: str, *, json_mode: bool) -> str:
        """
        Try a small set of compatible OpenAI request variants.
        Returns empty string if all variants produce empty content.
        """
        # 0) Prefer Responses API for certain models (avoids chat.completions 400/empty).
        if self._is_responses_preferred_model():
            try:
                text = self._call_openai_responses(prompt, json_mode=json_mode)
                return text
            except Exception as e:
                logger.debug("responses.create preferred-path failed: %s", e)
                return ""

        json_modes_to_try = (json_mode, not json_mode)

        # 1) chat.completions + JSON mode + max_completion_tokens
        for jm in json_modes_to_try:
            try:
                text = self._call_openai_chat(
                    prompt, json_mode=jm, token_param="max_completion_tokens"
                )
                if text:
                    return text
            except Exception as e:
                logger.debug(
                    "chat.completions failed (max_completion_tokens, json_mode=%s): %s",
                    jm,
                    e,
                )

        # 2) Compatibility: some models/SDKs use max_tokens instead
        for jm in json_modes_to_try:
            try:
                text = self._call_openai_chat(
                    prompt, json_mode=jm, token_param="max_tokens"
                )
                if text:
                    return text
            except Exception as e:
                logger.debug(
                    "chat.completions failed (max_tokens, json_mode=%s): %s",
                    jm,
                    e,
                )

        # 3) Fallback: Responses API
        try:
            text = self._call_openai_responses(prompt, json_mode=json_mode)
            if text:
                return text
        except Exception as e:
            logger.debug("responses.create fallback failed: %s", e)

        return ""

    def _complete_openai(self, prompt: str, json_mode: bool = True) -> str:
        """Complete using OpenAI API (with retries + fallbacks on empty output)."""
        max_attempts = int(os.getenv("LLM_EMPTY_RETRY_ATTEMPTS", "2"))
        last_err: Optional[Exception] = None

        for attempt in range(1, max_attempts + 1):
            try:
                text = self._attempt_openai_completion(prompt, json_mode=json_mode)
                if text:
                    return text

                logger.warning(
                    "OpenAI returned empty output (attempt %d/%d, model=%s).",
                    attempt,
                    max_attempts,
                    self.model,
                )

            except Exception as e:
                last_err = e
                logger.warning(
                    "OpenAI call failed (attempt %d/%d, model=%s): %s",
                    attempt,
                    max_attempts,
                    self.model,
                    e,
                )

            # small backoff to reduce rapid-fire retries
            if attempt < max_attempts:
                time.sleep(min(2.0, 0.25 * (2 ** (attempt - 1)) + random.random() * 0.25))

        if last_err is not None:
            logger.error("OpenAI API error after retries: %s", last_err)
            raise last_err

        return ""

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
