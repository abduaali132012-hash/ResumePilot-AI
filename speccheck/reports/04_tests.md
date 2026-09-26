# Test Report — SpecCheck

Source: [`tests/speccheck/test_requirements.py`](../../tests/speccheck/test_requirements.py)
Run command: `python -m pytest tests/speccheck -v`

> **Note on evaluation harness case count:** The README claims the harness runs
> 10 cases with a 45.0% baseline accuracy.  The harness (`evaluation/run_evaluation.py`)
> actually discovers every sub-directory under `evaluation/cases/`, so the true
> case count and aggregate accuracy depend on how many case directories are
> present.  As of the last run the harness executes more than 10 cases and the
> measured aggregate baseline accuracy is **58.9%**, not the 45.0% stated in the
> README.  The README has not been updated; the numbers in the test report
> reflect the real harness output.

---

## Bug-Fix Log (this session)

Tests were reported failing across two sessions.  For each, the root cause was
determined and classified as either **TEST BUG** (test code was wrong; fix the
test) or **DEFECT** (app does not meet the PRD requirement; keep the assertion
and mark `@pytest.mark.xfail(strict=True)`).

| # | Test | Req | Classification | Root cause / fix |
|---|------|-----|----------------|------------------|
| F1 | `TestReq06::test_req_06_no_api_key_gemini_client_not_available` | REQ-06 | **TEST BUG FIXED** | `get_api_key()` checks `st.secrets` before `_secrets_file_key()` — a local `.streamlit/secrets.toml` leaks the key even when env vars are cleared. Fix: `monkeypatch.setattr("ai.inference.get_api_key", lambda: None)` instead of patching only `_secrets_file_key`. |
| F2 | `TestReq08a::test_req_08a_harness_writes_baseline_results_json` | REQ-08a | **TEST BUG FIXED** | `evaluation/cases/case_01`–`case_10` used `"requirements"` as the top-level JSON key; the harness expects `"expected"`, so `json.loads(...)["expected"]` raised `KeyError` and the process exited with code 1. Fix: updated all 10 old-format case files to use `"expected"` with uppercase status strings. |
| F3 | `TestReq08b::test_req_08b_harness_writes_agent_results_json` | REQ-08b | **TEST BUG FIXED** | Same root cause as F2. |
| F4 | `TestReq08c::test_req_08c_harness_writes_comparison_md` | REQ-08c | **TEST BUG FIXED** | Same root cause as F2. |
| F5 | `TestReq08a/08b/08c` (subprocess tests) | REQ-08a/b/c | **TEST BUG FIXED** | On Windows the subprocess launched without `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` caused the harness to fail on non-ASCII characters in case files or emoji in file paths. Fix: added `"PYTHONUTF8": "1"` and `"PYTHONIOENCODING": "utf-8"` to the `env` dict in all three `test_req_08*_harness_writes_*` tests. |
| F6 | `TestReq05b::test_req_05b_heuristic_cloud_is_not_aws` | REQ-05b | **REAL DEFECT** | `heuristic_evaluate()` with JD `"Requires experience with AWS."` never surfaces `aws` as a requirement because `"requires"` is not in `_SKILL_STOP` and crowds out the technology token.  The test assertion `v.requirement.lower() == "aws"` finds zero verdicts. Marked `@pytest.mark.xfail(strict=True, reason="REQ-01 defect: heuristic extractor returns 'requires' instead of the technology")`. |
| F7 | `TestReq05d::test_req_05d_heuristic_absent_technology_not_supported` | REQ-05d | **REAL DEFECT** | Same root cause as F6 — JD `"Requires Kubernetes."` can result in `"kubernetes."` (period-suffixed) not matching the filter `"kubernetes" in v.requirement.lower()` in all edge cases. Marked `@pytest.mark.xfail(strict=True, reason="REQ-01 defect: heuristic extractor returns 'requires' instead of the technology")`. |

---

## Test Table

Legend:
- **PASS** — test asserts required behaviour; app meets the requirement.
- **XFAIL** — test asserts required behaviour; app does **not** meet it (defect confirmed). Marked `@pytest.mark.xfail(strict=True)`.

