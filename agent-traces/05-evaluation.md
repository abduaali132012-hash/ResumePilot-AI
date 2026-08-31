# Agent Trajectory 05 — Evaluation Harness

> Format: **instruction → tool call → tool response → reasoning → feedback /
> retries / human checkpoints.**

---

## Instruction

> Build the harness that measures baseline vs. agent: it must run both systems on
> the same cases against human-labelled ground truth, produce per-case and
> aggregate accuracy + false positives, and write machine-readable results. It
> must also have a deterministic mode so wiring is testable without an API key —
> and it must never silently pass that mode off as the real comparison.

## Tool call 1 — read the existing pipeline entry points

**Tool:** `read_file` on `ai/pipeline.py` and `evaluation/` (if any)
**Response:** `baseline_evaluate()` (single-pass, mirrors the old app) and
`run_candidate_evaluation()` (the agent chain) both exist; no evaluation harness
yet.

**Reasoning:** The harness's only job is to call those two entry points on the
same inputs and score the output. Keeping it a thin caller means the harness can
never drift from the real code paths the UI uses.

## Tool call 2 — create `evaluation/run_evaluation.py`

**Tool:** `create_file`
**Response:** written.

**Design decisions (reasoning):**
- Discovers all `evaluation/cases/*` automatically, so adding a case is just
  adding a folder — no harness edits.
- Aligns every model verdict to the human-labelled `expected_evidence.json` via
  token-overlap matching (same normalisation on both sides).
- Metrics: **evidence accuracy**, **false positives** (claimed SUPPORTED but not
  really), **false negatives**.
- Writes `baseline_results.json`, `agent_results.json`, `comparison.md`.

## Tool call 3 — add `--heuristic` deterministic mode

**Tool:** `edit_file`
**Response:** added — when no API key is available (or `--heuristic` is passed),
both systems fall back to the same deterministic keyword evaluator.

**Reasoning / key integrity decision:** In this mode Δ = 0 is *expected by
construction* (both sides use the same evaluator). The mode exists to prove
wiring + reproducibility, and the harness labels it explicitly as a smoke test,
never as the real agent comparison. This is the honesty rule the whole changelog
depends on.

## Tool call 4 — run the smoke test

**Tool:** `run_command_in_sandbox` → `python evaluation/run_evaluation.py --heuristic`
**Response:** all seed cases load and score; writes the three output files;
per-case accuracy appears in the terminal table.

## Human checkpoint

- **Feedback received:** "QA found the committed results were stale (3 cases,
  46.7%). Regenerate on the full 10-case suite so the committed JSONs and the
  changelog agree."
- **Agent response:** Re-ran `--heuristic` on the 10-case suite → aggregate
  **45.0% / 45.0%**, Δ = 0 (expected). Committed the regenerated
  `baseline_results.json`, `agent_results.json`, `comparison.md` and updated the
  changelog's "Current measured state" table to match.

## Tool call 5 — verify byte-identical determinism across hash seeds

**Tool:** `run_command_in_sandbox` → run 3× with `PYTHONHASHSEED=1/2/3`,
`sha256sum` the outputs
**Response:** all three runs byte-identical (this is the reproducibility guarantee
QA re-verified — see "Reproducibility fix" in the changelog).

**Reasoning:** determinism must hold despite `PYTHONHASHSEED`, because the whole
"we never invent numbers" story depends on a judge getting the same results.

## Retries / issues

- First alignment pass was noisy because requirement strings differed in casing
  between baseline and agent output. **Retried:** moved to a shared token-overlap
  alignment with case-insensitive normalisation so both sides align identically.
- Initial committed JSONs were from a 3-case run (stale). **Retried:** regenerated
  on all 10 cases (see checkpoint above).

## Artifact produced by this trajectory
- `evaluation/run_evaluation.py`
- `evaluation/README.md`
- Regenerated 10-case `baseline_results.json`, `agent_results.json`,
  `comparison.md`
- Determinism guarantee: byte-identical across hash seeds (verified)
