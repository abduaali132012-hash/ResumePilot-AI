# Evaluation Suite

This folder holds the controlled experiment used to compare the baseline ResumePilot evaluator with the evidence-based requirement evaluator.

## Structure

- `cases/` — curated resume/job pairs and expected evidence labels
- `baseline_results.json` — output produced by the original baseline system
- `agent_results.json` — output produced by the evidence-based system

## Purpose

Each case contains the same inputs for both systems:
- `job_description.txt`
- `candidate_resume.txt`
- `expected_evidence.json`

The same case set is used to compare the two systems fairly and to measure whether the evidence-based pipeline improves requirement accuracy.

## Metric

Primary metric:
- Evidence-grounded requirement accuracy

Measurement:
- Compare model output against `expected_evidence.json`
- Count correctly classified requirements across the case set
- Track false positives and false negatives separately

## Recommended workflow

1. Write a case with a known requirement set and gold labels.
2. Run the baseline evaluator on the case.
3. Run the evidence-based evaluator on the same case.
4. Compare each result to the expected evidence.
5. Store the JSON outcomes in `baseline_results.json` and `agent_results.json`.
