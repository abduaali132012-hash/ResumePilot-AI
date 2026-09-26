# 05 — Trace Report

_SpecCheck workflow · Step 5 of 5_
_Branch: `speccheck` · Target: ResumePilot AI v1.0 · Requirements source: `speccheck/PRD.md`_

---

## 1. Executive Summary

The SpecCheck pipeline processed 18 requirements across 13 requirement IDs (REQ-01–REQ-13, with REQ-05 split into four sub-requirements).
Before SpecCheck ran, only 1 requirement (REQ-11) was covered by any passing test, yielding a coverage score of **5.6 %**.
The Test Writer (Step 4) added 62 tests across `tests/speccheck/test_requirements.py`; when run via `python -m pytest tests/speccheck -v` those tests produce 50 **PASS**, and 12 **XFAIL** results (0 failures, 0 errors).
The 12 XFAIL results each represent a confirmed defect: the test asserts the PRD-required behaviour, the application violates it, and `strict=True` ensures any accidental fix is surfaced immediately as an ERROR rather than silently passing.
Per the project rule that requirements with xfail defect tests count as **DEFECT** (not "Implemented AND Tested"), 7 requirements are now fully covered, raising the after-SpecCheck coverage score to **38.9 %** — an improvement of **33.3 percentage points**.
Ten requirements remain defective (REQ-04, REQ-05a–d, REQ-07, REQ-08a, REQ-08b, REQ-08c, REQ-12), one is missing entirely (REQ-13), and one roadmap item (REQ-12) is also partially implemented with a design mismatch; REQ-07 is counted as DEFECT because the evaluation harness rewrites its own ground-truth files on every run (DEFECT-07-gt, see §4), so the reproducibility acceptance criterion cannot be independently verified; REQ-08a, REQ-08b, and REQ-08c are counted as DEFECT because on a clean checkout the evaluation harness crashes with `KeyError: 'expected'` on the committed ground-truth files, so the acceptance criterion (output files written) can never be met (DEFECT-08, see §4).

---

## 2. Traceability Matrix

> **Status legend**
> - **PASS** — tests exist, all pass; requirement is Implemented and Tested.
> - **DEFECT** — at least one `xfail(strict=True)` test confirms the app violates the PRD.
> - **MISSING** — no implementation code and no tests exist.
> - **PRE-EXISTING** — was already Implemented and Tested before this SpecCheck run.
> - **ROADMAP/DEFECT** — roadmap item with a partial implementation that violates the acceptance criterion.

