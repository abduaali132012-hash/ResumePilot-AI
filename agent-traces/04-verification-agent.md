# Agent Trajectory 04 — Verification Agent

> Format: **instruction → tool call → tool response → reasoning → feedback /
> retries / human checkpoints.**

---

## Instruction

> Make the system strict about weak evidence. A skill in a skills list with no
> usage context must NOT be "SUPPORTED"; "working knowledge of GraphQL (read
> queries)" is NOT GraphQL experience. Build the verifier and the matcher that
> feeds it.

## Tool call 1 — read the requirement extractor (existing)

**Tool:** `read_file` on `ai/agents/requirement_extractor.py`
**Response:** already extracts a typed list of `Requirement` (text, category,
importance) from the JD and splits compound items ("Python and FastAPI" → two
requirements).

**Reasoning:** Good — the requirements side is in place. What's missing is a way
to map each requirement to candidate quotes (matcher) and to pass strict judgment
(verifier).

## Tool call 2 — create the deterministic Matcher (`ai/agents/matcher.py`)

**Tool:** `create_file`
**Response:** written.

**Design decisions (reasoning):**
- The matcher is **deterministic (no API call)** — it shortlists candidate
  evidence quotes per requirement via token overlap.
- It is deliberately **generous**: nothing relevant should be dropped at this
  stage. Strictness is left to the verifier, so the matcher's false-negatives
  don't silently remove evidence the verifier could have used.

## Tool call 3 — create the Verifier (`ai/agents/verifier.py`)

**Tool:** `create_file`
**Response:** written.

**Verifier contract:** for every requirement, return
`SUPPORTED | PARTIALLY_SUPPORTED | NOT_VERIFIED | NOT_FOUND` **plus the exact
supporting quotes** and a one-line human-readable note.

**Anti-inflation rules baked into the verifier prompt (reasoning):**
- A skill in a skills list with no usage context is **not** SUPPORTED.
- "Cloud experience" is **not** evidence of AWS.
- "Led projects" is **not** people management unless it says so.
- If supported, the verdict MUST quote the exact sentence.

**Why:** the verifier is the second half of the evidence-grounding hypothesis
(Trace 02). Even with great extracted evidence, a loose judge inflates — these
rules are the enforcement layer that targets baseline false positives directly.

## Tool call 4 — wire into the pipeline

**Tool:** `edit_file` on `ai/pipeline.py`
**Response:** `run_candidate_evaluation()` now chains
RequirementExtractor → EvidenceExtractor → Matcher → Verifier, with a safe
fallback (if no requirements/evidence, every requirement is NOT_VERIFIED with a
clear note — never a crash).

## Human checkpoint

- **Feedback received:** "The verifier must be strict but not paranoid — a
  genuinely supported requirement must still be SUPPORTED. Don't overcorrect into
  false negatives."
- **Agent response:** Addressed by the four-status scheme: `PARTIALLY_SUPPORTED`
  exists precisely so indirect-but-real evidence ("cloud" without AWS) is
  recorded as a partial, not thrown away as NOT_FOUND. Verified in the prompt:
  the statuses and their exact meaning are enumerated for the model.

## Retries / issues

- First verifier prompt occasionally emitted statuses outside the enum
  (e.g. "PARTIAL"). **Retried:** changed the harness + verifier to `.upper()`
  and added a normalisation guard so stray casing/whitespace cannot produce an
  invalid status; invalid statuses are mapped to NOT_VERIFIED rather than
  crashing alignment.

## Artifact produced by this trajectory
- `ai/agents/matcher.py` (deterministic shortlister)
- `ai/agents/verifier.py` (strict LLM verifier)
- Pipeline wiring in `ai/pipeline.py`
