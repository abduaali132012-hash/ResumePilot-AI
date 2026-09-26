# ResumePilot AI — Product Requirements Document (PRD)

Version: 1.0 (SpecCheck demo target)
Scope: Evidence-Based Candidate Evaluation Agent and the surrounding app.

Each requirement has an ID, a statement, and an acceptance criterion.
SpecCheck verifies every requirement against the code and tests.

---

## A. Agent pipeline

**REQ-01 — Requirement extraction**
The RequirementExtractor turns a job description into a typed list of requirements.
*Acceptance:* compound items such as "Python and FastAPI" are split into separate requirements.

**REQ-02 — Evidence extraction without scoring**
The EvidenceExtractor reads a resume and outputs structured claims `{skill, exact quote, source section, confidence}`.
*Acceptance:* the extractor never produces a score or verdict; every claim includes a quote taken verbatim from the resume.

**REQ-03 — Deterministic matching**
The Matcher shortlists candidate quotes for each requirement using deterministic logic (no LLM call).
*Acceptance:* the same inputs always produce the same shortlist.

**REQ-04 — Four-level verdicts with quotes**
The Verifier returns exactly one of `SUPPORTED | PARTIALLY_SUPPORTED | NOT_VERIFIED | NOT_FOUND` for every requirement, plus the supporting quotes.
*Acceptance:* no requirement is left without a verdict; any non-NOT_FOUND verdict includes at least one quote.

**REQ-05 — Anti-inflation rules**
The Verifier must not inflate verdicts.
*Acceptance:* (a) a skill that appears only in a skills list with no usage context is not SUPPORTED; (b) "cloud experience" is not treated as AWS; (c) "working knowledge of X" is not treated as full X experience; (d) an absent technology is never SUPPORTED.

## B. Reliability and reproducibility

**REQ-06 — Works without an API key**
If `GOOGLE_API_KEY` is absent, the app and pipeline fall back to a deterministic evaluator.
*Acceptance:* no crash and a valid result is returned with no key set.

**REQ-07 — Reproducible evaluation harness**
`python evaluation/run_evaluation.py --heuristic` runs the 10 labelled cases.
*Acceptance:* results are byte-identical across repeated runs and different `PYTHONHASHSEED` values.

**REQ-08 — Evaluation outputs**
The harness writes `evaluation/baseline_results.json`, `evaluation/agent_results.json`, and `evaluation/comparison.md`.
*Acceptance:* all three files are created after a run.

## C. Recruiter experience

**REQ-09 — Human review dashboard**
The Candidate Evaluation page lets a reviewer mark each verdict as Confirm / Reject / Needs-review.
*Acceptance:* all three actions are available for every verdict.

**REQ-10 — JSON export of reviews**
Reviewer decisions can be exported as JSON.
*Acceptance:* the export contains each requirement, its verdict, and the reviewer's decision.

**REQ-11 — Baseline app preserved**
The original ResumePilot resume-optimization app (`app.py` and its pages) remains runnable.
*Acceptance:* `streamlit run app.py` starts without errors.

## D. Planned requirements (roadmap)

**REQ-12 — Batch candidate ranking**
A recruiter can evaluate several resumes against one job description and get a ranked list.
*Acceptance:* given N resumes, the output is a list of N candidates sorted by verified-requirement coverage.

**REQ-13 — Audit trail**
Every verdict and every reviewer decision is written to a timestamped audit log file.
*Acceptance:* after an evaluation and a review, the log contains one entry per verdict and per decision, each with a timestamp.