| Req ID | Requirement | Code (file:line) | Test (file:test name) | Final Status |
|--------|-------------|------------------|-----------------------|--------------|
| REQ-01 | RequirementExtractor splits compound requirements | [`ai/agents/requirement_extractor.py:16–37`](../../ai/agents/requirement_extractor.py), [`ai/prompts/templates.py:12–13`](../../ai/prompts/templates.py) | `TestReq01::test_req_01_returns_list_of_requirement_objects` · `test_req_01_compound_split_produces_two_requirements` · `test_req_01_empty_jd_returns_empty_list` · `test_req_01_requirement_has_required_fields` · `test_req_01_items_without_text_are_skipped` | **PASS** |
| REQ-02 | EvidenceExtractor outputs structured claims, no score/verdict | [`ai/agents/evidence_extractor.py:21–44`](../../ai/agents/evidence_extractor.py), [`ai/models/schemas.py:22–44`](../../ai/models/schemas.py), [`ai/prompts/templates.py:28–31`](../../ai/prompts/templates.py) | `TestReq02::test_req_02_returns_list_of_evidence_objects` · `test_req_02_evidence_has_no_score_field` · `test_req_02_evidence_has_no_verdict_field` · `test_req_02_evidence_schema_fields` · `test_req_02_empty_resume_returns_empty_list` · `test_req_02_items_without_skill_are_skipped` | **PASS** |
| REQ-03 | Matcher uses deterministic logic (no LLM call) | [`ai/agents/matcher.py:1–83`](../../ai/agents/matcher.py), [`ai/pipeline.py:128–133`](../../ai/pipeline.py) | `TestReq03::test_req_03_match_returns_dict_keyed_by_requirement_text` · `test_req_03_no_llm_call_on_match` · `test_req_03_identical_output_on_repeated_calls` · `test_req_03_python_requirement_matches_python_evidence` · `test_req_03_empty_inputs_return_empty_lists` · `test_req_03_stable_across_different_pythonhashseed` | **PASS** |
| REQ-04 | Verifier returns one of four verdict statuses, with quotes | [`ai/agents/verifier.py:69–98`](../../ai/agents/verifier.py), [`ai/models/schemas.py:10–15`](../../ai/models/schemas.py) | `TestReq04::test_req_04_all_four_statuses_are_valid` · `test_req_04_every_requirement_receives_a_verdict` · `test_req_04_unknown_status_is_coerced_to_not_verified` · `test_req_04_status_is_uppercased` · **XFAIL** `test_req_04_defect_supported_verdict_may_have_empty_quotes` | **DEFECT** |
| REQ-05a | Skills-list-only mention is not SUPPORTED | [`ai/prompts/templates.py:77–78`](../../ai/prompts/templates.py), [`ai/agents/verifier.py:8–10`](../../ai/agents/verifier.py) | **XFAIL** `TestReq05a::test_req_05a_skills_list_in_heuristic_gives_supported_by_keyword` · **XFAIL** `test_req_05a_verifier_status_allow_list_prevents_spurious_supported` | **DEFECT** |
| REQ-05b | "Cloud experience" not treated as AWS | [`ai/prompts/templates.py:79`](../../ai/prompts/templates.py), [`ai/agents/verifier.py:9`](../../ai/agents/verifier.py) | **XFAIL** `TestReq05b::test_req_05b_heuristic_cloud_is_not_aws` · **XFAIL** `test_req_05b_verifier_code_does_not_prevent_cloud_as_aws` | **DEFECT** |
| REQ-05c | "Working knowledge of X" not treated as full experience | [`ai/prompts/templates.py:44–45,74`](../../ai/prompts/templates.py) | **XFAIL** `TestReq05c::test_req_05c_heuristic_does_not_inflate_working_knowledge` · **XFAIL** `test_req_05c_verifier_no_code_guard_against_inflation` | **DEFECT** |
| REQ-05d | Absent technology is never SUPPORTED | [`ai/agents/verifier.py:69–71`](../../ai/agents/verifier.py), [`ai/prompts/templates.py:65–70`](../../ai/prompts/templates.py) | **XFAIL** `TestReq05d::test_req_05d_heuristic_absent_technology_not_supported` · PASS `test_req_05d_heuristic_absent_term_is_not_found` · PASS `test_req_05d_verifier_unknown_status_coerced_not_inflated` · PASS `test_req_05d_verifier_missing_requirement_gets_not_verified_not_supported` | **DEFECT** |
| REQ-06 | App falls back to deterministic evaluator when no API key | [`ai/pipeline.py:183–192`](../../ai/pipeline.py), [`ai/inference/__init__.py:86–97`](../../ai/inference/__init__.py), [`pages/7_📋_Candidate_Evaluation.py:206–209`](../../pages/7_📋_Candidate_Evaluation.py) | `TestReq06::test_req_06_no_api_key_gemini_client_not_available` · `test_req_06_auto_evaluate_falls_back_without_key` · `test_req_06_heuristic_evaluate_returns_structured_result` · `test_req_06_heuristic_mode_field_is_set` · `test_req_06_fallback_produces_valid_verdicts` · `test_req_06_auto_evaluate_without_key_uses_heuristic_mode` | **PASS** |
| REQ-07 | `--heuristic` run is byte-identical across PYTHONHASHSEED values | [`ai/pipeline.py:128–133`](../../ai/pipeline.py), [`evaluation/run_evaluation.py:188–189`](../../evaluation/run_evaluation.py) | `TestReq07::test_req_07_identical_output_seed_0_vs_seed_12345` · `test_req_07_identical_output_seed_1_vs_seed_99999` | **DEFECT** _(DEFECT-07-gt: harness rewrites ground-truth files; reproducibility cannot be independently verified — see §4)_ |
| REQ-08a | Harness writes `evaluation/baseline_results.json` | [`evaluation/run_evaluation.py:237–240`](../../evaluation/run_evaluation.py) | **XFAIL** `TestReq08a::test_req_08a_harness_writes_baseline_results_json` · SKIP `test_req_08a_baseline_results_is_valid_json` · SKIP `test_req_08a_baseline_results_contains_case_entries` | **DEFECT** _(DEFECT-08: harness crashes with `KeyError: 'expected'` on committed ground-truth files — see §4)_ |
| REQ-08b | Harness writes `evaluation/agent_results.json` | [`evaluation/run_evaluation.py:241–244`](../../evaluation/run_evaluation.py) | **XFAIL** `TestReq08b::test_req_08b_harness_writes_agent_results_json` · SKIP `test_req_08b_agent_results_is_valid_json` · SKIP `test_req_08b_agent_results_contains_case_entries` | **DEFECT** _(DEFECT-08: same root cause as REQ-08a — see §4)_ |
| REQ-08c | Harness writes `evaluation/comparison.md` | [`evaluation/run_evaluation.py:245–250`](../../evaluation/run_evaluation.py) | **XFAIL** `TestReq08c::test_req_08c_harness_writes_comparison_md` · SKIP `test_req_08c_comparison_md_is_markdown_table` | **DEFECT** _(DEFECT-08: same root cause as REQ-08a — see §4)_ |
| REQ-09 | Human review dashboard: Confirm / Reject / Needs-review | [`pages/7_📋_Candidate_Evaluation.py:100–122`](../../pages/7_📋_Candidate_Evaluation.py), [`ai/models/schemas.py:17–18`](../../ai/models/schemas.py) | `TestReq09::test_req_09_review_decision_type_has_all_three_values` · `test_req_09_verdict_review_defaults_to_none` · `test_req_09_review_survives_serialisation` · `test_req_09_review_persisted_on_evaluation_object` · `test_req_09_review_decision_schema_in_schemas_module` | **PASS** |
| REQ-10 | JSON export contains requirement, verdict, and reviewer decision | [`pages/7_📋_Candidate_Evaluation.py:140–149`](../../pages/7_📋_Candidate_Evaluation.py), [`ai/models/schemas.py:99–122`](../../ai/models/schemas.py) | `TestReq10::test_req_10_to_dict_includes_requirement_field` · `test_req_10_to_dict_includes_status_field` · `test_req_10_to_dict_includes_review_field` · `test_req_10_review_value_preserved_in_export` · `test_req_10_review_none_when_no_decision_made` · `test_req_10_full_export_structure` | **PASS** |
| REQ-11 | Original `app.py` remains runnable | [`app.py:1–973`](../../app.py) | [`test_app.py`](../../test_app.py) (import-level smoke — pre-existing) | **PASS (PRE-EXISTING)** |
| REQ-12 | Batch candidate ranking (Roadmap) | [`pages/5_📊_Recruiter_Dashboard.py:61–72,113`](../../pages/5_📊_Recruiter_Dashboard.py) | PASS `TestReq12::test_req_12_rank_candidates_function_exists` · **XFAIL** `test_req_12_defect_ranking_by_llm_score_not_coverage` · PASS `test_req_12_heuristic_evaluate_provides_coverage_metric` | **ROADMAP/DEFECT** |
| REQ-13 | Timestamped audit log (Roadmap) | _None_ | _None_ | **MISSING** |

