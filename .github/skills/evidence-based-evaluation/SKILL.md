---
name: evidence-based-evaluation
description: "Use when: evaluating a resume against a job description, comparing a baseline model to an evidence-based pipeline, reducing false-positive requirement matches, and documenting benchmark results with explicit proof." 
---

# Evidence-Based Evaluation

## Purpose

Use this workflow when you need to judge whether a resume genuinely satisfies a job requirement, not just whether the wording feels similar. The goal is to produce an explainable, defensible evaluation with explicit evidence and a verification layer that reduces over-claiming.

## Core workflow

### 1. Analyze the repo and locate the evaluation flow
- Start by mapping the project structure and identifying where the resume/job evaluation logic lives.
- Look for the app entry points, benchmark folders, gold-truth case files, and any existing experiment notes.
- Confirm whether the repo already contains the idea of evaluation but lacks the concrete benchmark or consistent taxonomy.
- Write a short repository summary that states the likely root cause and the most relevant files.

### 2. Establish a baseline before improvement
- Create a simple evaluator that checks requirement support in one pass.
- Keep the logic intentionally lightweight so you can compare it against the improved pipeline.
- Look for common failure modes: vague similarity, indirect references, broad contextual overlap, or overconfident labels.
- Record the baseline metrics: accuracy, false positives, and false negatives.

### 3. Add evidence extraction
- For each requirement, identify the exact resume sentence, phrase, or near-explicit wording that supports the claim.
- Require a concrete textual anchor before classifying a requirement as supported.
- Separate raw contextual similarity from direct proof.
- Track whether the evidence is explicit, weak, or absent.

### 4. Add a verification pass
- Distinguish between supported, partially supported, and not verified outcomes.
- Do not treat indirect or ambiguous language as full support.
- Gate full support behind sufficiently direct evidence.
- Review edge cases such as domain terms, frameworks, research, and tooling that are easy to over-claim.

### 5. Evaluate rigorously against a fixed benchmark
- Use the same curated case set for both the baseline and the improved system.
- Add gold-truth expected evidence for each requirement.
- Measure:
  - evidence accuracy
  - false-positive claims
  - false-negative misses
- Compare before/after numbers and summarize the improvement.

## Decision points

- If the resume only implies a skill without explicit proof, classify as partially supported or not verified rather than fully supported.
- If the system is producing broad claims from generic job-language overlap, add evidence extraction before making a final decision.
- If the benchmark still overstates certainty after evidence extraction, add a verification stage.
- If the benchmark is using different cases across runs, fix the evaluation set so the comparison is valid.

## Quality criteria

A good result should:
- rely on explicit or near-explicit resume evidence
- minimize false positives
- avoid claiming support without proof
- produce explainable labels rather than vague confidence
- show a clear before/after improvement with measured metrics

## Completion checklist

Before concluding the evaluation is complete, verify that:
- the project flow is mapped and documented
- baseline metrics were recorded
- evidence extraction is grounded in actual resume text
- the verification pass filters ambiguous claims
- the benchmark uses the same cases for both systems
- the final comparison reports accuracy and error counts clearly

## Example prompts

- "Analyze this repository and identify the evaluation flow for resume-to-job matching."
- "Build a baseline evaluator for requirement coverage and report its failure modes."
- "Add evidence extraction so each requirement is justified by resume text before final classification."
- "Introduce a verification pass that distinguishes fully supported vs partially supported vs not verified."
- "Run a benchmark comparing the baseline and the evidence pipeline and summarize the metric improvements."

## Related customizations

- A repository-analysis skill for mapping code structure and identifying the right experiment surfaces.
- A benchmark-validation skill for verifying that expected outputs, gold labels, and scoring logic remain consistent.
- A quality-gates skill for checking false positives, false negatives, and reasoning quality before shipping an evaluator.
