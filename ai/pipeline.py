"""Pipeline: orchestrates the full evidence-based candidate evaluation.

Public API
----------
- `run_candidate_evaluation(resume, jd, client=None)` — the full agentic
  pipeline (Requirement Extraction → Evidence Extraction → Matching →
  Verification). Uses Gemini; raises if the client is unavailable.
- `heuristic_evaluate(resume, jd)` — a deterministic, no-API fallback that
  still produces a structured `CandidateEvaluation` (used when Gemini is down
  or quota is exhausted).
- `auto_evaluate(resume, jd, client=None)` — tries Gemini, falls back to the
  heuristic so the dashboard and CLI never hard-crash on quota/404 errors.
- `baseline_evaluate(client, resume, jd)` — the single-pass LLM evaluator used
  by the evaluation suite to measure the improvement of the agentic pipeline
  over the baseline.
"""
from __future__ import annotations

import re
from typing import Optional

from ai.agents import EvidenceExtractor, Matcher, RequirementExtractor, Verifier
from ai.inference import GeminiClient
from ai.models import (
    CandidateEvaluation,
    Evidence,
    Requirement,
    RequirementVerdict,
    coverage_from_verdicts,
)
from ai.models.schemas import VerdictStatus  # noqa: F401  (re-exported for convenience)


# --------------------------------------------------------------------------- #
# Full agentic pipeline
# --------------------------------------------------------------------------- #
def run_candidate_evaluation(
    resume_text: str,
    job_description: str,
    client: Optional[GeminiClient] = None,
    with_verification: bool = True,
) -> CandidateEvaluation:
    """Run the evidence-based candidate evaluation (Gemini required)."""
    client = client or GeminiClient()
    if not client.available:
        raise RuntimeError(
            "Gemini client unavailable — use auto_evaluate() to fall back to the "
            "deterministic evaluator, or configure GOOGLE_API_KEY / GEMINI_API_KEY."
        )

    requirement_extractor = RequirementExtractor(client)
    evidence_extractor = EvidenceExtractor(client)
    matcher = Matcher()
    verifier = Verifier(client)

    requirements = requirement_extractor.extract(job_description)
    evidence = evidence_extractor.extract(resume_text)

    if with_verification and requirements and evidence:
        matched = matcher.match(requirements, evidence)
        verdicts = verifier.verify(requirements, evidence, matched)
    else:
        # Nothing to verify against — every requirement is unverified.
        verdicts = [
            RequirementVerdict(
                requirement=r.text,
                category=r.category,
                status="NOT_VERIFIED",
                notes="No resume evidence was available to verify this requirement.",
            )
            for r in requirements
        ]

    return CandidateEvaluation(
        requirements=requirements,
        evidence=evidence,
        verdicts=verdicts,
        overall_coverage=coverage_from_verdicts(verdicts),
        summary=_summarize(verdicts),
        mode="gemini",
    )


# --------------------------------------------------------------------------- #
# Deterministic fallback (no API calls)
# --------------------------------------------------------------------------- #
_SKILL_STOP = {
    "the", "and", "of", "for", "with", "to", "in", "on", "at", "experience",
    "knowledge", "strong", "good", "working", "work", "years", "year", "plus",
    "required", "preferred", "a", "an", "is", "are", "using", "use", "used",
    # Generic job-posting filler that is not a real requirement:
    "role", "candidate", "team", "company", "will", "must", "you", "your",
    "job", "position", "looking", "seeking", "ideal", "ability", "responsibilities",
    "responsibility", "qualifications", "including", "etc", "etc.", "ability",
    "ensure", "build", "develop", "help", "join", "want", "new", "join", "we",
    "engineer", "engineering", "senior", "junior", "lead", "developer", "development",
    # More job-posting filler / connective noise that is not a real requirement.
    # Kept here so the deterministic evaluator stops emitting junk "requirements"
    # like "or", "have", "nice", "ad", "hoc", "turn", "grasp" (see QA-2024).
    "or", "and", "have", "has", "nice", "ad", "hoc", "grasp", "turn", "equivalent",
    "excellent", "attention", "delightful", "consuming", "hiring", "proficiency",
    "highly", "fast", "pace", "familiarity", "understanding",
}


def _terms(text: str) -> set[str]:
    return {
        w for w in re.split(r"[^a-z0-9+#.]+", text.lower())
        if w and w not in _SKILL_STOP and len(w) > 1
    }


