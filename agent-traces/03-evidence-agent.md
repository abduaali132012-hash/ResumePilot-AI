# Agent Trajectory 03 — Evidence Extraction Agent

> Format: **instruction → tool call → tool response → reasoning → feedback /
> retries / human checkpoints.**

---

## Instruction

> Build the first new agent component: the Evidence Extraction agent. It must
> read a resume and produce structured, **quoted** evidence that the rest of the
> pipeline reasons from.

## Tool call 1 — review the data model

**Tool:** `read_file` on `ai/models/schemas.py`
**Response:** dataclasses available — `Evidence(skill, evidence, source,
confidence)`, `Requirement`, `RequirementVerdict`, `CandidateEvaluation`.

**Reasoning:** I can build on the typed model instead of ad-hoc dicts; the whole
pipeline stays type-safe and the dashboard can render it directly.

## Tool call 2 — check the shared prompt templates

**Tool:** `read_file` on `ai/prompts/templates.py`
**Response:** prompt constants exist (e.g. `REQUIREMENT_EXTRACTION`); no evidence
extraction prompt yet.

**Reasoning:** Add a dedicated prompt for evidence extraction that demands JSON of
the shape `{skill, evidence, source, confidence}`.

## Tool call 3 — create `ai/agents/evidence_extractor.py`

**Tool:** `create_file`
**Response:** written.

**Key design decisions (reasoning):**
- The extractor is **deliberately non-judgemental**: it never scores, it only
  extracts factual claims and quotes. Scoring is the verifier's job later.
- Confidence is assigned to the *evidence* (how explicit the quote is), not to
  the candidate — this keeps the extractor honest.
- Resumes are truncated at 24k chars to protect model context and quota.
- Output shape:

```json
{
  "skill": "Python",
  "evidence": "Built and maintained microservices in Python using FastAPI.",
  "source": "Experience",
  "confidence": "high"
}
```

**Why this design (the reasoning that ties to the hypothesis):** the baseline
reads the whole resume in one pass and forms one holistic opinion. By separating
*what the resume says* from *whether it satisfies the role*, each requirement can
be judged against tangible quotes a human can verify. This is the first half of
the evidence-grounding hypothesis from Trace 02.

## Tool call 4 — run a quick unit smoke test

**Tool:** `run_command_in_sandbox` → import the extractor against a sample resume
**Response:** imports OK; returns a structured list of `Evidence` objects.

## Human checkpoint

- **Feedback received:** "Don't let the extractor make verdict claims — keep it
  neutral, or the verifier stage loses its purpose."
- **Agent response:** Confirmed — the extractor prompt and code contain no status
  vocabulary (no SUPPORTED / NOT_FOUND); it only emits claims + quotes. Verified
  by reading the prompt template.

## Retries / issues

- First prompt produced free-text instead of strict JSON on a sample. **Retried:**
  tightened the prompt to demand only a JSON array and added a `parse_json`
  tolerance path in the client for stray prose/fences (shared with the rest of
  the pipeline).

## Artifact produced by this trajectory
- `ai/agents/evidence_extractor.py`
- Evidence-extraction prompt in `ai/prompts/templates.py`
