"""
SpecCheck tests — one function per requirement ID.

Covered: REQ-01 through REQ-10, REQ-12 (IMPLEMENTED_UNTESTED and PARTIAL).
REQ-11 is already IMPLEMENTED_AND_TESTED.
REQ-13 is MISSING (no code to test).

All tests run offline. No GOOGLE_API_KEY is set (conftest.py strips it).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]

# ────────────────────────────────────────────────────────────────────────────
# Local imports (repo root is on sys.path via conftest.py)
# ────────────────────────────────────────────────────────────────────────────
from ai.agents.requirement_extractor import RequirementExtractor
from ai.agents.evidence_extractor import EvidenceExtractor
from ai.agents.matcher import Matcher
from ai.agents.verifier import Verifier
from ai.models.schemas import (
    CandidateEvaluation,
    Evidence,
    Requirement,
    RequirementVerdict,
    ReviewDecision,
)
from ai.pipeline import heuristic_evaluate, auto_evaluate

from tests.speccheck.helpers import FakeClient, SAMPLE_JD, SAMPLE_RESUME


# ============================================================================
# REQ-01 — RequirementExtractor splits compound requirements
# ============================================================================

class TestReq01:
    """REQ-01: RequirementExtractor.extract() returns Requirement objects;
    compound items ("Python and FastAPI") must become two separate entries."""

    def _make_extractor(self, items: list[dict]) -> RequirementExtractor:
        return RequirementExtractor(FakeClient({"requirements": items}))

    def test_req_01_returns_list_of_requirement_objects(self):
        """extract() must return a list of Requirement dataclasses."""
        extractor = self._make_extractor([
            {"text": "Python", "category": "Technical", "importance": "required"},
        ])
        result = extractor.extract("We need Python.")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Requirement)

    def test_req_01_compound_split_produces_two_requirements(self):
        """When the LLM splits "Python and FastAPI" the extractor must surface
        both as independent Requirement objects (one per list entry)."""
        extractor = self._make_extractor([
            {"text": "Python", "category": "Technical", "importance": "required"},
            {"text": "FastAPI", "category": "Technical", "importance": "required"},
        ])
        result = extractor.extract("We need Python and FastAPI.")
        texts = [r.text for r in result]
        assert "Python" in texts, "Python must appear as a separate requirement"
        assert "FastAPI" in texts, "FastAPI must appear as a separate requirement"

    def test_req_01_empty_jd_returns_empty_list(self):
        """Empty input must return an empty list without raising."""
        extractor = self._make_extractor([])
        assert extractor.extract("") == []
        assert extractor.extract("   ") == []

    def test_req_01_requirement_has_required_fields(self):
        """Each Requirement must carry text, category, and importance."""
        extractor = self._make_extractor([
            {"text": "Docker", "category": "Technical", "importance": "preferred"},
        ])
        req = extractor.extract("Experience with Docker preferred.")[0]
        assert req.text == "Docker"
        assert req.category == "Technical"
        assert req.importance == "preferred"

    def test_req_01_items_without_text_are_skipped(self):
        """Malformed items (missing 'text') must be silently discarded."""
        extractor = self._make_extractor([
            {},
            {"text": "", "category": "Technical"},
            {"text": "Python", "category": "Technical", "importance": "required"},
        ])
        result = extractor.extract("We need Python.")
        assert len(result) == 1
        assert result[0].text == "Python"


# ============================================================================
# REQ-02 — EvidenceExtractor outputs structured claims without scoring/verdict
# ============================================================================

class TestReq02:
    """REQ-02: EvidenceExtractor.extract() returns Evidence objects that have
    no score or verdict field."""

    def _make_extractor(self, items: list[dict]) -> EvidenceExtractor:
        return EvidenceExtractor(FakeClient({"evidence": items}))

    def test_req_02_returns_list_of_evidence_objects(self):
        """extract() must return a list of Evidence dataclasses."""
        extractor = self._make_extractor([
            {"skill": "Python", "evidence": "Built APIs with Python.", "source": "Experience", "confidence": "high"},
        ])
        result = extractor.extract("Some resume text.")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Evidence)

    def test_req_02_evidence_has_no_score_field(self):
        """Evidence objects must NOT have a 'score' attribute."""
        extractor = self._make_extractor([
            {"skill": "Python", "evidence": "Built APIs with Python.", "source": "Experience", "confidence": "high"},
        ])
        ev = extractor.extract("Some resume.")[0]
        assert not hasattr(ev, "score"), "Evidence must not carry a score field"

    def test_req_02_evidence_has_no_verdict_field(self):
        """Evidence objects must NOT have a 'verdict' attribute."""
        extractor = self._make_extractor([
            {"skill": "Python", "evidence": "Built APIs with Python.", "source": "Experience", "confidence": "high"},
        ])
        ev = extractor.extract("Some resume.")[0]
        assert not hasattr(ev, "verdict"), "Evidence must not carry a verdict field"

    def test_req_02_evidence_schema_fields(self):
        """Evidence must expose exactly: skill, evidence, source, confidence."""
        extractor = self._make_extractor([
            {"skill": "Docker", "evidence": "Used Docker in production.", "source": "Experience", "confidence": "medium"},
        ])
        ev = extractor.extract("Docker experience.")[0]
        assert ev.skill == "Docker"
        assert "Docker" in ev.evidence
        assert ev.source == "Experience"
        assert ev.confidence == "medium"

    def test_req_02_empty_resume_returns_empty_list(self):
        """Empty resume input must return [] without raising."""
        extractor = self._make_extractor([])
        assert extractor.extract("") == []

    def test_req_02_items_without_skill_are_skipped(self):
        """Items missing 'skill' must be silently discarded."""
        extractor = self._make_extractor([
            {},
            {"skill": "", "evidence": "Built something."},
            {"skill": "Python", "evidence": "Used Python.", "source": "Experience", "confidence": "high"},
        ])
        result = extractor.extract("Some resume.")
        assert len(result) == 1
        assert result[0].skill == "Python"


# ============================================================================
# REQ-03 — Matcher uses deterministic logic (no LLM call)
# ============================================================================

class TestReq03:
    """REQ-03: Matcher.match() uses pure token overlap — no LLM calls.
    Output must be stable across calls with the same inputs."""

    REQUIREMENTS = [
        Requirement(text="Experience with Python"),
        Requirement(text="Experience with FastAPI"),
        Requirement(text="AWS cloud experience"),
    ]
    EVIDENCE = [
        Evidence(skill="Python", evidence="Built APIs with Python and FastAPI."),
        Evidence(skill="FastAPI", evidence="Built FastAPI services for dashboards."),
        Evidence(skill="cloud", evidence="Worked with cloud infrastructure."),
    ]

    def test_req_03_match_returns_dict_keyed_by_requirement_text(self):
        """match() must return a dict whose keys are the requirement texts."""
        result = Matcher().match(self.REQUIREMENTS, self.EVIDENCE)
        assert isinstance(result, dict)
        for req in self.REQUIREMENTS:
            assert req.text in result

    def test_req_03_no_llm_call_on_match(self):
        """Matcher must never call any method that requires a GeminiClient."""
        # If Matcher ever tried to import GeminiClient it would fail because
        # the network is absent and no key is set.  We additionally verify the
        # class has no client attribute.
        m = Matcher()
        assert not hasattr(m, "client"), "Matcher must not hold a GeminiClient"

    def test_req_03_identical_output_on_repeated_calls(self):
        """Calling match() twice with identical inputs must return identical results."""
        m = Matcher()
        r1 = m.match(self.REQUIREMENTS, self.EVIDENCE)
        r2 = m.match(self.REQUIREMENTS, self.EVIDENCE)
        assert r1 == r2, "Matcher output is not deterministic"

    def test_req_03_python_requirement_matches_python_evidence(self):
        """'Experience with Python' should surface the Python evidence entry."""
        result = Matcher().match(self.REQUIREMENTS, self.EVIDENCE)
        python_matches = result.get("Experience with Python", [])
        skills = [e.skill for e in python_matches]
        assert "Python" in skills

    def test_req_03_empty_inputs_return_empty_lists(self):
        """match() on empty lists must return a dict with empty value lists."""
        result = Matcher().match(
            [Requirement(text="Python")],
            [],
        )
        assert result["Python"] == []

    def test_req_03_stable_across_different_pythonhashseed(self):
        """Output must be the same regardless of PYTHONHASHSEED.

        We simulate different hash seeds by running the match in a subprocess
        with an explicit PYTHONHASHSEED and comparing to a second run.
        """
        root_fwd = str(ROOT).replace("\\", "/")
        script = (
            "import sys, json; sys.path.insert(0, '" + root_fwd + "');\n"
            "from ai.agents.matcher import Matcher;\n"
            "from ai.models.schemas import Requirement, Evidence;\n"
            "reqs = [Requirement(text='Python'), Requirement(text='FastAPI')];\n"
            "evs = [Evidence(skill='Python', evidence='Built APIs with Python.'),\n"
            "       Evidence(skill='FastAPI', evidence='FastAPI services deployed.')];\n"
            "result = Matcher().match(reqs, evs);\n"
            "out = {k: [e.skill for e in v] for k,v in result.items()};\n"
            "print(json.dumps(out, sort_keys=True))\n"
        )
        env1 = {**os.environ, "PYTHONHASHSEED": "0"}
        env2 = {**os.environ, "PYTHONHASHSEED": "12345"}
        r1 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env1)
        r2 = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env2)
        assert r1.returncode == 0, f"seed=0 failed: {r1.stderr}"
        assert r2.returncode == 0, f"seed=12345 failed: {r2.stderr}"
        assert r1.stdout.strip() == r2.stdout.strip(), (
            "Matcher output differs across PYTHONHASHSEED values:\n"
            f"  seed=0:     {r1.stdout.strip()}\n"
            f"  seed=12345: {r2.stdout.strip()}"
        )


# ============================================================================
# REQ-04 — Verifier returns one of four verdict statuses, with quotes
# ============================================================================

class TestReq04:
    """REQ-04 (PARTIAL): Verifier must assign one of the four allowed statuses
    to every requirement, and non-NOT_FOUND verdicts should carry quotes.

    The code-level guarantee is tested here; the prompt-only quote rule is
    recorded as a defect (the code does NOT enforce non-empty evidence_quotes).
    """

    VALID_STATUSES = {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"}

    def _verifier(self, raw_verdicts: list[dict]) -> Verifier:
        return Verifier(FakeClient({"verdicts": raw_verdicts}))

    def test_req_04_all_four_statuses_are_valid(self):
        """VerdictStatus type accepts exactly the four documented values."""
        # These are Literal types; we test by constructing objects and checking
        # that arbitrary strings are normalised or coerced by the Verifier.
        for status in self.VALID_STATUSES:
            verdict = RequirementVerdict(requirement="Python", status=status)
            assert verdict.status == status

    def test_req_04_every_requirement_receives_a_verdict(self):
        """Verifier must produce one verdict per requirement (defensive fallback)."""
        reqs = [
            Requirement(text="Python"),
            Requirement(text="FastAPI"),
            Requirement(text="Kubernetes"),
        ]
        # LLM returns only one verdict — the others must be filled in.
        raw = [
            {"requirement": "Python", "status": "SUPPORTED",
             "evidence_quotes": ["Built APIs with Python."], "confidence": "high", "notes": ""},
        ]
        verifier = self._verifier(raw)
        verdicts = verifier.verify(reqs, [])
        req_texts = {v.requirement for v in verdicts}
        for req in reqs:
            assert req.text in req_texts, f"Missing verdict for requirement '{req.text}'"

    def test_req_04_unknown_status_is_coerced_to_not_verified(self):
        """An out-of-vocabulary status string must be coerced to NOT_VERIFIED."""
        reqs = [Requirement(text="Python")]
        raw = [
            {"requirement": "Python", "status": "MAYBE_SUPPORTED",
             "evidence_quotes": [], "confidence": "low", "notes": ""},
        ]
        verifier = self._verifier(raw)
        verdicts = verifier.verify(reqs, [])
        assert verdicts[0].status == "NOT_VERIFIED"

    def test_req_04_status_is_uppercased(self):
        """Lowercase status strings from the model must be uppercased."""
        reqs = [Requirement(text="Python")]
        raw = [
            {"requirement": "Python", "status": "supported",
             "evidence_quotes": ["Used Python"], "confidence": "high", "notes": ""},
        ]
        verifier = self._verifier(raw)
        verdicts = verifier.verify(reqs, [])
        assert verdicts[0].status == "SUPPORTED"

    @pytest.mark.xfail(strict=True, reason="REQ-04 defect: SUPPORTED verdict allowed with empty evidence_quotes; code-level guard missing")
    def test_req_04_defect_supported_verdict_may_have_empty_quotes(self):
        """PRD requirement (REQ-04): a SUPPORTED or PARTIALLY_SUPPORTED verdict
        must carry at least one evidence_quote.  The code currently allows
        empty quotes through — this test asserts the REQUIRED behaviour and is
        marked xfail until the defect is fixed.
        """
        reqs = [Requirement(text="Python")]
        raw = [
            # LLM returns SUPPORTED with an empty quotes list.
            {"requirement": "Python", "status": "SUPPORTED",
             "evidence_quotes": [], "confidence": "high", "notes": "Present."},
        ]
        verifier = self._verifier(raw)
        verdicts = verifier.verify(reqs, [])
        # Required behaviour: a code-level guard must either reject the verdict
        # or coerce empty-quotes SUPPORTED → NOT_VERIFIED.
        assert len(verdicts[0].evidence_quotes) >= 1, (
            "REQ-04: SUPPORTED verdict must have at least one evidence_quote; "
            "code-level enforcement is missing."
        )


# ============================================================================
# REQ-05a — Skills-list-only mention is not SUPPORTED
# ============================================================================

class TestReq05a:
    """REQ-05a: A skill mentioned only in a skills list should NOT yield
    SUPPORTED — the heuristic evaluator and verifier coercion are tested."""

    @pytest.mark.xfail(strict=True, reason="REQ-05a defect: heuristic marks bare skills-list keyword as SUPPORTED; no usage-context check")
    def test_req_05a_skills_list_in_heuristic_gives_supported_by_keyword(self):
        """PRD requirement (REQ-05a): a skill mentioned only in a skills list
        must NOT yield SUPPORTED — usage context is required.

        The heuristic evaluator has no context check, so it returns SUPPORTED
        for any resume that mentions the keyword.  This test asserts the
        REQUIRED behaviour and is marked xfail until the defect is fixed.
        """
        resume = "Skills: Python, FastAPI, Docker"  # skills list only, no usage context
        jd = "Requires Python."
        result = heuristic_evaluate(resume, jd)
        python_verdicts = [v for v in result.verdicts if "python" in v.requirement.lower()]
        assert len(python_verdicts) >= 1, "Expected at least one verdict about Python"
        # Required behaviour: skills-list-only mention must NOT yield SUPPORTED.
        for v in python_verdicts:
            assert v.status != "SUPPORTED", (
                "REQ-05a: skill mentioned only in a skills list must not be SUPPORTED; "
                "usage context is required."
            )

    @pytest.mark.xfail(strict=True, reason="REQ-05a defect: Verifier has no code guard against skills-list-only SUPPORTED; prompt-only rule")
    def test_req_05a_verifier_status_allow_list_prevents_spurious_supported(self):
        """PRD requirement (REQ-05a): the Verifier must not pass SUPPORTED through
        when the LLM's only evidence is a skills-list mention.

        No code guard currently exists — the test asserts the REQUIRED behaviour
        (SUPPORTED blocked or downgraded) and is marked xfail until fixed.
        """
        reqs = [Requirement(text="Python")]
        # Simulate LLM returning SUPPORTED backed only by a skills-list quote.
        raw = [{"requirement": "Python", "status": "SUPPORTED",
                "evidence_quotes": ["Python listed in skills."], "confidence": "low", "notes": ""}]
        verifier = Verifier(FakeClient({"verdicts": raw}))
        verdicts = verifier.verify(reqs, [])
        # Required behaviour: skills-list-only quote must not yield SUPPORTED.
        assert verdicts[0].status != "SUPPORTED", (
            "REQ-05a: Verifier must not produce SUPPORTED when evidence is only "
            "a skills-list entry — a code-level guard is required."
        )


# ============================================================================
# REQ-05b — "Cloud experience" not treated as AWS
# ============================================================================

class TestReq05b:
    """REQ-05b: "Cloud experience" must not yield SUPPORTED for an AWS
    requirement.  This is enforced only by prompt; no code guard exists."""

    CLOUD_RESUME = (
        "Experienced cloud engineer. Worked with cloud infrastructure "
        "and deployment pipelines in multiple environments."
    )
    AWS_JD = "Requires experience with AWS."

    @pytest.mark.xfail(strict=True, reason="REQ-01 defect: heuristic extractor returns 'requires' instead of the technology")
    def test_req_05b_heuristic_cloud_is_not_aws(self):
        """heuristic_evaluate() checks for the exact word 'aws'.
        A resume that only says 'cloud' must NOT yield SUPPORTED for AWS."""
        result = heuristic_evaluate(self.CLOUD_RESUME, self.AWS_JD)
        all_reqs = [v.requirement for v in result.verdicts]
        aws_verdicts = [v for v in result.verdicts if v.requirement.lower() == "aws"]
        assert len(aws_verdicts) >= 1, (
            f"Expected 'aws' in requirements, got: {all_reqs}"
        )
        for v in aws_verdicts:
            assert v.status != "SUPPORTED", (
                f"REQ-05b FAIL: heuristic marked 'cloud-only' resume as SUPPORTED "
                f"for requirement '{v.requirement}'"
            )

    @pytest.mark.xfail(strict=True, reason="REQ-05b defect: Verifier allows 'cloud experience' as AWS evidence; no code-level guard")
    def test_req_05b_verifier_code_does_not_prevent_cloud_as_aws(self):
        """PRD requirement (REQ-05b): 'cloud experience' must NOT be accepted as
        evidence for an AWS-specific requirement.

        The Verifier currently has no code guard — it passes SUPPORTED through
        whenever the LLM says so.  This test asserts the REQUIRED behaviour
        (cloud ≠ AWS) and is marked xfail until the defect is fixed.
        """
        reqs = [Requirement(text="AWS experience")]
        raw = [
            {
                "requirement": "AWS experience",
                "status": "SUPPORTED",
                # LLM incorrectly treats "cloud experience" as AWS evidence.
                "evidence_quotes": ["Worked with cloud infrastructure"],
                "confidence": "medium",
                "notes": "Cloud experience interpreted as AWS",
            }
        ]
        verifier = Verifier(FakeClient({"verdicts": raw}))
        verdicts = verifier.verify(reqs, [])
        # Required behaviour: generic "cloud" evidence must not yield SUPPORTED for AWS.
        assert verdicts[0].status != "SUPPORTED", (
            "REQ-05b: Verifier must not produce SUPPORTED when the sole quote is "
            "'cloud experience' for an AWS requirement — a code-level guard is required."
        )


# ============================================================================
# REQ-05c — "Working knowledge of X" not treated as full experience
# ============================================================================

class TestReq05c:
    """REQ-05c: 'working knowledge of X' must not yield SUPPORTED for X."""

    @pytest.mark.xfail(strict=True, reason="REQ-05c defect: heuristic marks 'working knowledge of X' as SUPPORTED; no context-awareness")
    def test_req_05c_heuristic_does_not_inflate_working_knowledge(self):
        """PRD requirement (REQ-05c): 'working knowledge of X' must NOT yield
        SUPPORTED for X — it is weaker than full experience.

        The heuristic evaluator has no context check; it returns SUPPORTED for
        any keyword match.  This test asserts the REQUIRED behaviour and is
        marked xfail until the defect is fixed.
        """
        resume = "Has working knowledge of Kubernetes."
        jd = "Requires extensive Kubernetes experience."
        result = heuristic_evaluate(resume, jd)
        k8s_verdicts = [v for v in result.verdicts if "kubernetes" in v.requirement.lower()]
        assert len(k8s_verdicts) >= 1, (
            f"Expected kubernetes in requirements, got: {[v.requirement for v in result.verdicts]}"
        )
        for v in k8s_verdicts:
            # Required behaviour: working-knowledge claim must not be SUPPORTED.
            assert v.status != "SUPPORTED", (
                "REQ-05c: 'working knowledge of Kubernetes' must not be marked SUPPORTED; "
                "it is weaker than full experience and must not inflate to SUPPORTED."
            )

    @pytest.mark.xfail(strict=True, reason="REQ-05c defect: Verifier has no code guard against 'working knowledge' inflation; prompt-only rule")
    def test_req_05c_verifier_no_code_guard_against_inflation(self):
        """PRD requirement (REQ-05c): the Verifier must not pass SUPPORTED through
        when the LLM's evidence quote only claims 'working knowledge of X'.

        No code guard currently exists.  This test asserts the REQUIRED behaviour
        and is marked xfail until the defect is fixed.
        """
        reqs = [Requirement(text="Kubernetes experience")]
        raw = [
            {
                "requirement": "Kubernetes experience",
                "status": "SUPPORTED",
                "evidence_quotes": ["Has working knowledge of Kubernetes."],
                "confidence": "low",
                "notes": "Inflated from working-knowledge claim",
            }
        ]
        verifier = Verifier(FakeClient({"verdicts": raw}))
        verdicts = verifier.verify(reqs, [])
        # Required behaviour: working-knowledge quote must not yield SUPPORTED.
        assert verdicts[0].status != "SUPPORTED", (
            "REQ-05c: Verifier must not produce SUPPORTED when evidence only states "
            "'working knowledge of X' — a code-level guard is required."
        )


# ============================================================================
# REQ-05d — Absent technology is never SUPPORTED
# ============================================================================

class TestReq05d:
    """REQ-05d: A technology not mentioned in the resume must never receive
    the SUPPORTED verdict."""

    @pytest.mark.xfail(strict=True, reason="REQ-01 defect: heuristic extractor returns 'requires' instead of the technology")
    def test_req_05d_heuristic_absent_technology_not_supported(self):
        """heuristic_evaluate() must return NOT_FOUND for a term absent from the resume."""
        resume = "Python developer with FastAPI experience."
        jd = "Requires Kubernetes."
        result = heuristic_evaluate(resume, jd)
        k8s_verdicts = [v for v in result.verdicts if "kubernetes" in v.requirement.lower()]
        assert len(k8s_verdicts) >= 1, (
            f"Expected kubernetes requirement in result, got: {[v.requirement for v in result.verdicts]}"
        )
        for v in k8s_verdicts:
            assert v.status != "SUPPORTED", (
                f"REQ-05d FAIL: absent term 'kubernetes' marked as SUPPORTED"
            )

    def test_req_05d_heuristic_absent_term_is_not_found(self):
        """heuristic_evaluate() returns NOT_FOUND for terms absent from the resume."""
        resume = "Python developer."
        jd = "Requires Kubernetes and Terraform."
        result = heuristic_evaluate(resume, jd)
        absent_terms = {"kubernetes", "terraform"}
        for v in result.verdicts:
            if v.requirement.lower() in absent_terms:
                assert v.status == "NOT_FOUND", (
                    f"Expected NOT_FOUND for absent term '{v.requirement}', got '{v.status}'"
                )

    def test_req_05d_verifier_unknown_status_coerced_not_inflated(self):
        """Unknown/OOV status is coerced to NOT_VERIFIED, never SUPPORTED."""
        reqs = [Requirement(text="Terraform")]
        raw = [
            {
                "requirement": "Terraform",
                "status": "INVENTED_STATUS",  # out-of-vocabulary
                "evidence_quotes": [],
                "confidence": "low",
                "notes": "",
            }
        ]
        verifier = Verifier(FakeClient({"verdicts": raw}))
        verdicts = verifier.verify(reqs, [])
        assert verdicts[0].status == "NOT_VERIFIED"
        assert verdicts[0].status != "SUPPORTED"

    def test_req_05d_verifier_missing_requirement_gets_not_verified_not_supported(self):
        """Requirements skipped by the LLM get NOT_VERIFIED in the fallback — not SUPPORTED."""
        reqs = [
            Requirement(text="Python"),
            Requirement(text="Terraform"),  # LLM skips this
        ]
        raw = [
            {"requirement": "Python", "status": "SUPPORTED",
             "evidence_quotes": ["Python used."], "confidence": "high", "notes": ""},
        ]
        verifier = Verifier(FakeClient({"verdicts": raw}))
        verdicts = verifier.verify(reqs, [])
        terraform_v = next(v for v in verdicts if v.requirement == "Terraform")
        assert terraform_v.status == "NOT_VERIFIED"
        assert terraform_v.status != "SUPPORTED"


# ============================================================================
# REQ-06 — Works without an API key (deterministic fallback)
# ============================================================================

class TestReq06:
    """REQ-06: When no API key is configured the system must fall back to the
    deterministic heuristic evaluator and still return a CandidateEvaluation."""

    def test_req_06_no_api_key_gemini_client_not_available(self, monkeypatch):
        """GeminiClient.available must be False when no key is set.

        Uses monkeypatch to isolate from ALL key sources — env vars, any local
        .streamlit/secrets.toml, and st.secrets — so the test is hermetic on
        every developer machine regardless of what secrets they have configured.
        """
        from ai.inference import GeminiClient
        # Patch the entire key-resolution function so neither st.secrets nor a
        # local .streamlit/secrets.toml can leak in.
        monkeypatch.setattr("ai.inference.get_api_key", lambda: None)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        client = GeminiClient()
        assert client.available is False

    def test_req_06_auto_evaluate_falls_back_without_key(self):
        """auto_evaluate() must return a CandidateEvaluation even without a key.

        We pass a no-op client that raises RuntimeError to guarantee the
        fallback path is exercised regardless of local secrets.toml content.
        """
        class _UnavailableClient:
            available = False
            api_key = None
            client = None
        with patch("ai.pipeline.run_candidate_evaluation", side_effect=RuntimeError("no key")):
            result = auto_evaluate(SAMPLE_RESUME, SAMPLE_JD, client=_UnavailableClient())
        assert isinstance(result, CandidateEvaluation)

    def test_req_06_heuristic_evaluate_returns_structured_result(self):
        """heuristic_evaluate() must return a CandidateEvaluation with verdicts."""
        result = heuristic_evaluate(SAMPLE_RESUME, SAMPLE_JD)
        assert isinstance(result, CandidateEvaluation)
        assert len(result.verdicts) > 0, "heuristic_evaluate must produce at least one verdict"

    def test_req_06_heuristic_mode_field_is_set(self):
        """heuristic_evaluate() must set mode='heuristic' on the result."""
        result = heuristic_evaluate(SAMPLE_RESUME, SAMPLE_JD)
        assert result.mode == "heuristic"

    def test_req_06_fallback_produces_valid_verdicts(self):
        """Every verdict in the heuristic result must have a valid status."""
        valid = {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"}
        result = heuristic_evaluate(SAMPLE_RESUME, SAMPLE_JD)
        for v in result.verdicts:
            assert v.status in valid, f"Invalid status '{v.status}' from heuristic evaluator"

    def test_req_06_auto_evaluate_without_key_uses_heuristic_mode(self):
        """auto_evaluate() with no key must ultimately call heuristic_evaluate."""
        from ai.pipeline import run_candidate_evaluation
        # Patch run_candidate_evaluation to raise (simulating unavailable client).
        with patch("ai.pipeline.run_candidate_evaluation", side_effect=RuntimeError("no key")):
            result = auto_evaluate(SAMPLE_RESUME, SAMPLE_JD, client=None)
        assert result.mode == "heuristic"


# ============================================================================
# REQ-07 — --heuristic run is reproducible across PYTHONHASHSEED values
# ============================================================================

class TestReq07:
    """REQ-07: heuristic_evaluate() must return identical results when run
    with different PYTHONHASHSEED values."""

    SCRIPT = """\