def heuristic_evaluate(resume_text: str, job_description: str) -> CandidateEvaluation:
    """Deterministic, quota-free evaluation.

    Extracts requirements by simple term frequency from the JD and scores each
    against the resume via token overlap. Less nuanced than the agent pipeline
    but always available — this is what keeps the app usable during Gemini
    outages or quota exhaustion.
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # --- Requirements: top frequent significant terms in the JD ------------ #
    jd_terms = _terms(job_description)
    freq: dict[str, int] = {}
    for term in jd_terms:
        freq[term] = len(re.findall(r"\b" + re.escape(term) + r"\b", jd_lower))
    # Total order: frequency descending, then term alphabetically. Breaking
    # ties on the term keeps the ranking stable regardless of PYTHONHASHSEED /
    # set iteration order, which made identical inputs produce different
    # requirement sets (and different accuracy) on every run (QA-2024).
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    # Filter out resume-parsing junk / numbers-only tokens.
    requirements = [
        Requirement(text=term, category="Technical", importance="required")
        for term, count in ranked[:12]
        if count >= 1 and not term.replace(".", "").replace("#", "").isdigit() and len(term) > 1
    ]
    if not requirements:
        return CandidateEvaluation(mode="heuristic", summary="No requirements could be extracted.")

    # --- Verdicts: does the resume contain each term? ----------------------- #
    verdicts: list[RequirementVerdict] = []
    for req in requirements:
        term = req.text
        present = re.search(r"\b" + re.escape(term) + r"\b", resume_lower) is not None
        if present:
            verdicts.append(
                RequirementVerdict(
                    requirement=term,
                    category=req.category,
                    status="SUPPORTED",
                    evidence_quotes=[f"Resume mentions '{term}'."],
                    confidence="low",
                    notes=f"Keyword '{term}' appears in the resume (deterministic check).",
                )
            )
        else:
            verdicts.append(
                RequirementVerdict(
                    requirement=term,
                    category=req.category,
                    status="NOT_FOUND",
                    confidence="high",
                    notes=f"Keyword '{term}' was not found in the resume.",
                )
            )

    return CandidateEvaluation(
        requirements=requirements,
        evidence=[
            Evidence(skill=t, evidence=f"Resume mentions '{t}'.", source="Skills", confidence="low")
            for t in sorted({v.requirement for v in verdicts if v.status == "SUPPORTED"})
        ],
        verdicts=verdicts,
        overall_coverage=coverage_from_verdicts(verdicts),
        summary=_summarize(verdicts) + " (deterministic fallback)",
        mode="heuristic",
    )


def auto_evaluate(
    resume_text: str,
    job_description: str,
    client: Optional[GeminiClient] = None,
) -> CandidateEvaluation:
    """Try the full agent pipeline, fall back to the deterministic evaluator."""
    try:
        return run_candidate_evaluation(resume_text, job_description, client=client)
    except Exception:
        return heuristic_evaluate(resume_text, job_description)


# --------------------------------------------------------------------------- #
# Baseline evaluator (for measuring agent improvement)
# --------------------------------------------------------------------------- #
def baseline_evaluate(
    client: GeminiClient,
    resume_text: str,
    job_description: str,
) -> CandidateEvaluation:
    """The single-pass LLM baseline.

    Mirrors the old 'single-pass' behaviour of the pre-Micro1 app: one prompt,
    one holistic judgement, no structured evidence. Used ONLY by the evaluation
    suite to quantify what the agentic pipeline adds.
    """
    from ai.prompts.templates import REQUIREMENT_EXTRACTION

    prompt = (
        REQUIREMENT_EXTRACTION.format(job_description=job_description)
        + "\n\nThen, for EACH requirement, judge against the resume below whether the "
        "resume provides evidence. Return ONLY JSON with key 'verdicts': array of "
        "{requirement, category, status (SUPPORTED|PARTIALLY_SUPPORTED|NOT_VERIFIED|NOT_FOUND), "
        "evidence_quotes, confidence, notes}.\n\n[RESUME]\n" + resume_text
    )
    data = client.generate_json(prompt)
    raw = data.get("verdicts", []) if isinstance(data, dict) else data or []
    verdicts = [
        RequirementVerdict(
            requirement=str(item["requirement"]),
            category=str(item.get("category", "Technical")),
            status=str(item.get("status", "NOT_VERIFIED")).upper(),
            evidence_quotes=[str(q) for q in (item.get("evidence_quotes") or [])] if item.get("evidence_quotes") else [],
            confidence=item.get("confidence", "medium"),
            notes=str(item.get("notes", "")).strip(),
        )
        for item in raw or []
        if isinstance(item, dict) and item.get("requirement")
    ]
    return CandidateEvaluation(
        verdicts=verdicts,
        overall_coverage=coverage_from_verdicts(verdicts),
        summary=_summarize(verdicts),
        mode="baseline",
    )


def _summarize(verdicts: list[RequirementVerdict]) -> str:
    counts = {v.status: 0 for v in verdicts}
    for v in verdicts:
        counts[v.status] = counts.get(v.status, 0) + 1
    n = len(verdicts)
    supported = counts.get("SUPPORTED", 0)
    partial = counts.get("PARTIALLY_SUPPORTED", 0)
    missing = counts.get("NOT_VERIFIED", 0) + counts.get("NOT_FOUND", 0)
    return (
        f"Of {n} extracted requirements, {supported} are supported by explicit resume "
        f"evidence, {partial} are only partially supported, and {missing} are not verified."
    )
