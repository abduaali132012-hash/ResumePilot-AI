#!/usr/bin/env python3
"""Compute the evaluation improvement between baseline and evidence-agent outputs.

This file reads per-case metrics persisted by run_evaluation.py and prints an
aggregate comparison. It uses the same per-case accuracy measure as the evaluation
harness instead of trying to realign already-aligned verdicts.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE_PATH = ROOT / "baseline_results.json"
AGENT_PATH = ROOT / "agent_results.json"


def compute_system_metrics(system_payload):
    if not isinstance(system_payload, dict) or not system_payload:
        raise ValueError("Evaluation results must be a non-empty per-case object.")

    case_results = list(system_payload.items())
    required_fields = {
        "evidence_accuracy",
        "total_expected",
        "correct",
        "false_positives",
        "false_negatives",
    }
    for case_id, result in case_results:
        if not isinstance(result, dict) or not required_fields.issubset(result):
            raise ValueError(f"{case_id}: evaluation result is missing required metrics.")

    return {
        "total_requirements": sum(result["total_expected"] for _, result in case_results),
        "correctly_classified": sum(result["correct"] for _, result in case_results),
        "accuracy_percent": round(
            sum(result["evidence_accuracy"] for _, result in case_results)
            / len(case_results),
            2,
        ),
        "false_positives": sum(result["false_positives"] for _, result in case_results),
        "false_negatives": sum(result["false_negatives"] for _, result in case_results),
    }


def format_accuracy_row(label, baseline, agent, improvement):
    return f"| {label:<32} | {baseline:>7.2f}% | {agent:>7.2f}% | {improvement:>+8.2f}% |"


def format_count_row(label, baseline, agent, improvement):
    return f"| {label:<32} | {baseline:>7} | {agent:>7} | {improvement:>+8} |"


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    agent = json.loads(AGENT_PATH.read_text(encoding="utf-8"))

    baseline_metrics = compute_system_metrics(baseline)
    agent_metrics = compute_system_metrics(agent)

    evidence_accuracy_delta = agent_metrics["accuracy_percent"] - baseline_metrics["accuracy_percent"]
    fp_delta = baseline_metrics["false_positives"] - agent_metrics["false_positives"]
    fn_delta = baseline_metrics["false_negatives"] - agent_metrics["false_negatives"]

    print("Evaluation comparison")
    print("====================")
    print(f"Baseline accuracy: {baseline_metrics['accuracy_percent']:.2f}%")
    print(f"Agent accuracy:    {agent_metrics['accuracy_percent']:.2f}%")
    print(f"Improvement:       {evidence_accuracy_delta:+.2f} percentage points")
    print()
    print("| Metric                             | Baseline | Agent | Improvement |")
    print("| ---------------------------------- | -------: | ----: | ----------: |")
    print(format_accuracy_row("Evidence accuracy", baseline_metrics["accuracy_percent"], agent_metrics["accuracy_percent"], evidence_accuracy_delta))
    print(format_count_row("False-positive claims", baseline_metrics["false_positives"], agent_metrics["false_positives"], fp_delta))
    print(format_count_row("False-negative misses", baseline_metrics["false_negatives"], agent_metrics["false_negatives"], fn_delta))

    print()
    print("Raw numbers:")
    print(json.dumps({
        "baseline": baseline_metrics,
        "agent": agent_metrics,
        "improvement": {
            "evidence_accuracy_percentage_points": round(evidence_accuracy_delta, 2),
            "false_positive_reduction": fp_delta,
            "false_negative_reduction": fn_delta,
        },
    }, indent=2))


if __name__ == "__main__":
    main()
