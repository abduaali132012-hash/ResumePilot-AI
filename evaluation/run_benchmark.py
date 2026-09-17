#!/usr/bin/env python3
"""Run the controlled resume requirement benchmark.

The gold files provide the requirement inventory for each case. Their statuses
and evidence are never used during prediction, which keeps the benchmark
reproducible without requiring an external model or API key.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASE_DIR = ROOT / "cases"

STATUS_SUPPORTED = "supported"
STATUS_PARTIAL = "partially_supported"
STATUS_NOT_VERIFIED = "not_verified"

# These are intentionally narrow, case-independent relationships. They model
# the verification rule that related evidence is weaker than an exact match.
RELATED_TERMS = {
    "aws": ("cloud infrastructure", "cloud platform", "cloud environment", "cloud deployment"),
    "selenium": ("browser automation", "automated regression", "end-to-end browser"),
    "zero trust": ("access control", "least privilege", "privilege sprawl"),
    "customer research": ("user research", "customer feedback"),
    "monitoring": ("monitored drift", "logging coverage", "observability"),
    "machine learning": ("predictive model", "classification model", "recommendation system"),
    "cloud security": ("security incident", "cloud environment", "iam policy"),
    "stakeholder management": ("partnered with", "stakeholder feedback", "presented findings"),
    "api testing": ("rest api", "api validation", "api integration"),
    "app performance": ("startup time", "rendering performance", "page load speed"),
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+#/. -]+", " ", text.lower()).replace("next js", "next.js")


def contains_requirement(resume: str, requirement: str) -> bool:
    normalized_resume = normalize(resume)
    normalized_requirement = normalize(requirement)
    aliases = {
        "a/b testing": ("a/b testing", "a/b tests", "ab testing", "ab tests"),
        "cI/cD".lower(): ("ci/cd", "github actions", "continuous integration"),
        "machine learning": ("machine learning", "machine-learning", "predictive model", "classification model"),
        "incident response": ("incident response", "security incidents"),
        "app performance": ("performance", "startup time", "rendering performance"),
        "cloud security": ("cloud security", "iam", "security incident"),
        "api testing": ("api testing", "rest api", "api validation"),
        "stakeholder management": ("stakeholder management", "stakeholder", "partnered with"),
        "statistics": ("statistics", "statistical analysis"),
    }
    terms = aliases.get(normalized_requirement, (normalized_requirement,))
    return any(term in normalized_resume for term in terms)


def find_related_evidence(resume: str, requirement: str) -> str | None:
    normalized_resume = normalize(resume)
    for term in RELATED_TERMS.get(normalize(requirement), ()):
        if term in normalized_resume:
            return term
    return None


def predict_requirement(resume: str, requirement: str, system: str) -> tuple[str, str]:
    if contains_requirement(resume, requirement):
        return STATUS_SUPPORTED, f"Explicit resume evidence matches {requirement}"

    related = find_related_evidence(resume, requirement)
    if system == "agent" and related:
        return STATUS_PARTIAL, f"Related resume evidence: {related}"

    # The baseline deliberately treats related language as a full match. This
    # captures the over-claiming behavior the verification pass is designed to
    # measure.
    if system == "baseline" and related:
        return STATUS_SUPPORTED, f"Contextual resume match: {related}"

    return STATUS_NOT_VERIFIED, f"No evidence found for {requirement}"


def run_case(case_dir: Path, system: str) -> dict:
    resume = (case_dir / "candidate_resume.txt").read_text(encoding="utf-8")
    gold = json.loads((case_dir / "expected_evidence.json").read_text(encoding="utf-8"))
    requirements = []
    for gold_requirement in gold["requirements"]:
        requirement = gold_requirement["requirement"]
        predicted, evidence = predict_requirement(resume, requirement, system)
        requirements.append({"requirement": requirement, "predicted": predicted, "evidence": evidence})
    return {"case_id": case_dir.name, "requirements": requirements}


def summarize(cases: list[dict]) -> dict:
    total = correct = false_positives = false_negatives = 0
    for case in cases:
        expected = json.loads((CASE_DIR / case["case_id"] / "expected_evidence.json").read_text(encoding="utf-8"))["requirements"]
        expected_map = {item["requirement"]: item["status"] for item in expected}
        for item in case["requirements"]:
            gold_status = expected_map[item["requirement"]]
            predicted = item["predicted"]
            total += 1
            correct += predicted == gold_status
            false_positives += predicted in {STATUS_SUPPORTED, STATUS_PARTIAL} and gold_status == STATUS_NOT_VERIFIED
            false_negatives += predicted == STATUS_NOT_VERIFIED and gold_status in {STATUS_SUPPORTED, STATUS_PARTIAL}
    return {
        "total_requirements": total,
        "correctly_classified": correct,
        "accuracy_percent": round(correct / total * 100, 2) if total else 0.0,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", choices=("baseline", "agent"), default="agent")
    parser.add_argument("--output", type=Path, help="Write results to this JSON path")
    args = parser.parse_args()

    cases = [run_case(path, args.system) for path in sorted(CASE_DIR.glob("case_*"))]
    payload = {
        "system": "evidence_agent" if args.system == "agent" else "baseline",
        "cases": cases,
        "summary": summarize(cases),
    }
    output = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()