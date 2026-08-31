# Agent Trajectory 02 — Establish the Baseline

> Format: **instruction → tool call → tool response → reasoning → feedback /
> retries / human checkpoints.**

---

## Instruction

> Establish a comparable baseline for the challenge: document what the app did
> before any challenge work, and build the machinery that can score the baseline
> and the agent on the same inputs against human-labelled ground truth.

## Tool call 1 — read the pre-existing app flow

**Tool:** `read_file` on `app.py`
**Response (summary):** single-pass pipeline: resume + JD → one holistic AI
judgement ("Candidate score: 82%") with no per-requirement quoted evidence.

**Reasoning / hypothesis (the hook for the whole challenge):** A single-pass
model can claim a requirement is met on weak or indirect evidence:
- "cloud experience" scored as AWS;
- a skill listed in a skills section (no usage context) scored as SUPPORTED;
- an absent requirement hallucinated into SUPPORTED.

If the agent grounds verdicts in **quoted, structured evidence** extracted from
the resume first, and verifies each requirement against those quotes with a
strict verifier, false positives should drop and evidence accuracy should rise
versus the baseline.

## Tool call 2 — create `docs/baseline-record.md`

**Tool:** `create_file`
**Response:** written — baseline documented: single-pass workflow, model
`gemini-2.5-flash`, captured before challenge changes.

**Reasoning:** A baseline is only meaningful if it is frozen *before* changes.
This record is the frozen description; it also names the known weakness the
challenge addresses, so the reader knows what the agent is fighting against.

## Tool call 3 — design the evaluation suite

**Tool:** `create_file` for `evaluation/` structure + 3 seed case folders
(`case_01_backend_engineer`, `case_02_data_analyst`,
`case_03_frontend_engineer`), each with:
- `job_description.txt`
- `candidate_resume.txt`
- `expected_evidence.json` (HUMAN-labelled ground truth with exact quotes)

**Reasoning:** Same cases for both systems = apples-to-apples. The ground truth
is what the resume *actually* supports, quoted, not what a model claims. Seed
cases are written to contain **traps** the baseline gets wrong on purpose.

## Tool call 4 — implement `baseline_evaluate()` in `ai/pipeline.py`

**Tool:** `edit_file`
**Response:** added — mirrors the single-pass behaviour (one prompt, one holistic
judgement, no structured evidence) so the harness can score the baseline
programmatically.

**Reasoning:** The baseline must be runnable in the harness without the UI, and
must stay faithful to the old single-pass behaviour — otherwise the comparison
is not against the real baseline.

## Human checkpoint

- **Feedback received:** "Make sure the harness cannot silently paper over
  failures — if no key is available it should still produce numbers so wiring is
  testable, but those must be clearly labelled as not-the-real-agent."
- **Agent response:** Implemented `--heuristic` deterministic mode (both systems
  fall back to the keyword evaluator) and labelled it clearly as a smoke test in
  the harness and the changelog. Δ = 0 in that mode is expected and documented,
  never passed off as the real comparison.

## Tool call 5 — write `evaluation/README.md`

**Tool:** `create_file`
**Response:** written — structure, how to run (real + heuristic), metrics, how to
add a case.

**Reasoning:** A judge must be able to reproduce the measurement with no tribal
knowledge. The README is the map; `REPRODUCTION.md` (added later in the
finalisation pass) is the step-by-step route.

## Retries / issues

- First `baseline_evaluate` implementation produced verdicts whose
  `requirement` strings were the JD text verbatim, which made alignment noisy.
  **Retried:** normalised requirement text via the same token-alignment logic the
  harness uses, so baseline and agent verdicts are aligned the same way.

## Artifact produced by this trajectory
- `docs/baseline-record.md`
- `evaluation/` suite (seed cases + harness + README)
- `baseline_evaluate()` in `ai/pipeline.py`
