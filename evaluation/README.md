# Evaluation Suite — Baseline vs. Agent

This folder measures the *real* improvement of the Evidence-Based Candidate
Evaluation agent over the single-pass baseline that ResumePilot had before the
Micro1 (Frontier Engineering Challenge 2026) work.

We never invent numbers. Every figure in `baseline_results.json`,
`agent_results.json`, and `comparison.md` comes from actually running the two
systems on the controlled cases below.

## Structure

```
evaluation/
├── README.md
├── run_evaluation.py          # the harness
├── baseline_results.json      # written by the harness
├── agent_results.json         # written by the harness
├── comparison.md              # markdown table written by the harness
└── cases/
    ├── case_01_backend_engineer/
    │   ├── job_description.txt
    │   ├── candidate_resume.txt
    │   └── expected_evidence.json      # HUMAN-labelled ground truth
    ├── case_02_data_analyst/
    └── case_03_frontend_engineer/
```

Each case is deliberately written to contain **traps** that single-pass
evaluators get wrong — e.g. "cloud experience" that is not AWS, a skill listed
without usage context, an absent requirement the model might hallucinate into
a SUPPORTED. That is what makes the comparison meaningful.

## How to run

From the repo root, with `GOOGLE_API_KEY` set in the environment:

```bash
pip install -r requirements.txt
python evaluation/run_evaluation.py
```

No key handy? The harness still works in deterministic mode (both systems fall
back to the keyword evaluator) — useful as a wiring smoke test, but it will not
measure the real agent:

```bash
python evaluation/run_evaluation.py --heuristic
```

## Metrics

- **Evidence accuracy** — % of human-labelled requirements whose verdict the
  system got right.
- **False positives** — requirements the system claimed were `SUPPORTED` when
  the resume has no real evidence (the failure mode this project exists to fix).
- **False negatives** — supported requirements the system missed.

## Adding a case

1. `mkdir evaluation/cases/case_XX_<name>`
2. Add `job_description.txt` and `candidate_resume.txt`.
3. Hand-label `expected_evidence.json` with the ground-truth status for each
   requirement (`SUPPORTED` / `PARTIALLY_SUPPORTED` / `NOT_VERIFIED` /
   `NOT_FOUND`), quoting the exact resume line that supports the label.

The same cases feed both the baseline and the agent, so the comparison is
always apples-to-apples.
