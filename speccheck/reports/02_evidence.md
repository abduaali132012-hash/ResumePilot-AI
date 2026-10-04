# Evidence Report

Source requirements: `speccheck/reports/01_requirements.md`
Searched: entire repository (all `.py`, `.ts`, `.tsx` files).

---

## REQ-01 — RequirementExtractor splits compound requirements

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/agents/requirement_extractor.py` | 16–37 | `class RequirementExtractor: … def extract(self, job_description: str) -> list[Requirement]:` |
| `ai/prompts/templates.py` | 12–13 | `- Split compound requirements into separate items ("Python and FastAPI" becomes`<br>`  two requirements).` |

The splitting rule lives entirely in the prompt. The extractor calls the LLM and maps the returned items to typed `Requirement` objects (`ai/agents/requirement_extractor.py:27–37`). The "split compound items" instruction appears in the `REQUIREMENT_EXTRACTION` prompt template (`ai/prompts/templates.py:12`).

**Existing tests**

NONE FOUND — no test exercises `RequirementExtractor.extract()` or verifies the compound-split rule.

---

## REQ-02 — EvidenceExtractor outputs structured claims without scoring/verdict

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/agents/evidence_extractor.py` | 21–44 | `class EvidenceExtractor: … def extract(self, resume_text: str) -> list[Evidence]:` — returns `Evidence(skill, evidence, source, confidence)` only |
| `ai/prompts/templates.py` | 28–31 | `"Your ONLY job is to extract factual, verifiable claims … You never judge, score, or infer beyond what the resume says."` |
| `ai/models/schemas.py` | 22–44 | `@dataclass class Evidence: skill, evidence, source, confidence` — no score or verdict field |

**Existing tests**

NONE FOUND — no test calls `EvidenceExtractor.extract()`.

---

## REQ-03 — Matcher uses deterministic logic (no LLM call)

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/agents/matcher.py` | 1–83 | Entire class — pure Python token overlap, zero LLM calls |
| `ai/agents/matcher.py` | 48–82 | `class Matcher: def match(…) -> dict[str, list[Evidence]]:` — uses `_tokens()` and `_overlap()`, no `import genai` or client reference |
| `ai/pipeline.py` | 128–133 | `ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))` — tie-breaking comment explains PYTHONHASHSEED stability |

**Existing tests**

NONE FOUND — no test calls `Matcher.match()` or asserts identical output across calls.

---

## REQ-04 — Verifier returns one of four verdict statuses, with quotes

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/agents/verifier.py` | 69–70 | `status = str(item.get("status", "NOT_VERIFIED")).upper()` / `if status not in {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"}: status = "NOT_VERIFIED"` |
| `ai/agents/verifier.py` | 87–98 | Defensive fallback loop: every requirement not covered by the model gets an explicit `NOT_VERIFIED` verdict |
| `ai/models/schemas.py` | 10–15 | `VerdictStatus = Literal["SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_VERIFIED", "NOT_FOUND"]` |
| `ai/prompts/templates.py` | 64–71 | Prompt specifies all four statuses and requires `evidence_quotes` for non-NOT_FOUND verdicts |

**Existing tests**

NONE FOUND — no test calls `Verifier.verify()` or checks verdict completeness.

---

## REQ-05a — Skills-list-only mention is not SUPPORTED

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/prompts/templates.py` | 77–78 | `- A skill mentioned in a skills list with no usage context = "PARTIALLY_SUPPORTED"`<br>`  or "NOT_VERIFIED", never "SUPPORTED".` |
| `ai/agents/verifier.py` | 8–10 | Docstring: `"a skills-list mention is not 'SUPPORTED'; 'cloud experience' is not 'AWS'."` |

Rule is enforced via prompt instruction; no code-level guard exists.

**Existing tests**

NONE FOUND.

---

## REQ-05b — "Cloud experience" not treated as AWS

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/prompts/templates.py` | 79 | `- "Cloud experience" is NOT evidence of "AWS".` |
| `ai/models/schemas.py` | 12 | `"PARTIALLY_SUPPORTED", # indirect/weak evidence — e.g. "cloud" without naming AWS` |
| `ai/agents/verifier.py` | 9 | Docstring: `"'cloud experience' is not 'AWS'."` |

