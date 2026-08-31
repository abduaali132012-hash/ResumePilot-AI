# Improvement Changelog — Evidence-Based Candidate Evaluation

This log documents the *experiments* performed for the Frontier Engineering
Challenge 2026 (Micro1). It is the engineering story behind the project: what
we observed, what we tried, and — with real measured numbers — whether it worked.

> **Integrity rule: we never invent numbers.** Every "Result" below comes from
> an actual `python evaluation/run_evaluation.py` run. Where a number is not yet
> available because it requires a real Gemini key, it is explicitly labelled
> **"pending real run"** — we would rather show an honest gap than a fabricated
> improvement.

---

## Baseline

**What:** Single-pass candidate evaluation — the pre-existing ResumePilot
workflow (resume + JD → one holistic AI judgement). Captured before any challenge
changes in `docs/baseline-record.md`.

**Result:** See `evaluation/baseline_results.json`. On the current 10-case suite
the *deterministic* baseline scores an aggregate of **45.0%** evidence accuracy
(see "Current measured state" below). The *Gemini* baseline is [pending real
run — needs a key].

**Why this matters:** establishes the bar the agent pipeline must beat.

---

## Experiment 1 — Structured Evidence Extraction

**Why:** On the baseline, the model can claim a requirement is supported on
indirect evidence (e.g. treating "cloud experience" as AWS). We hypothesised
that extracting structured, quoted evidence *first*, and only reasoning from
those quotes, would ground the verdicts.

**What:** Added the Evidence Extraction agent (`ai/agents/evidence_extractor.py`)
— resume → list of `{skill, exact quote, source section, confidence}`. Matching
is now driven by these quotes, not by re-reading the whole resume.

**Result:** [pending real run — measured once `GOOGLE_API_KEY` is provided]

**Decision:** Kept — extraction is the foundation of the pipeline regardless of
the headline number; the dashboard cannot show quotes without it.

---

## Experiment 2 — Evidence Verification with strict prompts

**Why:** The verifier can still inflate. A skill that only appears in a skills
list is not "SUPPORTED"; "working knowledge of GraphQL (read queries)" is not
GraphQL experience.

**What:** Added the Verifier agent (`ai/agents/verifier.py`) with a deliberately
strict prompt (SUPPORTED / PARTIALLY_SUPPORTED / NOT_VERIFIED / NOT_FOUND, each
verdict quoting the exact resume line), plus the deterministic Matcher
(`ai/agents/matcher.py`) that shortlists candidate quotes so the verifier judges
a focused set rather than the whole resume.

**Result:** [pending real run — measured once `GOOGLE_API_KEY` is provided]

**Decision:** Kept — strictness is the core defence against false positives.

---

## Experiment 3 — Human review loop

**What:** Wrapped the agent output in a recruiter review dashboard
(`pages/7_📋_Candidate_Evaluation.py`) with Confirm / Reject / Needs-review per
verdict, and export of the reviewed evaluation. This makes the system a
human-in-the-loop tool rather than an autopilot.

**Result:** No accuracy metric applies; outcome is workflow usability.
**Decision:** Kept — the review loop is part of the final design.

---

## Current measured state (10-case suite, deterministic)

From `python evaluation/run_evaluation.py --heuristic` — the deterministic
fallback runs the **same evaluator for baseline and agent**, so Δ = 0 here is
expected by construction. This is a **wiring / reproducibility smoke test**, not
the real agent comparison. It proves the harness is deterministic (byte-identical
across runs and hash seeds) and that all 10 cases load and score correctly.

| Case | Baseline | Agent | Δ |
|------|---------:|------:|:--:|
| case_01_backend_engineer | 20.0% | 20.0% | +0.0pp |
| case_02_data_analyst | 60.0% | 60.0% | +0.0pp |
| case_03_frontend_engineer | 60.0% | 60.0% | +0.0pp |
| case_04_ml_engineer | 50.0% | 50.0% | +0.0pp |
| case_05_devops_engineer | 75.0% | 75.0% | +0.0pp |
| case_06_fullstack_engineer | 20.0% | 20.0% | +0.0pp |
| case_07_product_manager | 25.0% | 25.0% | +0.0pp |
| case_08_mobile_developer | 25.0% | 25.0% | +0.0pp |
| case_09_data_engineer | 40.0% | 40.0% | +0.0pp |
| case_10_qa_automation_engineer | 75.0% | 75.0% | +0.0pp |
| **Aggregate (10 cases)** | **45.0%** | **45.0%** | **+0.0pp** |

> **Reproducibility fix (QA-2024):** `heuristic_evaluate` ranked requirements
> with a frequency-only sort over a `set`, so tie order depended on
> `PYTHONHASHSEED` and identical inputs produced different requirement sets (and
> accuracy) on every run — observed aggregates of 58.3% / 75.6% / 83.3% for the
> same inputs. The sort now breaks ties alphabetically (`(-count, term)`) and the
> stopword list was expanded to drop junk tokens (`or`, `have`, `nice`, `ad`,
> `hoc`, `grasp`, `turn`, …). Verified: three fresh `--heuristic` runs across
> different hash seeds produce byte-identical `baseline_results.json`,
> `agent_results.json`, and `comparison.md`.

---

## Real agent comparison (the headline measurement)

To measure the *actual* improvement of the evidence-based agent over the
single-pass baseline, both must run against Gemini. This requires a key. Once
`GOOGLE_API_KEY` is available:

```bash
GOOGLE_API_KEY="AIza..." python evaluation/run_evaluation.py
```

This runs both systems on the same 10 cases, aligns to the hand-labelled
`expected_evidence.json` ground truth, and writes:
`evaluation/baseline_results.json`, `evaluation/agent_results.json`,
`evaluation/comparison.md`. Replace the table below with that output:

| Case | Baseline | Agent | Δ |
|------|---------:|------:|:--:|
| **Aggregate (10 cases)** | **pending real run** | **pending real run** | **pending** |

**Expected direction (hypothesis, not a number):** the agent should reduce false
positives — cases like `case_01` (cloud ≠ AWS), `case_04` (Spark listed but
unused), and `case_06` (GraphQL absent) are traps the strict verifier was built
to catch.

---

## Hot take / main failure mode the project exists to fix

Single-pass, holistic resume scoring is **silently over-confident**. It produces
a headline like "Candidate score: 82%" while quietly treating a skills list as
proof, "cloud experience" as AWS, and an absent technology as satisfied. That
failure is not a model quality problem — it is a **process** problem: the model
is never forced to quote the exact line that supports a verdict. The evidence-based
agent exists to make every verdict traceable to a quoted resume sentence, so the
false confidence becomes visible (and correctable by a human reviewer) instead
of hidden inside a single number.
