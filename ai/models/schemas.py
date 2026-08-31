"""Typed data structures for the evidence-based candidate evaluation workflow."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal, Optional

Confidence = Literal["high", "medium", "low"]

# Status of a requirement after evidence verification.
VerdictStatus = Literal[
    "SUPPORTED",           # explicit, verifiable evidence found in the resume
    "PARTIALLY_SUPPORTED", # indirect/weak evidence — e.g. "cloud" without naming AWS
    "NOT_VERIFIED",        # nothing in the resume maps to this requirement
    "NOT_FOUND",           # explicit gap: the term/requirement is absent
]

# Human review decision recorded by a recruiter on the dashboard.
ReviewDecision = Literal["confirm", "reject", "needs_review"]


@dataclass
class Evidence:
    """A single factual claim extracted from the resume, with its source.

    Attributes
    ----------
    skill : str
        The skill / concept the evidence is about (e.g. "Python").
    evidence : str
        The exact supporting sentence (or short quote) from the resume.
    source : str
        Which section of the resume it came from: Experience, Projects,
        Education, Certifications, Skills, Summary, etc.
    confidence : Confidence
        How certain we are that this is genuine, on-point evidence.
    """

    skill: str
    evidence: str
    source: str = "Skills"
    confidence: Confidence = "medium"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Requirement:
    """A requirement extracted from the job description.

    Attributes
    ----------
    text : str
        The requirement as stated (e.g. "Experience with AWS").
    category : str
        Technical, Soft, Certification, Domain, Education, Other.
    importance : Literal["required", "preferred"]
        Whether the JD marks it as required or nice-to-have.
    """

    text: str
    category: str = "Technical"
    importance: Literal["required", "preferred"] = "required"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RequirementVerdict:
    """The verdict for one requirement after evidence verification.

    Attributes
    ----------
    requirement : str
        The requirement text (as extracted from the JD).
    category : str
        Category of the requirement.
    status : VerdictStatus
        SUPPORTED / PARTIALLY_SUPPORTED / NOT_VERIFIED / NOT_FOUND.
    evidence_quotes : list[str]
        The resume quotes that support (or partially support) the requirement.
    confidence : Confidence
        Confidence in this verdict.
    notes : str
        Short human-readable justification.
    review : Optional[ReviewDecision]
        Optional recruiter review recorded on the dashboard.
    """

    requirement: str
    category: str = "Technical"
    status: VerdictStatus = "NOT_VERIFIED"
    evidence_quotes: list[str] = field(default_factory=list)
    confidence: Confidence = "medium"
    notes: str = ""
    review: Optional[ReviewDecision] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateEvaluation:
    """The complete output of the evaluation pipeline for one candidate."""

    requirements: list[Requirement] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    verdicts: list[RequirementVerdict] = field(default_factory=list)
    overall_coverage: float = 0.0  # 0-100, % of requirements with supporting evidence
    summary: str = ""
    mode: str = "gemini"  # "gemini" | "heuristic"

    def to_dict(self) -> dict:
        return {
            "overall_coverage": self.overall_coverage,
            "summary": self.summary,
            "mode": self.mode,
            "requirements": [r.to_dict() for r in self.requirements],
            "evidence": [e.to_dict() for e in self.evidence],
            "verdicts": [v.to_dict() for v in self.verdicts],
        }

    def status_counts(self) -> dict[str, int]:
        counts = {"SUPPORTED": 0, "PARTIALLY_SUPPORTED": 0, "NOT_VERIFIED": 0, "NOT_FOUND": 0}
        for v in self.verdicts:
            counts[v.status] = counts.get(v.status, 0) + 1
        return counts


def coverage_from_verdicts(verdicts: list[RequirementVerdict]) -> float:
    """Compute overall evidence coverage (0-100) from a list of verdicts.

    SUPPORTED counts fully, PARTIALLY_SUPPORTED counts half, the rest count
    zero. This keeps the headline number honest and evidence-grounded.
    """
    if not verdicts:
        return 0.0
    total = 0.0
    for v in verdicts:
        if v.status == "SUPPORTED":
            total += 1.0
        elif v.status == "PARTIALLY_SUPPORTED":
            total += 0.5
    return round(total / len(verdicts) * 100, 1)