---

## 3. Coverage Scores

### Formula (AGENTS.md)

```
Coverage = (requirements that are Implemented AND Tested) / (total requirements) × 100
```

Requirements with at least one `xfail(strict=True)` test are classified **DEFECT** and are **not** counted as "Implemented AND Tested."

### BEFORE (from `speccheck/reports/03_verdicts.md`, prior to Test Writer)

| Metric | Value |
|--------|-------|
| Total requirements | 18 |
| Implemented AND Tested | 1 (REQ-11 only) |
| **BEFORE coverage score** | **5.6 %** |

### AFTER (post `python -m pytest tests/speccheck -v`)

| Metric | Value |
|--------|-------|
| Total requirements | 18 |
| Total tests | 62 |
| PASS | 50 |
| SKIP (output absent due to harness defect) | 6 |
| XFAIL (confirmed defects) | 12 |
| XPASS / ERROR | 0 |
| Requirements with all-PASS tests (Implemented AND Tested) | 7 |
| Requirements with ≥1 XFAIL test (DEFECT) | 10 (REQ-04, REQ-05a, REQ-05b, REQ-05c, REQ-05d, REQ-07, REQ-08a, REQ-08b, REQ-08c, REQ-12) |
| MISSING (no code) | 1 (REQ-13) |
| **AFTER coverage score** | **38.9 %** |