| # | Test ID | Req | Description | Result |
|---|---------|-----|-------------|--------|
| 1 | `TestReq01::test_req_01_returns_list_of_requirement_objects` | REQ-01 | `extract()` returns `list[Requirement]` | PASS |
| 2 | `TestReq01::test_req_01_compound_split_produces_two_requirements` | REQ-01 | "Python and FastAPI" → two separate `Requirement` objects | PASS |
| 3 | `TestReq01::test_req_01_empty_jd_returns_empty_list` | REQ-01 | Empty JD → `[]` | PASS |
| 4 | `TestReq01::test_req_01_requirement_has_required_fields` | REQ-01 | Each `Requirement` carries `text`, `category`, `importance` | PASS |
| 5 | `TestReq01::test_req_01_items_without_text_are_skipped` | REQ-01 | Malformed items (no `text`) silently discarded | PASS |
| 6 | `TestReq02::test_req_02_returns_list_of_evidence_objects` | REQ-02 | `extract()` returns `list[Evidence]` | PASS |
| 7 | `TestReq02::test_req_02_evidence_has_no_score_field` | REQ-02 | `Evidence` has no `score` attribute | PASS |
| 8 | `TestReq02::test_req_02_evidence_has_no_verdict_field` | REQ-02 | `Evidence` has no `verdict` attribute | PASS |
| 9 | `TestReq02::test_req_02_evidence_schema_fields` | REQ-02 | `Evidence` carries `skill`, `evidence`, `source`, `confidence` | PASS |
| 10 | `TestReq02::test_req_02_empty_resume_returns_empty_list` | REQ-02 | Empty resume → `[]` | PASS |
| 11 | `TestReq02::test_req_02_items_without_skill_are_skipped` | REQ-02 | Items missing `skill` silently discarded | PASS |
| 12 | `TestReq03::test_req_03_match_returns_dict_keyed_by_requirement_text` | REQ-03 | `match()` returns `dict` keyed by requirement text | PASS |
| 13 | `TestReq03::test_req_03_no_llm_call_on_match` | REQ-03 | `Matcher` has no `client` attribute → no LLM dependency | PASS |
| 14 | `TestReq03::test_req_03_identical_output_on_repeated_calls` | REQ-03 | Two calls with same input produce same output | PASS |
| 15 | `TestReq03::test_req_03_python_requirement_matches_python_evidence` | REQ-03 | "Experience with Python" shortlists the Python evidence entry | PASS |
| 16 | `TestReq03::test_req_03_empty_inputs_return_empty_lists` | REQ-03 | Empty evidence list → empty candidate lists | PASS |
| 17 | `TestReq03::test_req_03_stable_across_different_pythonhashseed` | REQ-03 | Subprocess check: output identical with seed=0 vs seed=12345 | PASS |
| 18 | `TestReq04::test_req_04_all_four_statuses_are_valid` | REQ-04 | All four `VerdictStatus` values accepted by `RequirementVerdict` | PASS |
| 19 | `TestReq04::test_req_04_every_requirement_receives_a_verdict` | REQ-04 | Defensive fallback fills in `NOT_VERIFIED` for LLM-skipped requirements | PASS |
| 20 | `TestReq04::test_req_04_unknown_status_is_coerced_to_not_verified` | REQ-04 | OOV status string → coerced to `NOT_VERIFIED` | PASS |
| 21 | `TestReq04::test_req_04_status_is_uppercased` | REQ-04 | Lowercase `"supported"` from model → `"SUPPORTED"` | PASS |
| 22 | `TestReq04::test_req_04_defect_supported_verdict_may_have_empty_quotes` | REQ-04 | **DEFECT**: `SUPPORTED` must have ≥1 `evidence_quote`; code has no guard | **XFAIL** |
| 23 | `TestReq05a::test_req_05a_skills_list_in_heuristic_gives_supported_by_keyword` | REQ-05a | **DEFECT**: Heuristic must not mark bare skills-list keyword as `SUPPORTED` | **XFAIL** |
| 24 | `TestReq05a::test_req_05a_verifier_status_allow_list_prevents_spurious_supported` | REQ-05a | **DEFECT**: Verifier must block `SUPPORTED` for skills-list-only evidence | **XFAIL** |
| 25 | `TestReq05b::test_req_05b_heuristic_cloud_is_not_aws` | REQ-05b | **DEFECT**: Heuristic: `"requires"` extracted instead of `"aws"` — technology never appears in verdicts | **XFAIL** |
| 26 | `TestReq05b::test_req_05b_verifier_code_does_not_prevent_cloud_as_aws` | REQ-05b | **DEFECT**: Verifier must not accept "cloud experience" as AWS evidence | **XFAIL** |
| 27 | `TestReq05c::test_req_05c_heuristic_does_not_inflate_working_knowledge` | REQ-05c | **DEFECT**: Heuristic must not return `SUPPORTED` for "working knowledge of X" | **XFAIL** |
| 28 | `TestReq05c::test_req_05c_verifier_no_code_guard_against_inflation` | REQ-05c | **DEFECT**: Verifier must not produce `SUPPORTED` for "working knowledge" evidence | **XFAIL** |
| 29 | `TestReq05d::test_req_05d_heuristic_absent_technology_not_supported` | REQ-05d | **DEFECT**: `"kubernetes"` not found as requirement — extractor emits `"requires"` instead | **XFAIL** |
| 30 | `TestReq05d::test_req_05d_heuristic_absent_term_is_not_found` | REQ-05d | Absent term → `NOT_FOUND` | PASS |
| 31 | `TestReq05d::test_req_05d_verifier_unknown_status_coerced_not_inflated` | REQ-05d | OOV status → `NOT_VERIFIED`, never `SUPPORTED` | PASS |
| 32 | `TestReq05d::test_req_05d_verifier_missing_requirement_gets_not_verified_not_supported` | REQ-05d | LLM-skipped requirement → `NOT_VERIFIED`, not `SUPPORTED` | PASS |
| 33 | `TestReq06::test_req_06_no_api_key_gemini_client_not_available` | REQ-06 | `GeminiClient.available = False` when no key set — **TEST BUG FIXED**: now uses `monkeypatch` to patch `get_api_key` entirely, isolating from `st.secrets` and `.streamlit/secrets.toml` | PASS |
| 34 | `TestReq06::test_req_06_auto_evaluate_falls_back_without_key` | REQ-06 | `auto_evaluate()` returns `CandidateEvaluation` when pipeline raises | PASS |
| 35 | `TestReq06::test_req_06_heuristic_evaluate_returns_structured_result` | REQ-06 | `heuristic_evaluate()` returns `CandidateEvaluation` with verdicts | PASS |
| 36 | `TestReq06::test_req_06_heuristic_mode_field_is_set` | REQ-06 | `result.mode == "heuristic"` | PASS |
| 37 | `TestReq06::test_req_06_fallback_produces_valid_verdicts` | REQ-06 | Every heuristic verdict has a valid status | PASS |
| 38 | `TestReq06::test_req_06_auto_evaluate_without_key_uses_heuristic_mode` | REQ-06 | `auto_evaluate()` with mocked failure → `mode == "heuristic"` | PASS |
| 39 | `TestReq07::test_req_07_identical_output_seed_0_vs_seed_12345` | REQ-07 | Subprocess: sorted verdicts identical with PYTHONHASHSEED=0 and =12345 | PASS |
| 40 | `TestReq07::test_req_07_identical_output_seed_1_vs_seed_99999` | REQ-07 | Subprocess: sorted verdicts identical with PYTHONHASHSEED=1 and =99999 | PASS |
| 41 | `TestReq08a::test_req_08a_harness_writes_baseline_results_json` | REQ-08a | Harness `--heuristic` creates `evaluation/baseline_results.json` — **TEST BUG FIXED (2 rounds)**: (1) old case files used `"requirements"` key; (2) subprocess needed `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8` on Windows | PASS |
| 42 | `TestReq08a::test_req_08a_baseline_results_is_valid_json` | REQ-08a | `baseline_results.json` parses as JSON `dict` | PASS |
| 43 | `TestReq08a::test_req_08a_baseline_results_contains_case_entries` | REQ-08a | Each case entry has `evidence_accuracy` key | PASS |
| 44 | `TestReq08b::test_req_08b_harness_writes_agent_results_json` | REQ-08b | Harness `--heuristic` creates `evaluation/agent_results.json` — **TEST BUG FIXED (2 rounds)**: (1) old case files; (2) subprocess `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8` | PASS |
| 45 | `TestReq08b::test_req_08b_agent_results_is_valid_json` | REQ-08b | `agent_results.json` parses as JSON `dict` | PASS |
| 46 | `TestReq08b::test_req_08b_agent_results_contains_case_entries` | REQ-08b | Each case entry has `evidence_accuracy` key | PASS |
| 47 | `TestReq08c::test_req_08c_harness_writes_comparison_md` | REQ-08c | Harness `--heuristic` creates `evaluation/comparison.md` — **TEST BUG FIXED (2 rounds)**: (1) old case files; (2) subprocess `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8` | PASS |
| 48 | `TestReq08c::test_req_08c_comparison_md_is_markdown_table` | REQ-08c | `comparison.md` contains a markdown table and mentions "accuracy" | PASS |
| 49 | `TestReq09::test_req_09_review_decision_type_has_all_three_values` | REQ-09 | `RequirementVerdict` accepts `confirm`, `reject`, `needs_review` | PASS |
| 50 | `TestReq09::test_req_09_verdict_review_defaults_to_none` | REQ-09 | `verdict.review` defaults to `None` | PASS |
| 51 | `TestReq09::test_req_09_review_survives_serialisation` | REQ-09 | `review` preserved through `to_dict()` | PASS |
| 52 | `TestReq09::test_req_09_review_persisted_on_evaluation_object` | REQ-09 | Mutating `verdict.review` appears in `CandidateEvaluation.to_dict()` | PASS |
| 53 | `TestReq09::test_req_09_review_decision_schema_in_schemas_module` | REQ-09 | `ReviewDecision` importable from `ai.models.schemas` | PASS |
| 54 | `TestReq10::test_req_10_to_dict_includes_requirement_field` | REQ-10 | Verdict dict has `"requirement"` key | PASS |
| 55 | `TestReq10::test_req_10_to_dict_includes_status_field` | REQ-10 | Verdict dict has `"status"` key | PASS |
| 56 | `TestReq10::test_req_10_to_dict_includes_review_field` | REQ-10 | Verdict dict has `"review"` key | PASS |
| 57 | `TestReq10::test_req_10_review_value_preserved_in_export` | REQ-10 | Reviewer decision exact-match after JSON export | PASS |
| 58 | `TestReq10::test_req_10_review_none_when_no_decision_made` | REQ-10 | `review = None` when no decision | PASS |
| 59 | `TestReq10::test_req_10_full_export_structure` | REQ-10 | All top-level keys present in `to_dict()` output | PASS |
| 60 | `TestReq12::test_req_12_rank_candidates_function_exists` | REQ-12 | `rank_candidates()` defined in Recruiter Dashboard source | PASS |
| 61 | `TestReq12::test_req_12_defect_ranking_by_llm_score_not_coverage` | REQ-12 | **DEFECT**: Dashboard must sort by `coverage_from_verdicts()`, not LLM score | **XFAIL** |
| 62 | `TestReq12::test_req_12_heuristic_evaluate_provides_coverage_metric` | REQ-12 | `heuristic_evaluate()` produces usable `overall_coverage`; candidate A > B | PASS |

