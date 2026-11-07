from ai.models import RequirementVerdict
from evaluation.run_evaluation import aggregate, evaluate_case, render_table


def test_evaluate_case_counts_unmatched_predictions_and_requirements():
    verdicts = [
        RequirementVerdict(requirement="Python experience", status="SUPPORTED"),
        RequirementVerdict(requirement="Unlisted framework", status="SUPPORTED"),
    ]
    expected = [
        {"requirement": "Python experience", "status": "SUPPORTED"},
        {"requirement": "AWS experience", "status": "NOT_FOUND"},
    ]

    result = evaluate_case(verdicts, expected)

    assert result["aligned"] == 1
    assert result["total_predictions"] == 2
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["missed_requirements"] == ["AWS experience"]
    assert result["precision"] == 50.0
    assert result["recall"] == 50.0
    assert result["f1"] == 50.0
    assert result["evidence_accuracy"] == 100.0


def test_evaluate_case_preserves_aligned_status_error_metrics():
    verdicts = [
        RequirementVerdict(requirement="Python experience", status="SUPPORTED"),
        RequirementVerdict(requirement="AWS experience", status="NOT_FOUND"),
    ]
    expected = [
        {"requirement": "Python experience", "status": "NOT_FOUND"},
        {"requirement": "AWS experience", "status": "SUPPORTED"},
    ]

    result = evaluate_case(verdicts, expected)

    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["status_false_positives"] == 1
    assert result["status_false_negatives"] == 1
    assert result["evidence_accuracy"] == 0.0


def test_aggregate_uses_micro_requirement_precision_and_recall():
    results = {
        "case_a": evaluate_case(
            [RequirementVerdict(requirement="Python", status="SUPPORTED")],
            [
                {"requirement": "Python", "status": "SUPPORTED"},
                {"requirement": "AWS", "status": "NOT_FOUND"},
            ],
        ),
        "case_b": evaluate_case(
            [RequirementVerdict(requirement="Kubernetes", status="SUPPORTED")],
            [{"requirement": "Kubernetes", "status": "SUPPORTED"}],
        ),
    }

    summary = aggregate(results)

    assert summary["precision"] == 100.0
    assert summary["recall"] == 66.7
    assert summary["f1"] == 80.0
    assert summary["false_negatives_total"] == 1


def test_rendered_table_is_printable_in_windows_console_encoding():
    result = evaluate_case(
        [RequirementVerdict(requirement="Python", status="SUPPORTED")],
        [{"requirement": "Python", "status": "SUPPORTED"}],
    )

    render_table({"case": result}, {"case": result}).encode("cp1252")