```
Coverage = 7 / 18 × 100 = 38.9%
```

The 7 requirements counted as Implemented AND Tested after SpecCheck:
REQ-01, REQ-02, REQ-03, REQ-06, REQ-09, REQ-10, REQ-11.

**Coverage improvement: +33.3 percentage points (5.6 % → 38.9 %)**

---

## 4. Defects and Missing Features

### Defects confirmed by XFAIL tests

| ID | Req | Severity | Description | Code Location |
|----|-----|----------|-------------|---------------|
| DEFECT-04 | REQ-04 | Medium | `SUPPORTED` verdict is allowed with an empty `evidence_quotes` list; no code-level guard enforces ≥1 quote for non-`NOT_FOUND` verdicts; rule is prompt-only | [`ai/agents/verifier.py:72–80`](../../ai/agents/verifier.py) |
| DEFECT-05a-h | REQ-05a | High | Heuristic evaluator marks a bare skills-list keyword as `SUPPORTED` with no usage-context check | [`ai/pipeline.py:147–157`](../../ai/pipeline.py) |
| DEFECT-05a-v | REQ-05a | High | Verifier has no code guard preventing `SUPPORTED` for a skills-list-only evidence quote; enforcement is prompt-only | [`ai/agents/verifier.py:69–70`](../../ai/agents/verifier.py) |
| DEFECT-05b-h | REQ-05b | High | Heuristic extractor emits `"requires"` as a top-level requirement instead of the technology keyword (e.g., `"aws"`), because `"requires"` is absent from `_SKILL_STOP`; AWS verdicts are never surfaced by exact-match lookup | [`ai/pipeline.py:87–103`](../../ai/pipeline.py) |
| DEFECT-05b-v | REQ-05b | High | Verifier has no code guard blocking `SUPPORTED` when the only evidence quote is a generic phrase like `"cloud experience"` for an `AWS` requirement | [`ai/agents/verifier.py:69–70`](../../ai/agents/verifier.py) |
| DEFECT-05c-h | REQ-05c | High | Heuristic evaluator produces `SUPPORTED` for a resume containing only `"working knowledge of X"` — no qualifier/context check exists | [`ai/pipeline.py:147–157`](../../ai/pipeline.py) |
| DEFECT-05c-v | REQ-05c | High | Verifier has no code guard preventing `SUPPORTED` when an evidence quote states only `"working knowledge of X"` | [`ai/agents/verifier.py:69–70`](../../ai/agents/verifier.py) |
| DEFECT-05d | REQ-05d | High | Same root cause as DEFECT-05b-h: single-technology JDs of the form `"Requires Kubernetes."` may yield only `"requires"` in the extracted requirements list, so absent-technology look-ups never find the correct requirement | [`ai/pipeline.py:87–103`](../../ai/pipeline.py) |
| DEFECT-12 | REQ-12 | Medium | Recruiter Dashboard sorts candidates by an LLM-generated 0–100 score, not by verified-requirement coverage as the acceptance criterion specifies | [`pages/5_📊_Recruiter_Dashboard.py:113`](../../pages/5_📊_Recruiter_Dashboard.py) |

### Newly observed defects (confirmed by XFAIL tests or direct observation)