---

## Defect Summary

Tests #22, #23, #24, #25, #26, #27, #28, #29, #61 are marked `@pytest.mark.xfail(strict=True)`.
They assert the **PRD-required behaviour**.  Because the app violates that behaviour,
pytest reports them as **XFAIL** — confirming a real defect.

An XFAIL result means: *"the test ran, the assertion failed as expected — the defect is present."*

If a defect is fixed, the formerly-XFAIL test will become **XPASS**, which `strict=True` converts to a hard ERROR, preventing silent regression.

| # | Req | Defect | Code Location |
|---|-----|--------|---------------|
| DEFECT-01-h | REQ-01 / REQ-05b / REQ-05d | `_SKILL_STOP` in `ai/pipeline.py` does not include `"requires"` (or similar verb forms), so the heuristic extractor emits `"requires"` as a top-level requirement instead of the actual technology keyword; this breaks exact-match verdict look-ups in tests for REQ-05b and REQ-05d | `ai/pipeline.py:87-103` |
| DEFECT-04 | REQ-04 (PARTIAL) | `SUPPORTED` verdict allowed with empty `evidence_quotes`; non-empty quotes not enforced by code | `ai/agents/verifier.py:72-80` |
| DEFECT-05a-h | REQ-05a | Heuristic marks skills-list keyword as `SUPPORTED` — no usage-context check | `ai/pipeline.py:147-157` |
| DEFECT-05a-v | REQ-05a | Verifier code has no guard preventing `SUPPORTED` for a skills-list-only mention | `ai/agents/verifier.py:69-70` |
| DEFECT-05b-h | REQ-05b | Heuristic extractor emits `"requires"` instead of `"aws"` — exact-match filter never finds the AWS verdict (see DEFECT-01-h) | `ai/pipeline.py:87-103` |
| DEFECT-05b-v | REQ-05b | Verifier allows "cloud experience" as AWS evidence — prompt-only rule | `ai/agents/verifier.py:69-70` |
| DEFECT-05c-h | REQ-05c | Heuristic marks "working knowledge of X" as `SUPPORTED` via keyword match | `ai/pipeline.py:147-157` |
| DEFECT-05c-v | REQ-05c | Verifier code does not guard against "working knowledge" inflation | `ai/agents/verifier.py:69-70` |
| DEFECT-05d | REQ-05d | Heuristic extractor emits `"requires"` alongside the technology; single-term JDs may not surface the technology at all (see DEFECT-01-h) | `ai/pipeline.py:87-103` |
| DEFECT-12 | REQ-12 (PARTIAL) | Recruiter Dashboard ranks by LLM score (0–100), not verified-requirement coverage | `pages/5_📊_Recruiter_Dashboard.py:113` |

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 62 |
| Requirements exercised | 16 (REQ-01–REQ-10, REQ-12) |
| Skipped by design | REQ-11 (already IMPLEMENTED_AND_TESTED), REQ-13 (MISSING — no code exists) |
| PASS (requirement met) | 53 |
| XFAIL (requirement **not** met — defect confirmed) | 9 |
| XPASS / ERROR | 0 (expected) |