import sys, json
sys.path.insert(0, r'{root}')
from ai.pipeline import heuristic_evaluate
jd = (
    "We are hiring a Python backend engineer. "
    "Strong experience with Python, FastAPI, PostgreSQL, and Docker. "
    "Kubernetes or AWS is a plus."
)
resume = (
    "Python engineer. Built FastAPI services. Managed PostgreSQL databases. "
    "Deployed Docker containers. Worked with AWS and Kubernetes."
)
result = heuristic_evaluate(resume, jd)
output = sorted([
    {{'req': v.requirement, 'status': v.status}}
    for v in result.verdicts
], key=lambda x: x['req'])
print(json.dumps(output))
""".format(root=str(ROOT))

    def _run_with_seed(self, seed: str) -> str:
        env = {**os.environ, "PYTHONHASHSEED": seed,
               "GOOGLE_API_KEY": "", "GEMINI_API_KEY": ""}
        r = subprocess.run(
            [sys.executable, "-c", self.SCRIPT],
            capture_output=True, text=True, env=env,
        )
        assert r.returncode == 0, f"seed={seed} failed:\n{r.stderr}"
        return r.stdout.strip()

    def test_req_07_identical_output_seed_0_vs_seed_12345(self):
        """heuristic_evaluate() must produce the same sorted verdicts with
        PYTHONHASHSEED=0 and PYTHONHASHSEED=12345."""
        out0 = self._run_with_seed("0")
        out1 = self._run_with_seed("12345")
        assert out0 == out1, (
            "REQ-07 FAIL: heuristic output differs across PYTHONHASHSEED values.\n"
            f"  seed=0:     {out0}\n"
            f"  seed=12345: {out1}"
        )

    def test_req_07_identical_output_seed_1_vs_seed_99999(self):
        """Second pair of seeds to catch regressions."""
        out1 = self._run_with_seed("1")
        out2 = self._run_with_seed("99999")
        assert out1 == out2, (
            "REQ-07 FAIL: heuristic output differs between seed=1 and seed=99999."
        )


# ============================================================================
# REQ-08a — Harness writes evaluation/baseline_results.json
# ============================================================================

class TestReq08a:
    """REQ-08a: run_evaluation.py must write evaluation/baseline_results.json."""

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "REQ-08 defect: harness crashes with KeyError 'expected' on the committed "
            "ground-truth files (case_01..case_10 use key 'requirements', not 'expected') "
            "on a clean checkout"
        ),
    )
    def test_req_08a_harness_writes_baseline_results_json(self, tmp_path):
        """Run the harness with --heuristic and check baseline_results.json is written."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "evaluation" / "run_evaluation.py"), "--heuristic"],
            capture_output=True, text=True,
            cwd=str(ROOT),
            env={**os.environ, "GOOGLE_API_KEY": "", "GEMINI_API_KEY": "",
                 "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        assert result.returncode == 0, (
            f"Harness exited with code {result.returncode}:\n{result.stderr}"
        )
        output_file = ROOT / "evaluation" / "baseline_results.json"
        assert output_file.exists(), "evaluation/baseline_results.json was not written"

    def test_req_08a_baseline_results_is_valid_json(self):
        """evaluation/baseline_results.json must be parseable as JSON."""
        output_file = ROOT / "evaluation" / "baseline_results.json"
        if not output_file.exists():
            pytest.skip("baseline_results.json not present — run REQ-08a first")
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "baseline_results.json must be a JSON object"

    def test_req_08a_baseline_results_contains_case_entries(self):
        """Each top-level key in baseline_results.json must contain evaluation metrics."""
        output_file = ROOT / "evaluation" / "baseline_results.json"
        if not output_file.exists():
            pytest.skip("baseline_results.json not present")
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert len(data) > 0, "baseline_results.json must have at least one case entry"
        for case_name, case_data in data.items():
            assert "evidence_accuracy" in case_data, (
                f"Case '{case_name}' missing 'evidence_accuracy' key"
            )


