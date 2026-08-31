#!/usr/bin/env python3
"""
Evaluation harness for the Evidence-Based Candidate Evaluation agent.

Measures, on a controlled set of cases, how the agentic pipeline (Requirement
Extraction → Evidence Extraction → Matching → Verification) compares to the
single-pass baseline that ResumePilot had before the Micro1 work.

Usage (from the repo root):

    # Full run — needs GOOGLE_API_KEY / GEMINI_API_KEY in the environment:
    python evaluation/run_evaluation.py

    # Deterministic-only run (no API key required), for a quick smoke test:
    python evaluation/run_evaluation.py --heuristic

Outputs:
    evaluation/baseline_results.json
    evaluation/agent_results.json
    evaluation/comparison.md     (markdown table for the changelog)
    (prints the same table to stdout)

Metrics (all computed from REAL runs — we never invent numbers):
    evidence_accuracy      % of requirements whose verdict matches the
                           human-labelled expected status
    false_positives        predicted SUPPORTED but actually missing/weak
    false_negatives        predicted missing but actually supported
    aligned / total        how many expected requirements could be compared
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.inference import GeminiClient, get_api_key  # noqa: E402
from ai.models import CandidateEvaluation, RequirementVerdict  # noqa: E402
from ai.pipeline import baseline_evaluate, heuristic_evaluate, run_candidate_evaluation  # noqa: E402

CASES_DIR = Path(__file__).resolve().parent / "cases"

VALID_STATUSES = {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"}


# --------------------------------------------------------------------------- #
# Alignment: match a model verdict string to an expected requirement string.
# --------------------------------------------------------------------------- #
_STOP = {
    "the", "of", "for", "with", "to", "in", "on", "at", "and", "or", "a", "an",
    "experience", "knowledge", "strong", "good", "working", "work", "years",
    "plus", "required", "preferred", "skills", "skill",
}


def _tokens(text: str) -> set[str]:
    return {
        w for w in re.split(r"[^a-z0-9+#.-]+", text.lower())
        if w and w not in _STOP and len(w) > 1
    }


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a)


def align(verdicts: list[RequirementVerdict], expected: list[dict]) -> list[tuple]:
    """Return (verdict, expected_dict_or_None, score) pairs aligned by text overlap."""
    aligned: list[tuple] = []
    used: set[int] = set()
    for v in verdicts:
        v_tokens = _tokens(v.requirement)
        best_i, best_score = -1, 0.0
        for i, exp in enumerate(expected):
            if i in used:
                continue
            score = _overlap(v_tokens, _tokens(exp["requirement"]))
            if score > best_score:
                best_i, best_score = i, score
        if best_i != -1 and best_score >= 0.5:
            used.add(best_i)
            aligned.append((v, expected[best_i], best_score))
        else:
            aligned.append((v, None, best_score))
    return aligned


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def evaluate_case(verdicts: list[RequirementVerdict], expected: list[dict]) -> dict:
    aligned = align(verdicts, expected)
    compared = [(v, e) for v, e, _ in aligned if e]
    correct = sum(1 for v, e in compared if v.status == e["status"])

    false_positives = sum(
        1
        for v, e in compared
        if v.status == "SUPPORTED" and e["status"] in {"NOT_FOUND", "NOT_VERIFIED"}
    )
    false_negatives = sum(
        1
        for v, e in compared
        if v.status in {"NOT_FOUND", "NOT_VERIFIED"} and e["status"] == "SUPPORTED"
    )

    detail = []
    for v, e, score in aligned:
        detail.append(
            {
                "predicted_requirement": v.requirement,
                "status": v.status,
                "expected_requirement": e["requirement"] if e else None,
                "expected_status": e["status"] if e else None,
                "correct": bool(e and v.status == e["status"]),
                "evidence_quotes": v.evidence_quotes,
            }
        )

    return {
        "aligned": len(compared),
        "total_expected": len(expected),
        "correct": correct,
        "evidence_accuracy": round(correct / len(compared) * 100, 1) if compared else 0.0,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "detail": detail,
    }


def aggregate(results: dict[str, dict]) -> dict:
    acc, fp, fn, aligned, total = 0.0, 0, 0, 0, 0
    for r in results.values():
        acc += r["evidence_accuracy"]
        fp += r["false_positives"]
        fn += r["false_negatives"]
        aligned += r["aligned"]
        total += r["total_expected"]
    n = len(results) or 1
    return {
        "evidence_accuracy_avg": round(acc / n, 1),
        "false_positives_total": fp,
        "false_negatives_total": fn,
        "aligned_total": aligned,
        "expected_total": total,
    }


def render_table(baseline: dict, agent: dict) -> str:
    lines = [
        "| Case | Baseline accuracy | Agent accuracy | Δ | FP (base→agent) |",
        "|------|------------------:|---------------:|:--:|:---:|",
    ]
    for case in baseline:
        b = baseline[case]
        a = agent.get(case, {})
        delta = a.get("evidence_accuracy", 0) - b.get("evidence_accuracy", 0)
        lines.append(
            f"| {case} | {b.get('evidence_accuracy', 0)}% | "
            f"{a.get('evidence_accuracy', 0)}% | {delta:+.1f}pp | "
            f"{b.get('false_positives', 0)} → {a.get('false_positives', 0)} |"
        )
    ba, aa = aggregate(baseline), aggregate(agent)
    lines.append(
        f"| **Aggregate** | **{ba['evidence_accuracy_avg']}%** | "
        f"**{aa['evidence_accuracy_avg']}%** | "
        f"**{aa['evidence_accuracy_avg'] - ba['evidence_accuracy_avg']:+.1f}pp** | "
        f"**{ba['false_positives_total']} → {aa['false_positives_total']}** |"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the candidate-evaluation agent vs baseline.")
    parser.add_argument(
        "--heuristic",
        action="store_true",
        help="Use only the deterministic evaluator (no API key needed).",
    )
    args = parser.parse_args()

    cases = sorted(
        [d for d in CASES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )
    if not cases:
        print("No cases found under evaluation/cases/. Add case folders first.")
        return 1

    client = GeminiClient()
    use_agent = client.available and not args.heuristic
    if args.heuristic:
        print("Running in --heuristic mode (deterministic evaluator only).")
    elif not client.available:
        print(
            "WARNING: no GOOGLE_API_KEY / GEMINI_API_KEY found in the environment. "
            "Running BOTH systems with the deterministic fallback so the harness still "
            "produces numbers. Set the key to measure the real agent."
        )

    baseline_results: dict[str, dict] = {}
    agent_results: dict[str, dict] = {}

    for case_dir in cases:
        case_name = case_dir.name
        jd = (case_dir / "job_description.txt").read_text(encoding="utf-8")
        resume = (case_dir / "candidate_resume.txt").read_text(encoding="utf-8")
        expected = json.loads((case_dir / "expected_evidence.json").read_text(encoding="utf-8"))["expected"]
        print(f"\n=== {case_name} ===")

        # Baseline: single-pass evaluation.
        if use_agent:
            base_ev = baseline_evaluate(client, resume, jd)
        else:
            base_ev = heuristic_evaluate(resume, jd)
        baseline_results[case_name] = evaluate_case(base_ev.verdicts, expected)
        print(f"  baseline accuracy: {baseline_results[case_name]['evidence_accuracy']}%")

        # Agent: evidence-based pipeline.
        if use_agent:
            agent_ev = run_candidate_evaluation(resume, jd, client=client)
        else:
            agent_ev = heuristic_evaluate(resume, jd)
        agent_results[case_name] = evaluate_case(agent_ev.verdicts, expected)
        print(f"  agent accuracy:    {agent_results[case_name]['evidence_accuracy']}%")

    table = render_table(baseline_results, agent_results)
    print("\n" + table)

    # Persist everything.
    out = Path(__file__).resolve().parent
    (out / "baseline_results.json").write_text(
        json.dumps(baseline_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "agent_results.json").write_text(
        json.dumps(agent_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "comparison.md").write_text(
        f"# Baseline vs Agent comparison\n\n{table}\n\n"
        f"_Generated by `python evaluation/run_evaluation.py`"
        f"{' --heuristic' if not use_agent else ''}._\n",
        encoding="utf-8",
    )
    print(f"\nWrote baseline_results.json, agent_results.json, comparison.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
