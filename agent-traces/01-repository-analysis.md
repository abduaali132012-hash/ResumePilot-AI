# Agent Trajectory 01 — Repository Analysis

> Format: every entry shows the **instruction** given to the agent, the **tool
> call** it made, the **tool response** it received, the agent's **reasoning**,
> and any **feedback / retries / human checkpoints** that shaped the next step.

---

## Instruction

> Analyse the existing `ResumePilot-AI` repository before making any challenge
> changes. Identify the current architecture, the stack, what already works, and
> anything that will break if we build on top of it.

## Tool call 1 — list repository files

**Tool:** `read_file` (directory listing)
**Response:**
```
app.py                      # single-file Streamlit app
pages/4_🌍_Multi_Language_Resume.py
pages/5_📊_Recruiter_Dashboard.py
pages/6_🎤_AI_Interview_Coach.py
ai/ ... evaluation/ ... docs/ ... agent-traces/ ...
```

**Reasoning:** The app is a single-pass Streamlit application. The `pages/`
folder contains roadmap features; there is no existing agent package yet. I need
to read the core files to understand the stack and find landmines before
touching anything.

## Tool call 2 — read `app.py` and `pages/4,5,6`

**Tool:** `read_file`
**Response (summary):**
- Stack: Streamlit + `google-genai` (Gemini) + pdfplumber/python-docx +
  pandas/plotly + reportlab.
- `app.py` does one-pass resume vs. JD analysis: ATS score, strengths,
  weaknesses, keyword gaps, interview prep, rewrite, cover letter, career coach.
- The three roadmap pages call model `gemini-2.0-flash`.

**Reasoning / observation (found a bug):** `gemini-2.0-flash` is retired —
calling it returns HTTP 404. Only `app.py` uses the valid `gemini-2.5-flash`.
This is a pre-existing landmine that must be fixed so the app stays runnable.

**Agent feedback loop → checkpoint:** I will *not* silently rewrite the whole
app. The challenge needs a *measurable* improvement, which requires the baseline
to stay intact. Decision: fix the model references, remove the corrupted stray
folder, leave `app.py` untouched, and add the agent as a **separate module +
page**.

## Tool call 3 — inspect the corrupted stray folder

**Tool:** `read_file` on the stray `pages` folder (unquoted)
**Response:** contains truncated duplicate files (corrupted copies of the real
pages).

**Reasoning:** These are duplicates that would confuse the file tree and break
imports. Remove them, keep the real pages.

## Tool call 4 — check the model constant location

**Tool:** `search_in_file` for `gemini-2.0-flash` and the model env override
**Response:** model is chosen via `GEMINI_MODEL` env with default
`gemini-2.5-flash` in the inference layer; the three pages hardcode the retired
name.

## Human checkpoint

- **Feedback received:** "Keep the baseline runnable and comparable; the agent
  must be additive, not a rewrite."
- **Agent response:** Confirmed — this is exactly the plan. The baseline is the
  comparison point; the agent is measured against it in `evaluation/`.

## Decisions recorded (the plan this trace produced)

1. Fix the deprecated model references in `pages/4,5,6` → `gemini-2.5-flash`.
2. Remove the corrupted stray folder.
3. Leave `app.py` untouched (it is the challenge baseline).
4. Add the candidate-evaluation agent as a separate `ai/` package + a new page,
   so the baseline remains runnable and comparable.

**Retries:** none needed — repository reads succeeded first attempt.

## Artifact produced by this trajectory
- `docs/baseline-record.md` (baseline described before challenge changes)
- The decision log above (recorded for the changelog)