# ============================================================================
# REQ-08b — Harness writes evaluation/agent_results.json
# ============================================================================

class TestReq08b:
    """REQ-08b: run_evaluation.py must write evaluation/agent_results.json."""

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "REQ-08 defect: harness crashes with KeyError 'expected' on the committed "
            "ground-truth files (case_01..case_10 use key 'requirements', not 'expected') "
            "on a clean checkout"
        ),
    )
    def test_req_08b_harness_writes_agent_results_json(self):
        """Run the harness with --heuristic and check agent_results.json is written."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "evaluation" / "run_evaluation.py"), "--heuristic"],
            capture_output=True, text=True,
            cwd=str(ROOT),
            env={**os.environ, "GOOGLE_API_KEY": "", "GEMINI_API_KEY": "",
                 "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        assert result.returncode == 0, (
            f"Harness exited with code {result.returncode}:\n{result.stderr}"
        )
        output_file = ROOT / "evaluation" / "agent_results.json"
        assert output_file.exists(), "evaluation/agent_results.json was not written"

    def test_req_08b_agent_results_is_valid_json(self):
        """evaluation/agent_results.json must be parseable as JSON."""
        output_file = ROOT / "evaluation" / "agent_results.json"
        if not output_file.exists():
            pytest.skip("agent_results.json not present")
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_req_08b_agent_results_contains_case_entries(self):
        """Each top-level key must contain evaluation metrics."""
        output_file = ROOT / "evaluation" / "agent_results.json"
        if not output_file.exists():
            pytest.skip("agent_results.json not present")
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert len(data) > 0
        for case_name, case_data in data.items():
            assert "evidence_accuracy" in case_data, (
                f"Case '{case_name}' missing 'evidence_accuracy' key"
            )


# ============================================================================
# REQ-08c — Harness writes evaluation/comparison.md
# ============================================================================

class TestReq08c:
    """REQ-08c: run_evaluation.py must write evaluation/comparison.md."""

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "REQ-08 defect: harness crashes with KeyError 'expected' on the committed "
            "ground-truth files (case_01..case_10 use key 'requirements', not 'expected') "
            "on a clean checkout"
        ),
    )
    def test_req_08c_harness_writes_comparison_md(self):
        """Run the harness with --heuristic and check comparison.md is written."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "evaluation" / "run_evaluation.py"), "--heuristic"],
            capture_output=True, text=True,
            cwd=str(ROOT),
            env={**os.environ, "GOOGLE_API_KEY": "", "GEMINI_API_KEY": "",
                 "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        assert result.returncode == 0, (
            f"Harness exited with code {result.returncode}:\n{result.stderr}"
        )
        output_file = ROOT / "evaluation" / "comparison.md"
        assert output_file.exists(), "evaluation/comparison.md was not written"

    def test_req_08c_comparison_md_is_markdown_table(self):
        """comparison.md must contain a markdown table with expected headers."""
        output_file = ROOT / "evaluation" / "comparison.md"
        if not output_file.exists():
            pytest.skip("comparison.md not present")
        content = output_file.read_text(encoding="utf-8")
        assert "| Case |" in content, "comparison.md must contain a markdown table"
        assert "accuracy" in content.lower(), "comparison.md must mention accuracy"


