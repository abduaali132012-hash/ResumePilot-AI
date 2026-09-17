import json
from pathlib import Path

from evaluation.run_benchmark import (
    CASE_DIR,
    STATUS_NOT_VERIFIED,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    contains_requirement,
    find_related_evidence,
    run_case,
    summarize,
)


def test_benchmark_contains_ten_cases():
    assert len(list(CASE_DIR.glob("case_*"))) == 10


def test_agent_predictions_match_gold_labels():
    cases = [run_case(path, "agent") for path in sorted(CASE_DIR.glob("case_*"))]
    summary = summarize(cases)
    assert summary["total_requirements"] == 51
    assert summary["correctly_classified"] == 51
    assert summary["accuracy_percent"] == 100.0


def test_explicit_requirement_is_supported():
    assert contains_requirement("Built APIs with Python and FastAPI", "Python")


def test_related_requirement_is_partial_for_agent():
    resume = "Worked with cloud infrastructure and deployment workflows"
    assert find_related_evidence(resume, "AWS") == "cloud infrastructure"
    assert run_case(CASE_DIR / "case_01", "agent")["requirements"][5]["predicted"] == STATUS_PARTIAL


def test_related_requirement_is_overclaimed_by_baseline():
    result = run_case(CASE_DIR / "case_01", "baseline")
    assert result["requirements"][5]["predicted"] == STATUS_SUPPORTED


def test_unverified_requirement_has_no_evidence():
    result = run_case(CASE_DIR / "case_01", "agent")
    kubernetes = next(item for item in result["requirements"] if item["requirement"] == "Kubernetes")
    assert kubernetes["predicted"] == STATUS_NOT_VERIFIED


if __name__ == "__main__":
    json.dumps({"cases": len(list(Path(CASE_DIR).glob("case_*")))})
