"""
ResumePilot AI — Evidence-Based Candidate Evaluation Agent
==========================================================

Frontier Engineering Challenge 2026 (Micro1) work.

This package transforms the single-pass ATS-style analysis of the pre-existing
ResumePilot into an *evidence-grounded* candidate evaluation workflow:

    Job Description
        → Requirement Extraction        (what does the role actually ask for?)
        → Candidate Resume
        → Evidence Extraction           (what factual evidence does the resume contain?)
        → Evidence Matching             (which evidence could support each requirement?)
        → Evidence Verification         (is each requirement SUPPORTED / PARTIAL / NOT VERIFIED?)
        → Recruiter Review Dashboard   (human confirm / reject / needs-review)

Every claim the system makes about a candidate is anchored to a quoted line
from the resume — no unsupported "Candidate score: 82%" without a reason.

Modules
-------
- `models`     : typed data structures for evidence, requirements, verdicts.
- `inference`  : resilient Gemini client wrapper (retry + graceful fallback).
- `prompts`    : the prompt templates used by each agent.
- `agents`     : RequirementExtractor, EvidenceExtractor, Matcher, Verifier.
- `pipeline`   : `run_candidate_evaluation()` orchestrator + baseline evaluator.
"""

__version__ = "0.1.0"