# ============================================================================
# REQ-09 — Human review dashboard: Confirm / Reject / Needs-review
# ============================================================================

class TestReq09:
    """REQ-09: The human-review mechanism must support all three decisions
    (confirm, reject, needs_review) and persist them onto verdicts."""

    def test_req_09_review_decision_type_has_all_three_values(self):
        """ReviewDecision literal must include 'confirm', 'reject', 'needs_review'."""
        # Verify by constructing objects with each value.
        for decision in ("confirm", "reject", "needs_review"):
            v = RequirementVerdict(requirement="Python", review=decision)
            assert v.review == decision

    def test_req_09_verdict_review_defaults_to_none(self):
        """A verdict with no reviewer decision must have review=None."""
        v = RequirementVerdict(requirement="Python")
        assert v.review is None

    def test_req_09_review_survives_serialisation(self):
        """review decision must be preserved through to_dict()."""
        for decision in ("confirm", "reject", "needs_review"):
            v = RequirementVerdict(requirement="Python", status="SUPPORTED", review=decision)
            d = v.to_dict()
            assert d["review"] == decision, (
                f"review='{decision}' was lost during to_dict()"
            )

    def test_req_09_review_persisted_on_evaluation_object(self):
        """Updating verdict.review must be visible on the parent CandidateEvaluation."""
        ev = CandidateEvaluation(
            verdicts=[
                RequirementVerdict(requirement="Python", status="SUPPORTED"),
                RequirementVerdict(requirement="FastAPI", status="NOT_FOUND"),
            ]
        )
        # Simulate dashboard action: recruiter confirms the first, rejects the second.
        ev.verdicts[0].review = "confirm"
        ev.verdicts[1].review = "reject"

        d = ev.to_dict()
        reviews = [v["review"] for v in d["verdicts"]]
        assert reviews[0] == "confirm"
        assert reviews[1] == "reject"

    def test_req_09_review_decision_schema_in_schemas_module(self):
        """ReviewDecision must be importable from ai.models.schemas."""
        from ai.models.schemas import ReviewDecision  # noqa: F401
        # If the import fails, the test fails — that's the whole point.


