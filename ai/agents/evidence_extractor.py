"""Agent 2 — Evidence Extractor.

Pulls the factual, verifiable claims out of a resume (skill + exact quote +
source section + confidence). The evaluator only ever reasons from these
quotes, which is what makes the system *evidence-based* rather than a vibe
score from a single-pass LLM.
"""
from __future__ import annotations

from typing import Any

from ai.inference import GeminiClient
from ai.models import Evidence
from ai.prompts import EVIDENCE_EXTRACTION

# Truncation guard: a resume longer than this is unlikely to add signal and
# risks blowing the model context / hitting token limits.
MAX_RESUME_CHARS = 24000


class EvidenceExtractor:
    def __init__(self, client: GeminiClient):
        self.client = client

    def extract(self, resume_text: str) -> list[Evidence]:
        if not resume_text or not resume_text.strip():
            return []
        text = resume_text.strip()[:MAX_RESUME_CHARS]
        prompt = EVIDENCE_EXTRACTION.format(resume_text=text)
        data: dict[str, Any] = self.client.generate_json(prompt)
        raw_items = data.get("evidence", []) if isinstance(data, dict) else data or []
        evidence = []
        for item in raw_items or []:
            if not isinstance(item, dict) or not item.get("skill"):
                continue
            evidence.append(
                Evidence(
                    skill=str(item["skill"]).strip(),
                    evidence=str(item.get("evidence", "")).strip(),
                    source=str(item.get("source", "Other")),
                    confidence=item.get("confidence", "medium"),
                )
            )
        return evidence