Rule is enforced via prompt instruction and type-system comment; no code-level guard.

**Existing tests**

NONE FOUND.

---

## REQ-05c — "Working knowledge of X" not treated as full X experience

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/prompts/templates.py` | 44–45 | `- Do not invent achievements. If the resume says "knowledge of X", say so in`<br>`  the quote — do not upgrade it to "X years of experience".` |
| `ai/prompts/templates.py` | 74 | `Be brutally honest about weak evidence. Do NOT inflate.` |

Rule is enforced via prompt instruction only; no code-level guard.

**Existing tests**

NONE FOUND.

---

## REQ-05d — Absent technology is never SUPPORTED

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/prompts/templates.py` | 65–70 | `"NOT_FOUND" — the requirement is clearly absent` and `"NOT_VERIFIED" — the resume neither confirms nor clearly denies it` |
| `ai/prompts/templates.py` | 76–78 | `If the resume supports … ALWAYS quote … so a human can verify` (absence of a quote → NOT_FOUND / NOT_VERIFIED) |
| `ai/agents/verifier.py` | 69–70 | Out-of-vocabulary statuses are coerced to `NOT_VERIFIED`, never inflated to `SUPPORTED` |

No affirmative code guard prevents `SUPPORTED` on an absent term; enforcement is purely through prompt rules and the status allow-list.

**Existing tests**

NONE FOUND.

---

## REQ-06 — Works without an API key (deterministic fallback)

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/pipeline.py` | 183–192 | `def auto_evaluate(…): try: return run_candidate_evaluation(…) except Exception: return heuristic_evaluate(…)` |
| `ai/pipeline.py` | 113–180 | `def heuristic_evaluate(resume_text, job_description) -> CandidateEvaluation:` — entirely regex/set-based, no API call |
| `ai/inference/__init__.py` | 86–97 | `class GeminiClient: … self.client = None` when `api_key` is absent; `available` property returns `False` |
| `pages/7_📋_Candidate_Evaluation.py` | 54–62 | `def get_client(): … if not client.available: st.info("… deterministic fallback mode …")` |
| `pages/7_📋_Candidate_Evaluation.py` | 206–209 | `if client.available: ev = run_candidate_evaluation(…) else: ev = auto_evaluate(…)` |

**Existing tests**

NONE FOUND — no test sets the environment without a key and calls `auto_evaluate` or `heuristic_evaluate`.

---

## REQ-07 — `--heuristic` run is reproducible across PYTHONHASHSEED values

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `ai/pipeline.py` | 128–133 | `# Total order: frequency descending, then term alphabetically. Breaking ties on the term keeps the ranking stable regardless of PYTHONHASHSEED / set iteration order …`<br>`ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))` |
| `evaluation/run_evaluation.py` | 188–189 | `cases = sorted([d for d in CASES_DIR.iterdir() if d.is_dir() …])` — sorted directory iteration eliminates OS ordering variance |
| `evaluation/run_evaluation.py` | 196–204 | `--heuristic` flag paths both `baseline_results` and `agent_results` through `heuristic_evaluate()` |

**Existing tests**

NONE FOUND — no test runs the harness twice with different `PYTHONHASHSEED` and compares output.

---

## REQ-08a — Harness writes `evaluation/baseline_results.json`

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `evaluation/run_evaluation.py` | 237–240 | `(out / "baseline_results.json").write_text(json.dumps(baseline_results, …), encoding="utf-8")` |

File already present in the repository: `evaluation/baseline_results.json`.

**Existing tests**

| File | Lines | Note |
|------|-------|------|
| `evaluation/validate_evaluation.py` | 25–28 | Checks `baseline_results.json` exists; also validates it contains `cases` and `summary` keys — but the harness currently does not write those keys (it writes per-case dicts directly), so this validator would currently report errors. |

---

