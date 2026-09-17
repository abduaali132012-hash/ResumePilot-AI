import json
from pathlib import Path

from evaluation.run_evaluation import CASES_DIR, aggregate, evaluate_case
from ai.pipeline import heuristic_evaluate


CASE_DIRS = sorted(
    path for path in CASES_DIR.iterdir() if path.is_dir() and path.name.count("_") >= 2
)


def load_expected(case_dir):
    return json.loads((case_dir / "expected_evidence.json").read_text())["expected"]


def test_harness_contains_ten_named_cases():
    assert len(CASE_DIRS) == 10


def test_heuristic_evaluator_returns_verdicts():
    case_dir = CASE_DIRS[0]
    evaluation = heuristic_evaluate(
        (case_dir / "candidate_resume.txt").read_text(),
        (case_dir / "job_description.txt").read_text(),
    )
    assert evaluation.verdicts


def test_case_metrics_align_expected_requirements():
    case_dir = CASE_DIRS[0]
    evaluation = heuristic_evaluate(
        (case_dir / "candidate_resume.txt").read_text(),
        (case_dir / "job_description.txt").read_text(),
    )
    result = evaluate_case(evaluation.verdicts, load_expected(case_dir))
    assert result["aligned"] <= result["total_expected"]


def test_case_metrics_include_accuracy():
    case_dir = CASE_DIRS[1]
    evaluation = heuristic_evaluate(
        (case_dir / "candidate_resume.txt").read_text(),
        (case_dir / "job_description.txt").read_text(),
    )
    result = evaluate_case(evaluation.verdicts, load_expected(case_dir))
    assert 0.0 <= result["evidence_accuracy"] <= 100.0


def test_aggregate_sums_expected_requirements():
    results = {"case": {"evidence_accuracy": 50.0, "false_positives": 1, "false_negatives": 2, "aligned": 2, "total_expected": 4}}
    summary = aggregate(results)
    assert summary["expected_total"] == 4
    assert summary["false_positives_total"] == 1


def test_aggregate_handles_empty_results():
    summary = aggregate({})
    assert summary["evidence_accuracy_avg"] == 0.0
    assert summary["expected_total"] == 0