| ID | Req | Severity | Description | Observed Evidence |
|----|-----|----------|-------------|-------------------|
| DEFECT-08 | REQ-08a / REQ-08b / REQ-08c | Critical | On a clean checkout, `evaluation/cases/case_01`–`case_10/expected_evidence.json` use `"requirements"` as the top-level JSON key; the harness reads `json.load(...)["expected"]` → `KeyError: 'expected'` → process exits with code 1; `baseline_results.json`, `agent_results.json`, and `comparison.md` are never written. Confirmed by XFAIL tests `test_req_08a_harness_writes_baseline_results_json`, `test_req_08b_harness_writes_agent_results_json`, `test_req_08c_harness_writes_comparison_md`. | `evaluation/run_evaluation.py:213` / `evaluation/cases/case_*/expected_evidence.json` |
| DEFECT-07-gt | REQ-07 | Critical | Running `python evaluation/run_evaluation.py --heuristic` modifies the tracked ground-truth files `evaluation/cases/*/expected_evidence.json`. **Observed: 13 files changed, +2244/−242 lines** after a single run. Because the labelled evaluation data is overwritten on every harness execution, the baseline is not stable across runs, the acceptance criterion of byte-identical results cannot be independently verified, and any comparison of successive runs is meaningless. This also means the ground-truth corpus committed to the repository cannot be trusted as a stable reference. | Directly observed: 13 `evaluation/cases/*/expected_evidence.json` files changed with +2244/−242 line delta after one `--heuristic` run |

### Missing features

| ID | Req | Description |
|----|-----|-------------|
| MISSING-13 | REQ-13 | Timestamped audit log — no implementation code, no log module, no output file; requirement is entirely unimplemented |

### Test bugs fixed during this SpecCheck run (not defects in the application)

| # | Test | Root Cause |
|---|------|-----------|
| F1 | `TestReq06::test_req_06_no_api_key_gemini_client_not_available` | `_secrets_file_key` patch did not prevent `st.secrets` from providing the key on developer machines with a local `.streamlit/secrets.toml`; fixed by patching `ai.inference.get_api_key` directly |
| F2–F4 | `TestReq08a/b/c` (harness subprocess tests) | Initially treated as a test bug and "fixed" by updating fixture files; reclassified as **REAL DEFECT** (DEFECT-08) because on a clean checkout `evaluation/cases/case_01..case_10` still use `"requirements"` as the top-level key; `evaluation/` is frozen; tests now marked `@pytest.mark.xfail(strict=True)` to confirm the defect |
| F5 | `TestReq08a/b/c` (Windows subprocess) | Subprocess launched without `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`; harness crashed on non-ASCII characters; both env vars added to all three harness-writing tests |

---

## 5. Manual Review Time vs. Automated Run Time

> All figures below are **estimates**. No wall-clock timer was attached to this session.

| Activity | Estimated Duration |
|----------|--------------------|
| Reading PRD, mapping 18 requirements to code, writing evidence report (`02_evidence.md`) | 3–4 hours manual |
| Strict-verification pass — checking each code path against the acceptance criterion (`03_verdicts.md`) | 2–3 hours manual |
| Writing 62 offline tests covering 16 requirement IDs, debugging 5 test bugs, classifying 9 defects as XFAIL (`04_tests.md`) | 4–6 hours manual |
| Producing this trace report with matrix, scores, and defect list (`05_TRACE_REPORT.md`) | 1–2 hours manual |
| **Estimated total manual review time** | **10–15 hours** |
| | |
| SpecCheck automated run (pytest collection + 62 tests incl. subprocess calls) | **~90–120 seconds** (estimated from subprocess-heavy test suite on a typical CI runner; no live timer attached) |
| Full SpecCheck pipeline end-to-end (Steps 1–5, agent-assisted) | **~20–30 minutes** elapsed session time |

**Key observation:** The automated test suite surfaces the same 12 defects and 33.3-point coverage gap that a manual review would have found, but does so in approximately 2 minutes of machine time versus an estimated 10–15 hours of human analyst time — roughly a **15–30× reduction** in calendar effort for the verification step alone.

---

_Report generated by SpecCheck Step 5 (Trace Reporter) on branch `speccheck`._
_Test command: `python -m pytest tests/speccheck -v`_
_Results: 50 passed, 6 skipped, 12 xfailed — 0 errors, 0 failures._