> Run `python -m pytest tests/speccheck -v` to verify.
> XFAIL results appear in the pytest summary as `xfailed` — this is the correct signal for an unmet requirement.
> Any XPASS result means an unexpected fix; `strict=True` converts it to an ERROR so it cannot be silently ignored.

---

## Test Bug Fix Table (this session)

| Test | Req | Classification | One-line reason |
|------|-----|----------------|-----------------|
| `TestReq06::test_req_06_no_api_key_gemini_client_not_available` | REQ-06 | **TEST BUG FIXED** | `patch("ai.inference._secrets_file_key")` did not stop `st.secrets` from returning a key; replaced with `monkeypatch.setattr("ai.inference.get_api_key", lambda: None)` |
| `TestReq08a::test_req_08a_harness_writes_baseline_results_json` | REQ-08a | **TEST BUG FIXED** | `evaluation/cases/case_01`–`case_10` used `"requirements"` key; harness reads `["expected"]` → `KeyError`; updated 10 fixture files to `"expected"` with uppercase statuses |
| `TestReq08b::test_req_08b_harness_writes_agent_results_json` | REQ-08b | **TEST BUG FIXED** | Same old-format case fixture issue |
| `TestReq08c::test_req_08c_harness_writes_comparison_md` | REQ-08c | **TEST BUG FIXED** | Same old-format case fixture issue |
| `TestReq08a/b/c` (harness subprocess tests) | REQ-08a/b/c | **TEST BUG FIXED** | On Windows, subprocess env lacked `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`; harness crashed on non-ASCII content; added both env vars to the three `test_req_08*_harness_writes_*` tests |
| `TestReq05b::test_req_05b_heuristic_cloud_is_not_aws` | REQ-05b | **REAL DEFECT — kept as XFAIL** | `"requires"` not in `_SKILL_STOP`; JD `"Requires experience with AWS."` yields verdict for `"requires"` but not `"aws"` as an exact match; marked `xfail(strict=True, reason="REQ-01 defect: …")` |
| `TestReq05d::test_req_05d_heuristic_absent_technology_not_supported` | REQ-05d | **REAL DEFECT — kept as XFAIL** | Same root cause; JD `"Requires Kubernetes."` may only surface `"requires"` in the requirements list; marked `xfail(strict=True, reason="REQ-01 defect: …")` |
