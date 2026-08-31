"""Inference layer: resilient Gemini client wrapper.

Re-exports the client, key resolution, quota guard, and JSON helpers from the
package, so both `from ai.inference import GeminiClient` and
`from ai.inference.gemini_client import GeminiClient` work.
"""
from ai.inference import (
    GeminiClient,
    get_api_key,
    is_daily_quota_exhausted,
    parse_json,
)

__all__ = ["GeminiClient", "get_api_key", "is_daily_quota_exhausted", "parse_json"]
