# Micro1 — Git Workflow (do this on your machine)

The code for the challenge is ready in this repo. This page is the exact
sequence to isolate it on a dedicated branch, verify it, and push it — keeping
the challenge work cleanly separate from the pre-existing ResumePilot history.

> ℹ️ All the code below is already written and lives alongside this doc:
> the `ai/` package, the candidate-evaluation page, the `evaluation/` suite,
> the notebooks, and the challenge docs.

## 1. Create the challenge branch (from `main`)

Open a terminal in your ResumePilot-AI folder (or a Codespace) and run:

```bash
git checkout -b micro1-candidate-evaluation
```

Verify you're on it:

```bash
git branch
```

You should see `* micro1-candidate-evaluation` (the `*` means it's active).

## 2. Baseline record (before touching anything)

The baseline is already documented in `docs/baseline-record.md` — it describes
the pre-existing single-pass workflow, captured before challenge changes.

## 3. Install dependencies and run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

The existing ResumePilot opens at http://localhost:8501 — this proves the
baseline still works.

## 4. Try the new Candidate Evaluation page

In the Streamlit sidebar you'll now see **📋 Candidate Evaluation**. Paste a
candidate resume + a job description and run it. It uses `GOOGLE_API_KEY` from
`.streamlit/secrets.toml` (same key as the rest of the app). If the key is
missing it falls back to a deterministic evaluator so nothing crashes.

## 5. Run the evaluation harness (real numbers)

From the repo root:

```bash
GOOGLE_API_KEY="AIza..." python evaluation/run_evaluation.py
```

This writes `evaluation/baseline_results.json`, `evaluation/agent_results.json`
and `evaluation/comparison.md`. Paste the resulting table into
`docs/improvement-changelog.md` replacing the placeholders.

## 6. Commit and push

```bash
git add .
git commit -m "Micro1: evidence-based candidate evaluation agent (requirements→evidence→verification→review)"
git push -u origin micro1-candidate-evaluation
```

## 7. Open a Pull Request (main ← micro1-candidate-evaluation)

On GitHub, open the repo → the banner will offer to create a PR. Title it
something like:

> **Frontier Engineering Challenge 2026 — Evidence-Based Candidate Evaluation**

and reference `docs/improvement-changelog.md` + `agent-traces/` in the body.

---

## What's included in this branch

| Path | Purpose |
|------|---------|
| `ai/` | Agent package: models, inference (resilient Gemini client), prompts, agents (RequirementExtractor, EvidenceExtractor, Matcher, Verifier), `pipeline.py` |
| `pages/7_📋_Candidate_Evaluation.py` | Recruiter review dashboard for the agent |
| `evaluation/` | Controlled baseline-vs-agent harness + 3 labelled cases |
| `notebooks/` | GPU-prep notebooks (ROCm / PyTorch / Hugging Face) |
| `docs/` | `baseline-record.md`, `improvement-changelog.md`, this file |
| `agent-traces/` | The representative agent trajectory log |
| `pages/4,5,6` | Fixed deprecated `gemini-2.0-flash` → `gemini-2.5-flash` |
