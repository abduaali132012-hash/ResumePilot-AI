"""Agent 3 — Evidence Matcher (deterministic, no LLM call).

Maps each requirement to the resume evidence entries that *might* support it,
using token/keyword overlap. This is deliberately a cheap, deterministic,
reproducible step: it does not burn API quota and gives the LLM verifier a
shortlist of candidate quotes to judge, instead of asking it to re-read the
whole resume every time.

A requirement is shortlisted against an evidence entry when the requirement's
significant tokens appear in the evidence text or skill. This is intentionally
*generous* — the Verifier agent decides whether the match is genuine. Being
generous here and strict at verification is what eliminates false positives.
"""
from __future__ import annotations

import re

from ai.models import Evidence, Requirement

# Words that carry no matching signal (stop words, connectors, "years", "x",
# "experience", "strong", "good", etc.). Removing them prevents silly matches
# like "5+ years of experience" matching every requirement.
_STOPWORDS = {
    "a", "an", "the", "of", "in", "for", "with", "and", "or", "to", "on", "at",
    "by", "is", "are", "be", "as", "from", "using", "use", "used", "knowledge",
    "experience", "working", "work", "strong", "good", "excellent", "solid",
    "proven", "years", "year", "plus", "preferred", "required", "ability",
    "including", "etc", "etc.", "e.g", "i.e", "within", "across", "various",
    "handson", "hands-on", "understanding", "familiarity", "familiar", "x",
    "5", "4", "3", "2", "1", "+", "&",
}

_STOP_RE = re.compile(r"[^a-z0-9+#.-]+")


def _tokens(text: str) -> set[str]:
    """Significant lowercase tokens from a string."""
    words = {w for w in _STOP_RE.split(text.lower()) if w}
    return {w for w in words if w and w not in _STOPWORDS and len(w) > 1}


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a)


class Matcher:
    """Shortlists evidence entries for each requirement."""

    def match(self, requirements: list[Requirement], evidence: list[Evidence]) -> dict[str, list[Evidence]]:
        """Return {requirement.text: [candidate Evidence entries]}."""
        by_skill: dict[str, list[Evidence]] = {}
        for ev in evidence:
            key = ev.skill.strip().lower()
            by_skill.setdefault(key, []).append(ev)

        result: dict[str, list[Evidence]] = {}
        for req in requirements:
            req_tokens = _tokens(req.text)
            candidates: list[tuple[float, Evidence]] = []

            # 1) Exact skill-key hit (highest confidence of a genuine match).
            for skill_key, entries in by_skill.items():
                if skill_key in req_tokens or skill_key in req.text.lower():
                    for ev in entries:
                        candidates.append((1.0, ev))

            # 2) Token overlap with the evidence text.
            for ev in evidence:
                ev_tokens = _tokens(ev.skill + " " + ev.evidence)
                score = _overlap(req_tokens, ev_tokens)
                if score >= 0.5:
                    candidates.append((score, ev))

            # Deduplicate by quote, keep best score.
            seen: dict[str, tuple[float, Evidence]] = {}
            for score, ev in candidates:
                q = ev.evidence.strip().lower()
                if q not in seen or score > seen[q][0]:
                    seen[q] = (score, ev)
            result[req.text] = [ev for _, ev in sorted(seen.values(), key=lambda t: -t[0])][:6]
        return result