# ============================================================================
# REQ-10 — JSON export contains requirement, verdict, and reviewer decision
# ============================================================================

class TestReq10:
    """REQ-10: CandidateEvaluation.to_dict() must include requirement, status
    (verdict), and review (reviewer decision) for every verdict."""

    def _make_evaluation(self, review=None) -> CandidateEvaluation:
        return CandidateEvaluation(
            requirements=[Requirement(text="Python")],
            verdicts=[
                RequirementVerdict(
                    requirement="Python",
                    status="SUPPORTED",
                    evidence_quotes=["Built APIs with Python."],
                    review=review,
                )
            ],
            overall_coverage=100.0,
            summary="All requirements supported.",
            mode="gemini",
        )

    def test_req_10_to_dict_includes_requirement_field(self):
        """Each verdict dict must include the 'requirement' key."""
        d = self._make_evaluation().to_dict()
        assert len(d["verdicts"]) == 1
        assert "requirement" in d["verdicts"][0], "'requirement' key missing from verdict dict"

    def test_req_10_to_dict_includes_status_field(self):
        """Each verdict dict must include the 'status' key (the verdict)."""
        d = self._make_evaluation().to_dict()
        assert "status" in d["verdicts"][0], "'status' key missing from verdict dict"

    def test_req_10_to_dict_includes_review_field(self):
        """Each verdict dict must include the 'review' key (reviewer decision)."""
        d = self._make_evaluation(review="confirm").to_dict()
        assert "review" in d["verdicts"][0], "'review' key missing from verdict dict"

    def test_req_10_review_value_preserved_in_export(self):
        """The reviewer decision value must be preserved exactly in the export."""
        for decision in ("confirm", "reject", "needs_review"):
            d = self._make_evaluation(review=decision).to_dict()
            assert d["verdicts"][0]["review"] == decision

    def test_req_10_review_none_when_no_decision_made(self):
        """When no reviewer decision has been made, 'review' must be None."""
        d = self._make_evaluation(review=None).to_dict()
        assert d["verdicts"][0]["review"] is None

    def test_req_10_full_export_structure(self):
        """to_dict() must include top-level keys: overall_coverage, summary,
        mode, requirements, evidence, verdicts."""
        d = self._make_evaluation().to_dict()
        for key in ("overall_coverage", "summary", "mode", "requirements", "evidence", "verdicts"):
            assert key in d, f"top-level key '{key}' missing from to_dict() output"


