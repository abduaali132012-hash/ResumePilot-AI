"""Resilient Gemini client wrapper used by every agent in the pipeline.

Design goals
------------
1. **One source of truth for the API key.** Reads `GOOGLE_API_KEY` (or
   `GEMINI_API_KEY`) from `st.secrets` when running inside Streamlit, and from
   the environment otherwise (used by the CLI evaluation suite). Never hardcoded.
2. **Retry on transient failures.** Mirrors the retry logic in the main app:
   brief rate-limits / network hiccups are retried, but daily quota exhaustion
   (HTTP 429 with a per-day message) is NOT retried — a short delay cannot
   fix a limit that only resets once a day.
3. **JSON-safe generation.** All agents exchange structured data with the model
   as JSON; `generate_json` strips markdown fences and parses reliably.
4. **Graceful degradation.** If no key is configured (or every call fails), the
   caller can fall back to the deterministic heuristic evaluator instead of
   crashing.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional


def _default_model() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _secrets_file_key() -> Optional[str]:
    """Read the key from `.streamlit/secrets.toml` (the repo's git-ignored
    Streamlit secrets file) so the CLI evaluation harness and the Streamlit app
    share the same configured location."""
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:  # pragma: no cover - py3.10 fallback
        try:
            import tomli as tomllib  # type: ignore
        except ModuleNotFoundError:
            return None
    root = Path(__file__).resolve().parents[2]  # repo root
    secrets_file = root / ".streamlit" / "secrets.toml"
    try:
        with secrets_file.open("rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return None
    return data.get("GOOGLE_API_KEY") or data.get("GEMINI_API_KEY")


def get_api_key() -> Optional[str]:
    """Return the configured Gemini API key from secrets or environment."""
    # Inside Streamlit, st.secrets is the canonical place for keys.
    try:
        import streamlit as st  # type: ignore

        if hasattr(st, "secrets") and st.secrets:
            key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
            if key:
                return key
    except Exception:
        pass  # not running inside Streamlit (e.g. CLI evaluation run)

    # Outside Streamlit (evaluation suite, notebooks, tests).
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    return _secrets_file_key()


def is_daily_quota_exhausted(error_text: str) -> bool:
    """True if this is the per-day quota limit (not worth retrying)."""
    text = error_text.lower().replace(" ", "")
    return "429" in error_text and (
        "quotaexceeded" in text
        or "perday" in text
        or "resource_exhausted" in text.replace("_", "").lower()
    )


class GeminiClient:
    """Thin wrapper around the google-genai client with retry + JSON helpers."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or _default_model()
        self.api_key = get_api_key()
        self.client = None
        if self.api_key:
            from google import genai

            self.client = genai.Client(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self.client is not None and bool(self.api_key)

    def generate(
        self,
        prompt: str,
        max_attempts: int = 3,
        delay_seconds: float = 2.0,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate text, retrying transient failures. Raises on final failure."""
        if not self.available:
            raise RuntimeError(
                "Gemini client is not available. Add GOOGLE_API_KEY / GEMINI_API_KEY "
                "to .streamlit/secrets.toml (app) or the environment (CLI)."
            )
        last_error: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            try:
                kwargs: dict[str, Any] = {"model": self.model, "contents": prompt}
                if temperature is not None:
                    kwargs["config"] = {"temperature": temperature}
                response = self.client.models.generate_content(**kwargs)
                return response.text or ""
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if is_daily_quota_exhausted(str(exc)):
                    break  # daily quota — retrying just wastes what's left
                if attempt < max_attempts:
                    time.sleep(delay_seconds)
        raise last_error  # type: ignore[misc]

    def generate_json(
        self,
        prompt: str,
        max_attempts: int = 3,
        delay_seconds: float = 2.0,
    ) -> Any:
        """Generate text and parse it as JSON. Raises on failure."""
        text = self.generate(prompt, max_attempts=max_attempts, delay_seconds=delay_seconds)
        return parse_json(text)


def parse_json(text: str) -> Any:
    """Parse model output as JSON, tolerating ```json fences and stray prose."""
    text = text.strip()
    # Strip a single fenced block if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    if fence:
        text = fence.group(1).strip()
    # If the model wrapped the array/object in prose, cut to the first '[' or '{'.
    start = min([i for i in (text.find("["), text.find("{")) if i != -1] or [-1])
    if start > 0:
        text = text[start:]
    return json.loads(text)
