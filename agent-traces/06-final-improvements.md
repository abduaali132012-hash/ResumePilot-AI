# Agent Trajectory 06 — Final Improvements & Integration

> Format: **instruction → tool call → tool response → reasoning → feedback /
> retries / human checkpoints.**

---

## Instruction

> Finalise the agent for the hackathon submission: integrate it into the app as a
> recruiter-facing dashboard, harden the inference layer against the recurring
> quota/retired-model failures, and make the whole thing resilient enough to demo
> live. Keep the baseline intact and runnable.

## Tool call 1 — read the inference client

**Tool:** `read_file` on `ai/inference/__init__.py` and `ai/inference/gemini_client.py`
**Response (issue found):** `gemini_client.py` was a re-export that imported from
itself (`from ai.inference.gemini_client import ...` inside the same module) —
a circular import that fails when the module is imported directly.

**Reasoning:** any direct import of `ai.inference.gemini_client` (tests, notebooks,
the README's reproduction snippet) would crash. Fix the re-export to source from
the package, so both import styles work.

## Tool call 2 — fix the broken re-export + key resolution

**Tool:** `edit_file`
**Response:** written.
- `gemini_client.py` now re-exports from `ai.inference` (no self-import).
- `get_api_key()` now falls back to reading the git-ignored
  `.streamlit/secrets.toml` directly (via `tomllib`) when not running inside
  Streamlit, so the **CLI evaluation harness** picks up a key placed in the app's
  documented secrets file — one location for both the UI and the harness.

**Reasoning:** REPRODUCTION.md tells users to put the key in
`.streamlit/secrets.toml`; without this fallback that instruction only worked for
the Streamlit app, not the CLI harness. Now it works for both.

## Tool call 3 — harden the client (quota + parsing + fallback)

**Tool:** `edit_file` on the inference layer
**Response:** client now:
- Retries transient failures but **never retries daily-quota exhaustion** (429
  "per day") — retrying just wastes what's left;
- Tolerates ``` fences and stray prose in model JSON (`parse_json`);
- **Auto-degrades** to the deterministic keyword evaluator when Gemini is
  unavailable/out of quota, so the app and harness never crash.

**Reasoning:** the recurring 429 quota errors were the single biggest live-demo
risk; the resilience rules came from the earlier baseline traces.

## Tool call 4 — migrate all pages off the retired model

**Tool:** `edit_file` on `pages/4,5,6` (+ page 7)
**Response:** all pages now use `gemini-2.5-flash` via the shared `GEMINI_MODEL`
default instead of the hardcoded, retired `gemini-2.0-flash`.

**Reasoning:** `gemini-2.0-flash` returns HTTP 404 — it is retired. This was a
pre-existing landmine from Trace 01; fixing it keeps the baseline pages runnable.

## Tool call 5 — build the recruiter review dashboard

**Tool:** `create_file` → `pages/7_📋_Candidate_Evaluation.py`
**Response:** written — a human-in-the-loop surface for the agent output:
- coverage gauge + per-requirement evidence table;
- Confirm / Reject / Needs-review per verdict (persisted + exportable);
- per-requirement expanders showing the exact supporting quotes;
- JSON export of the full evaluation including human decisions.

**Reasoning:** the agent's value is *auditability*; the dashboard is what makes
that visible. Human review is part of the design (Experiment 3), not a bolt-on.

## Human checkpoint

- **Feedback received:** "The submission must tell the whole story — traces 01–06,
  changelog, README, REPRODUCTION and the demo script must all describe the
  candidate-evaluation agent, not the old resume app. Also re-verify build and
  evaluation still pass after the finalisation edits."
- **Agent response:** Aligned the narrative across all six traces and the docs;
  rewrote the demo video script for the agent story (≤5 min); verified
  `npm run build` and `python evaluation/run_evaluation.py --heuristic` both pass
  after the changes.

## Retries / issues

- Direct import of `gemini_client.py` crashed (circular self-import) — fixed in
  Tool call 2 and verified with `python -c "import ai.inference.gemini_client"`.
- The demo script originally described the old ATS resume app; rewritten to the
  agent story (candidate evaluation + quoted evidence + human review).

## Artifact produced by this trajectory
- `pages/7_📋_Candidate_Evaluation.py` (recruiter review dashboard)
- Hardened `ai/inference/` (quota guard, JSON tolerance, key fallback, degraded
  mode, fixed re-export)
- Model fix to `gemini-2.5-flash` across all pages
- Final narrative alignment (traces, changelog, README, REPRODUCTION, demo script)