## REQ-08b — Harness writes `evaluation/agent_results.json`

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `evaluation/run_evaluation.py` | 241–244 | `(out / "agent_results.json").write_text(json.dumps(agent_results, …), encoding="utf-8")` |

File already present in the repository: `evaluation/agent_results.json`.

**Existing tests**

| File | Lines | Note |
|------|-------|------|
| `evaluation/validate_evaluation.py` | 25–28 | Checks `agent_results.json` exists; same key-shape caveat as REQ-08a. |

---

## REQ-08c — Harness writes `evaluation/comparison.md`

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `evaluation/run_evaluation.py` | 245–250 | `(out / "comparison.md").write_text(f"# Baseline vs Agent comparison\n\n{table}\n\n…")` |

File already present in the repository: `evaluation/comparison.md`.

**Existing tests**

NONE FOUND — `validate_evaluation.py` does not check for `comparison.md`.

---

## REQ-09 — Human review dashboard with Confirm / Reject / Needs-review

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `pages/7_📋_Candidate_Evaluation.py` | 100–117 | `st.data_editor(df, column_config={"Review": st.column_config.SelectboxColumn("Human review", options=["confirm", "reject", "needs_review"], …)})` |
| `ai/models/schemas.py` | 17–18 | `ReviewDecision = Literal["confirm", "reject", "needs_review"]` |
| `pages/7_📋_Candidate_Evaluation.py` | 119–122 | Loop persists selected review back onto each `RequirementVerdict.review` field |

All three actions are wired as `SelectboxColumn` options for every verdict row.

**Existing tests**

NONE FOUND — no test exercises the dashboard or the review-persistence loop.

---

## REQ-10 — JSON export contains requirement, verdict, and reviewer decision

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `pages/7_📋_Candidate_Evaluation.py` | 140–149 | `st.download_button("⬇️ Export evaluation (JSON)", data=json.dumps(ev.to_dict(), …), …)` |
| `ai/models/schemas.py` | 99–100 | `def to_dict(self) -> dict: return asdict(self)` — serializes all fields of `RequirementVerdict` including `requirement`, `status`, and `review` |
| `ai/models/schemas.py` | 114–122 | `CandidateEvaluation.to_dict()` includes the full `verdicts` list |

**Existing tests**

NONE FOUND — no test calls `to_dict()` and checks that `review` is present.

---

## REQ-11 — Original `app.py` remains runnable

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `app.py` | 1–973 | Original Streamlit app, all imports and `st.set_page_config` at lines 1–21 — unchanged |
| `pages/4_🌍_Multi_Language_Resume.py` | — | Additional page, independently runnable |
| `pages/5_📊_Recruiter_Dashboard.py` | — | Additional page, independently runnable |
| `pages/6_🎤_AI_Interview_Coach.py` | — | Additional page, independently runnable |

No structural changes to `app.py` that would prevent `streamlit run app.py` from starting.

**Existing tests**

| File | Lines | Note |
|------|-------|------|
| `test_app.py` | 12, 18–130 | Imports `calculate_score` and `extract_section` directly from `app.py` — if `app.py` had an import error the test suite would fail at collection time. Not a runtime smoke test but provides partial coverage. |

---

## REQ-12 — Batch candidate ranking (Roadmap)

**Implementing code**

| File | Lines | Excerpt |
|------|-------|---------|
| `pages/5_📊_Recruiter_Dashboard.py` | 61–72 | `def rank_candidates(client, job_desc, resumes) -> list:` — accepts multiple resumes, returns LLM-scored list |
| `pages/5_📊_Recruiter_Dashboard.py` | 113 | `results = sorted(results, key=lambda r: r.get("score", 0), reverse=True)` |

A partial implementation exists in the Recruiter Dashboard page. It ranks by an LLM-generated score (0–100), not by verified-requirement coverage as specified. The acceptance criterion (sort by *verified-requirement coverage*) is not met by the current implementation.

**Existing tests**

NONE FOUND.

---

## REQ-13 — Timestamped audit log (Roadmap)

**Implementing code**

NONE FOUND — no audit log file, no timestamp-writing code, no log module in the codebase.

**Existing tests**

NONE FOUND.
