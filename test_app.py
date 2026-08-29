"""
Unit tests for ResumePilot AI core logic.

Run with:  pytest test_app.py -v

These tests cover the pure functions extracted from app.py so they
run without a Gemini API key, Streamlit runtime, or any other external
dependency.
"""

from app import (
    calculate_score,
    extract_section,
    evaluate_requirement_evidence,
    evaluate_requirement_set,
    extract_resume_evidence,
    verify_requirement_evidence,
    build_evidence_summary,
    get_runtime_api_key,
    select_free_port,
)


# ---------------------------------------------------------------------------
# Evidence-grounded requirement agent tests
# ---------------------------------------------------------------------------

def test_evaluate_requirement_evidence_supported_requirement():
    resume = "Built APIs in Python and FastAPI. Deployed PostgreSQL in production."
    result = evaluate_requirement_evidence(resume, "FastAPI")
    assert result["status"] == "supported"
    assert result["requirement"] == "FastAPI"


def test_evaluate_requirement_evidence_missing_requirement_is_unsupported():
    resume = "Built APIs in Python and FastAPI. Deployed PostgreSQL in production."
    result = evaluate_requirement_evidence(resume, "Kubernetes")
    assert result["status"] == "unsupported"


def test_evaluate_requirement_set_detects_false_positive_requirements():
    resume = "Python, FastAPI, PostgreSQL, Docker"
    job_requirements = ["Python", "FastAPI", "PostgreSQL", "AWS", "Kubernetes", "Docker"]
    results = evaluate_requirement_set(resume, job_requirements)
    statuses = {item["requirement"]: item["status"] for item in results}
    assert statuses["Python"] == "supported"
    assert statuses["FastAPI"] == "supported"
    assert statuses["PostgreSQL"] == "supported"
    assert statuses["Docker"] == "supported"
    assert statuses["AWS"] == "unsupported"
    assert statuses["Kubernetes"] == "unsupported"


def test_extract_resume_evidence_returns_structured_evidence():
    resume = """Senior Software Engineer\n\nBuilt APIs with Python and FastAPI.\nDeployed PostgreSQL services on AWS and Docker.\nBachelor's degree in Computer Science."""
    evidence = extract_resume_evidence(resume)
    assert any(item["skill"] == "Python" and item["source"] == "Projects" for item in evidence)
    assert any(item["skill"] == "FastAPI" and item["confidence"] == "high" for item in evidence)
    assert any(item["skill"] == "AWS" and item["source"] == "Experience" for item in evidence)
    assert any(item["skill"] == "Bachelor's degree" and item["source"] == "Education" for item in evidence)


def test_verify_requirement_evidence_classifies_supported_and_unverified():
    resume = "Built APIs with Python and FastAPI; deployed PostgreSQL services on Docker and cloud infrastructure."
    supported = verify_requirement_evidence(resume, "Python")
    unverified = verify_requirement_evidence(resume, "Kubernetes")
    partial = verify_requirement_evidence(resume, "AWS")

    assert supported["status"] == "supported"
    assert supported["evidence_found"]
    assert unverified["status"] == "not_verified"
    assert partial["status"] == "partially_supported"


def test_build_evidence_summary_sets_dashboard_metrics():
    resume = "Built APIs with Python and FastAPI; deployed PostgreSQL services on Docker and cloud infrastructure."
    summary = build_evidence_summary(
        resume,
        ["Python", "FastAPI", "AWS", "Kubernetes"],
        candidate_name="Example Candidate",
        position_name="Backend Engineer",
    )

    assert summary["candidate"] == "Example Candidate"
    assert summary["position"] == "Backend Engineer"
    assert summary["overall_coverage"] >= 50
    statuses = {item["requirement"]: item["status"] for item in summary["requirements"]}
    assert statuses["Python"] == "supported"
    assert statuses["FastAPI"] == "supported"
    assert statuses["AWS"] == "partially_supported"
    assert statuses["Kubernetes"] == "not_verified"


# ---------------------------------------------------------------------------
# calculate_score tests
# ---------------------------------------------------------------------------

def test_get_runtime_api_key_supports_environment_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-test-key")
    assert get_runtime_api_key() == "env-test-key"


def test_select_free_port_returns_valid_port():
    port = select_free_port(8765)
    assert isinstance(port, int)
    assert 1 <= port <= 65535


def test_score_empty_resume():
    assert calculate_score("", "Python developer") == 0


def test_score_empty_jd():
    assert calculate_score("Python experience", "") == 0


def test_score_both_empty():
    assert calculate_score("", "") == 0


def test_score_no_match():
    score = calculate_score("I like cooking", "Python Django React")
    assert score == 0  # no overlap at all


def test_score_perfect_match():
    score = calculate_score("Python Django React", "Python Django React")
    # 3/3 = 100% → with no boost
    assert score == 100


def test_score_partial_match():
    score = calculate_score("Python Java", "Python Django React")
    # 1 out of 3 keywords matched → 33% (no boost)
    assert score == 33


def test_score_with_boost():
    score = calculate_score("Python", "Python Django", boost=20)
    # 1/2 = 50 + 20 = 70
    assert score == 70


def test_score_boost_caps_at_100():
    score = calculate_score("Python Django", "Python Django React", boost=80)
    # 2/3 = 66 + 80 = 146 → capped at 100
    assert score == 100


def test_score_case_insensitive():
    score = calculate_score("python", "PYTHON")
    assert score == 100


def test_score_punctuation_handling():
    score = calculate_score("Python, Java, and SQL", "Python Java SQL")
    # "Python," (with comma) ≠ "Python" — this is expected because
    # split() keeps punctuation.  Real analysis should use the AI pass.
    assert score > 0  # at least "and" and "Java" may match loosely


# ---------------------------------------------------------------------------
# extract_section tests
# ---------------------------------------------------------------------------

SAMPLE_TEXT = """### RESUME SUMMARY
A skilled developer with 5 years of experience.

### CORE STRENGTHS
- Python
- Django

### CRITICAL WEAKNESSES
- Missing cloud experience

### INTERVIEW PREPARATION
Q1: Tell me about yourself...
"""


def test_extract_section_found():
    result = extract_section(SAMPLE_TEXT, "### RESUME SUMMARY", "### CORE STRENGTHS")
    assert "skilled developer" in result
    assert "### CORE STRENGTHS" not in result


def test_extract_section_to_end():
    result = extract_section(SAMPLE_TEXT, "### INTERVIEW PREPARATION")
    assert "Q1:" in result


def test_extract_section_missing_header():
    result = extract_section(SAMPLE_TEXT, "### NONEXISTENT HEADER")
    assert "mismatched" in result


def test_extract_section_strips_whitespace():
    result = extract_section(SAMPLE_TEXT, "### RESUME SUMMARY", "### CORE STRENGTHS")
    assert result == result.strip()
    assert not result.startswith("\n")
    assert not result.endswith("\n")


def test_extract_section_respects_boundary():
    result = extract_section(SAMPLE_TEXT, "### CORE STRENGTHS", "### CRITICAL WEAKNESSES")
    assert "Python" in result
    assert "cloud" not in result


# ---------------------------------------------------------------------------
# Integration-style: edge cases for combined logic
# ---------------------------------------------------------------------------

def test_score_and_extract_no_crash():
    """Prove the two main helpers can be called in sequence safely."""
    score = calculate_score("Python developer", "Python senior developer")
    section = extract_section(SAMPLE_TEXT, "### RESUME SUMMARY", "### CORE STRENGTHS")
    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert isinstance(section, str)
    assert len(section) > 10