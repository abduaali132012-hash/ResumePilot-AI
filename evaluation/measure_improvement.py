#!/usr/bin/env python3
"""Compute the evaluation improvement between baseline and evidence-agent outputs.

This file reads the persisted benchmark results from evaluation/baseline_results.json
and evaluation/agent_results.json, compares each predicted requirement status to the
expected status stored in each case's expected_evidence.json file, and prints a
comparison table. It never invents numbers; it only reports metrics derived from the
actual JSON test artifacts in this repository.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASE_DIR = ROOT / "cases"
BASELINE_PATH = ROOT / "baseline_results.json"
AGENT_PATH = ROOT / "agent_results.json"


def load_expected(case_id: str):
    path = CASE_DIR / case_id / "expected_evidence.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["requirements"]


def compute_case_accuracy(expected_requirements, predicted_requirements):
    expected_map = {req["requirement"]: req["status"] for req in expected_requirements}
    correct = 0
    total = len(expected_map)
    fp = 0
    fn = 0

    for req in predicted_requirements:
        requirement = req["requirement"]
        expected = expected_map.get(requirement)
        if expected is None:
            continue
        predicted = req["predicted"]
        if expected == predicted:
            correct += 1
        if predicted in {"supported", "partially_supported"} and expected == "not_verified":
            fp += 1
        if expected in {"supported", "partially_supported"} and predicted == "not_verified":
            fn += 1

    accuracy = (correct / total * 100.0) if total else 0.0
    return accuracy, fp, fn


def compute_system_metrics(system_payload):
    total_requirements = 0
    correct = 0
    false_positives = 0
    false_negatives = 0

    for case in system_payload["cases"]:
        case_id = case["case_id"]
        expected = load_expected(case_id)
        accuracy, fp, fn = compute_case_accuracy(expected, case["requirements"])
        total_requirements += len(expected)
        correct += int(round((accuracy / 100.0) * len(expected)))
        false_positives += fp
        false_negatives += fn

    overall_accuracy = (correct / total_requirements * 100.0) if total_requirements else 0.0
    return {
        "total_requirements": total_requirements,
        "correctly_classified": correct,
        "accuracy_percent": round(overall_accuracy, 2),
        "false_positives": false_positives,
        "false_negatives": false_negatives,
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
