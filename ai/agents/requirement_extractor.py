"""Agent 1 — Requirement Extractor.

Turns a raw job description into a structured list of `Requirement` objects,
so that the rest of the pipeline evaluates against explicit, comparable items
instead of an unstructured blob of text.
"""
from __future__ import annotations

from typing import Any

from ai.inference import GeminiClient
from ai.models import Requirement
from ai.prompts import REQUIREMENT_EXTRACTION


class RequirementExtractor:
    def __init__(self, client: GeminiClient):
        self.client = client

    def extract(self, job_description: str) -> list[Requirement]:
        if not job_description or not job_description.strip():
            return []
        prompt = REQUIREMENT_EXTRACTION.format(job_description=job_description.strip())
        data: dict[str, Any] = self.client.generate_json(prompt)
        raw_items = data.get("requirements", []) if isinstance(data, dict) else data or []
        requirements = []
        for item in raw_items or []:
            if not isinstance(item, dict) or not item.get("text"):
                continue
            requirements.append(
                Requirement(
                    text=str(item["text"]).strip(),
                    category=str(item.get("category", "Technical")),
                    importance=item.get("importance", "required"),
                )
            )
        return requirements
