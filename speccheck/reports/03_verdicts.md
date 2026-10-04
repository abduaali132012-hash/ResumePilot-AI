# Verdict Report

Source evidence: `speccheck/reports/02_evidence.md`
Verdict formula: IMPLEMENTED_AND_TESTED / IMPLEMENTED_UNTESTED / PARTIAL / MISSING / CONFLICT

---

## Verdict Table

| ID | Requirement (short) | Verdict | Rationale |
|----|---------------------|---------|-----------|
| REQ-01 | RequirementExtractor splits compound items | IMPLEMENTED_UNTESTED | `RequirementExtractor.extract()` exists at `ai/agents/requirement_extractor.py:20-37` and the compound-split rule is in `ai/prompts/templates.py:12`; no test exercises `extract()` or verifies the split behaviour. |
| REQ-02 | EvidenceExtractor outputs structured claims without scoring/verdict | IMPLEMENTED_UNTESTED | `EvidenceExtractor.extract()` at `ai/agents/evidence_extractor.py:25-44` returns only `Evidence(skill, evidence, source, confidence)` — no score or verdict field exists in the schema (`ai/models/schemas.py:22-44`); no test calls `extract()`. |
| REQ-03 | Matcher uses deterministic logic (no LLM call) | IMPLEMENTED_UNTESTED | `ai/agents/matcher.py:1-83` is pure Python token overlap with no LLM import; determinism is guaranteed by sorted deduplication at line 82; no test calls `Matcher.match()` or asserts identical output across PYTHONHASHSEED values. |
| REQ-04 | Verifier returns one of four verdict statuses, with quotes | PARTIAL | The four statuses and the fallback loop (`ai/agents/verifier.py:69-98`) ensure every requirement receives a verdict; however, the acceptance criterion also requires at least one quote for any non-NOT_FOUND verdict — no code guard enforces non-empty `evidence_quotes` for SUPPORTED/PARTIALLY_SUPPORTED (prompt-only rule at `ai/prompts/templates.py:71`). |
| REQ-05a | Skills-list-only mention is not SUPPORTED | IMPLEMENTED_UNTESTED | Rule encoded in prompt at `ai/prompts/templates.py:77-78` and verifier docstring at `ai/agents/verifier.py:8-10`; no code-level guard and no test exercises this anti-inflation rule. |
| REQ-05b | "Cloud experience" not treated as AWS | IMPLEMENTED_UNTESTED | Rule encoded in prompt at `ai/prompts/templates.py:79` and schema comment at `ai/models/schemas.py:12`; no code-level guard and no test verifies this specific case. |
| REQ-05c | "Working knowledge of X" not treated as full experience | IMPLEMENTED_UNTESTED | Rule encoded in prompt at `ai/prompts/templates.py:44-45,74`; no code-level guard and no test exercises this anti-inflation rule. |
| REQ-05d | Absent technology is never SUPPORTED | IMPLEMENTED_UNTESTED | The status allow-list at `ai/agents/verifier.py:69-71` coerces unknown statuses to NOT_VERIFIED (never inflates to SUPPORTED); absence enforcement is otherwise prompt-only (`ai/prompts/templates.py:65-70`); no test verifies this property. |
| REQ-06 | Works without an API key (deterministic fallback) | IMPLEMENTED_UNTESTED | `GeminiClient.available` at `ai/inference/__init__.py:95-97` returns False with no key; `auto_evaluate()` falls back to `heuristic_evaluate()` at `ai/pipeline.py:183-192`; the UI branch at `pages/7_📋_Candidate_Evaluation.py:206-209` routes accordingly; no test runs the pipeline with no API key set. |
| REQ-07 | `--heuristic` run is reproducible across PYTHONHASHSEED values | IMPLEMENTED_UNTESTED | Alphabetical tie-breaking at `ai/pipeline.py:128-133` and sorted directory iteration at `evaluation/run_evaluation.py:188-189` make the harness deterministic; no test runs the harness twice with different PYTHONHASHSEED values and compares results. |
| REQ-08a | Harness writes `evaluation/baseline_results.json` | IMPLEMENTED_UNTESTED | `evaluation/run_evaluation.py:237-240` writes the file; `evaluation/validate_evaluation.py:25-28` checks for existence but also asserts `cases`/`summary` keys that the harness does not write, so the validator would fail; the acceptance criterion (file created) is met in code but no passing test confirms it. |
| REQ-08b | Harness writes `evaluation/agent_results.json` | IMPLEMENTED_UNTESTED | `evaluation/run_evaluation.py:240-244` writes the file; same key-shape mismatch in `validate_evaluation.py` as REQ-08a means no passing test exists. |
| REQ-08c | Harness writes `evaluation/comparison.md` | IMPLEMENTED_UNTESTED | `evaluation/run_evaluation.py:243-248` writes the file; `validate_evaluation.py` does not check for `comparison.md` at all, so there is no test for this output. |
| REQ-09 | Human review dashboard: Confirm / Reject / Needs-review | IMPLEMENTED_UNTESTED | `pages/7_📋_Candidate_Evaluation.py:100-122` wires all three actions as `SelectboxColumn` options and persists them back onto each verdict; no test exercises the dashboard or the review-persistence logic. |
| REQ-10 | JSON export contains requirement, verdict, and reviewer decision | IMPLEMENTED_UNTESTED | `pages/7_📋_Candidate_Evaluation.py:140-149` calls `ev.to_dict()`; `CandidateEvaluation.to_dict()` at `ai/models/schemas.py:114-122` serialises the full verdicts list including `RequirementVerdict.review`; no test calls `to_dict()` and asserts the `review` field is present. |
| REQ-11 | Original `app.py` remains runnable | IMPLEMENTED_AND_TESTED | `app.py` is structurally unchanged; `test_app.py:11` imports `calculate_score` and `extract_section` directly from `app.py` — a broken import would fail test collection; the existing test suite passes, confirming the module loads without error. |
| REQ-12 | Batch candidate ranking (Roadmap) | PARTIAL | `pages/5_📊_Recruiter_Dashboard.py:61-72,113` implements multi-resume ranking, but sorts by an LLM-generated 0-100 score, not by verified-requirement coverage as the acceptance criterion specifies. |
| REQ-13 | Timestamped audit log (Roadmap) | MISSING | No audit log file, no timestamp-writing code, and no log module exists anywhere in the codebase. |

---

## Summary

| Verdict | Count | Requirements |
|---------|-------|-------------|
| IMPLEMENTED_AND_TESTED | 1 | REQ-11 |
| IMPLEMENTED_UNTESTED | 14 | REQ-01, REQ-02, REQ-03, REQ-05a, REQ-05b, REQ-05c, REQ-05d, REQ-06, REQ-07, REQ-08a, REQ-08b, REQ-08c, REQ-09, REQ-10 |
| PARTIAL | 2 | REQ-04, REQ-12 |
| MISSING | 1 | REQ-13 |
| CONFLICT | 0 | — |
| **Total** | **18** | |

---

## BEFORE Coverage Score

```
Coverage = (Requirements that are IMPLEMENTED_AND_TESTED) / (Total requirements) × 100
         = 1 / 18 × 100
         = 5.6%
```

**BEFORE coverage score: 5.6%**

> _Formula source: AGENTS.md — "Coverage score = (requirements that are Implemented AND Tested) / (total requirements) × 100, rounded to one decimal."_