# ============================================================================
# REQ-12 — Batch candidate ranking (PARTIAL)
# ============================================================================

class TestReq12:
    """REQ-12 (PARTIAL): Batch ranking must sort by verified-requirement
    coverage, not by an LLM-generated 0-100 score.

    The current implementation uses LLM score — this is a real defect.
    The test below documents the gap by inspecting the code behaviour.
    """

    def test_req_12_rank_candidates_function_exists(self):
        """rank_candidates() function must be defined in the Recruiter Dashboard."""
        source = (ROOT / "pages" / "5_📊_Recruiter_Dashboard.py").read_text(encoding="utf-8")
        assert "def rank_candidates(" in source, (
            "rank_candidates() function not found in pages/5_📊_Recruiter_Dashboard.py"
        )

    @pytest.mark.xfail(strict=True, reason="REQ-12 defect: rank_candidates() sorts by LLM score (0-100), not by verified-requirement coverage")
    def test_req_12_defect_ranking_by_llm_score_not_coverage(self):
        """PRD requirement (REQ-12): batch candidate ranking must sort by
        verified-requirement coverage, not by an LLM-generated 0-100 score.

        The dashboard currently sorts by r.get('score', 0) and never calls
        coverage_from_verdicts().  This test asserts the REQUIRED behaviour
        and is marked xfail until the defect is fixed.
        """
        source = (ROOT / "pages" / "5_📊_Recruiter_Dashboard.py").read_text(encoding="utf-8")
        # Required behaviour: sort key must use coverage, not a raw LLM score.
        assert "coverage_from_verdicts" in source, (
            "REQ-12: rank_candidates() must sort by verified-requirement coverage "
            "(coverage_from_verdicts()), not by an LLM-assigned score field."
        )
        # Confirm the old LLM-score sort is gone.
        assert 'r.get("score", 0)' not in source and "r.get('score', 0)" not in source, (
            "REQ-12: sorting by LLM score (r.get('score', 0)) must be replaced "
            "by a coverage-based sort."
        )

    def test_req_12_heuristic_evaluate_provides_coverage_metric(self):
        """heuristic_evaluate() produces an overall_coverage score that
        COULD be used for batch ranking — but the dashboard does not use it."""
        resume_a = "Python developer with extensive Python, FastAPI, Docker experience."
        resume_b = "Generalist developer."
        jd = "Requires Python, FastAPI, Docker."

        result_a = heuristic_evaluate(resume_a, jd)
        result_b = heuristic_evaluate(resume_b, jd)

        # Candidate A should have higher coverage.
        assert result_a.overall_coverage >= result_b.overall_coverage, (
            "Expected candidate A (with matching skills) to have >= coverage than candidate B"
        )
