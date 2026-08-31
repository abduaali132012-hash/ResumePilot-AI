"""Agent 4 — Evidence Verifier.

Given the requirements and the extracted evidence, produces a `RequirementVerdict`
for every requirement: SUPPORTED / PARTIALLY_SUPPORTED / NOT_VERIFIED /
NOT_FOUND, always anchored to exact quotes from the resume.

This is the agent that turns "Candidate score: 82%" into a defensible,
evidence-backed statement. The prompt is written to be deliberately strict
about weak evidence (a skills-list mention is not "SUPPORTED"; "cloud
experience" is not "AWS").
"""
from __future__ import annotations

import json
from typing import Any

from ai.inference import GeminiClient
from ai.models import Evidence, Requirement, RequirementVerdict
from ai.prompts import VERIFICATION


class Verifier:
    def __init__(self, client: GeminiClient):
        self.client = client

    def verify(
        self,
        requirements: list[Requirement],
        evidence: list[Evidence],
        matched: dict[str, list[Evidence]] | None = None,
    ) -> list[RequirementVerdict]:
        if not requirements:
            return []

        # Keep the evidence shortlist focused so the model reads only what is
        # relevant to this candidate, not an enormous dump.
        if matched:
            selected: list[Evidence] = []
            seen: set[str] = set()
            for entries in matched.values():
                for ev in entries:
                    key = ev.evidence.strip().lower()
                    if key not in seen:
                        seen.add(key)
                        selected.append(ev)
            evidence = selected or evidence

        requirements_json = json.dumps(
            [r.to_dict() for r in requirements], ensure_ascii=False
        )
        evidence_json = json.dumps(
            [e.to_dict() for e in evidence], ensure_ascii=False
        )
        prompt = VERIFICATION.format(
            requirements_json=requirements_json,
            evidence_json=evidence_json,
        )
        data: dict[str, Any] = self.client.generate_json(prompt)
        raw = data.get("verdicts", []) if isinstance(data, dict) else data or []

        # Map raw verdicts back onto the typed Requirement objects so category
        # and importance survive even if the model is sloppy.
        req_by_text = {r.text: r for r in requirements}
        verdicts: list[RequirementVerdict] = []
        for item in raw or []:
            if not isinstance(item, dict) or not item.get("requirement"):
                continue
            req = req_by_text.get(str(item["requirement"]).strip())
            status = str(item.get("status", "NOT_VERIFIED")).upper()
            if status not in {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"}:
                status = "NOT_VERIFIED"
            quotes = item.get("evidence_quotes") or []
            if isinstance(quotes, str):
                quotes = [quotes]
            verdicts.append(
                RequirementVerdict(
                    requirement=str(item["requirement"]).strip(),
                    category=req.category if req else str(item.get("category", "Technical")),
                    status=status,
                    evidence_quotes=[str(q) for q in quotes],
                    confidence=item.get("confidence", "medium"),
                    notes=str(item.get("notes", "")).strip(),
                )
            )

        # Defensive: make sure every requirement has a verdict, even if the
        # model skipped one (shouldn't happen, but keeps coverage honest).
        covered = {v.requirement for v in verdicts}
        for req in requirements:
            if req.text not in covered:
                verdicts.append(
                    RequirementVerdict(
                        requirement=req.text,
                        category=req.category,
                        status="NOT_VERIFIED",
                        notes="Requirement was not explicitly addressed in the available evidence.",
                    )
                )
        return verdicts
