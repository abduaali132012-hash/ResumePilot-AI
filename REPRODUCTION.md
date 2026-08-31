# Reproduction Guide — Evidence-Based Candidate Evaluation Agent

This guide lets anyone reproduce, from a clean environment, (a) the baseline, (b)
the agentic pipeline, and (c) the measured improvement — exactly as documented in
`docs/improvement-changelog.md`. It covers what data is required, the exact
commands, expected outputs, versions, approximate runtime, and cost.

> Integrity rule: **we never invent numbers.** The evaluation harness only writes
> numbers it actually produced on your machine. If you have no Gemini key, the
> harness still runs in deterministic mode so you can verify wiring — but the
> real agent numbers need a key (step 5).

---

## 1. Requirements

| Tool | Version (tested) | Notes |
|------|------------------|-------|
| Python | 3.10 – 3.12 | 3.12 recommended; the repo pins nothing above 3.12 |
| pip | any recent | |
| OS | Linux / macOS / WSL2 | Windows native works but WSL is smoother for shell commands |
| Gemini API key | — | only needed for the **real** agent run (step 5) |

### Python dependencies (`requirements.txt`)

```
streamlit==1.58.0
pdfplumber>=0.11.4
python-docx>=1.1.2
google-genai>=0.3.0
pandas>=2.2.3
plotly>=5.24.1
reportlab>=4.2.5
```

> The `ai/`, `evaluation/`, and `pages/7_...` code uses only `google-genai`,
> `pandas`, and `streamlit`. `pdfplumber`, `python-docx`, `plotly`, `reportlab`
> are used by the wider ResumePilot app (`app.py`, `pages/4–6`) which stays
> intact as the baseline.

---

## 2. Clean-environment setup

```bash
# 1) Clone
git clone https://github.com/abduaali132012-hash/ResumePilot-AI.git
cd ResumePilot-AI

# 2) Create + activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4) (Optional but recommended) check the suite loads
python -c "import ai, evaluation.run_evaluation; print('imports OK')"
```

---

## 3. Data required

Everything needed is already in the repo — no external download:

| Data | Location | What it is |
|------|----------|-----------|
| 10 job descriptions | `evaluation/cases/case_XX_*/job_description.txt` | Realistic postings with traps |
| 10 candidate resumes | `evaluation/cases/case_XX_*/candidate_resume.txt` | Realistic resumes with weaknesses |
| Ground truth | `evaluation/cases/case_XX_*/expected_evidence.json` | **Hand-labelled** `SUPPORTED / PARTIALLY_SUPPORTED / NOT_VERIFIED / NOT_FOUND` per requirement, with the exact supporting quote |

The cases are deliberately adversarial: "cloud experience" that is not AWS, a
skill listed in a skills section with no usage context, absent technologies that
a careless model might hallucinate into SUPPORTED, and "working knowledge of
GraphQL" that must be PARTIAL, not SUPPORTED. Both the baseline and the agent run
on the **same** cases, so the comparison is always apples-to-apples.

---

## 4. Run the app (the agent in the UI)

```bash
streamlit run app.py
```

Open the **📋 Candidate Evaluation** page (`pages/7_...`), paste a resume and a
job description, and run it. Without a Gemini key it degrades to the
deterministic evaluator (nothing crashes). With a key it runs the full agent
pipeline and shows per-requirement verdicts with the exact supporting quotes, a
coverage gauge, and Confirm / Reject / Needs-review controls.

---

## 5. Run the evaluation (the measured improvement)

### 5a. Wiring + reproducibility smoke test (no key needed)

```bash
python evaluation/run_evaluation.py --heuristic
```

- Runs both systems with the **deterministic** evaluator on all 10 cases.
- Δ = 0 here is expected by construction (both sides use the same evaluator).
- Writes `evaluation/baseline_results.json`, `evaluation/agent_results.json`,
  `evaluation/comparison.md`.
- **Determinism check:** run it three times with different hash seeds —
  `PYTHONHASHSEED=1`, `PYTHONHASHSEED=2`, `PYTHONHASHSEED=3` — and confirm the
  three outputs are byte-identical (`sha256sum`).

```bash
for s in 1 2 3; do
  PYTHONHASHSEED=$s python evaluation/run_evaluation.py --heuristic
  cp evaluation/comparison.md /tmp/comp_$s.md
done
sha256sum /tmp/comp_*.md   # all three hashes must match
```

### 5b. Real agent comparison (needs a Gemini key)

```bash
GOOGLE_API_KEY="AIza..." python evaluation/run_evaluation.py
```

- Runs the **single-pass baseline** (`baseline_evaluate`) and the **agent
  pipeline** (`run_candidate_evaluation`) against Gemini on the same 10 cases.
- Aligns every model verdict to the hand-labelled ground truth and reports
  **evidence accuracy**, **false positives** (claimed SUPPORTED but not really),
  and **false negatives** per case + aggregate.
- Overwrites the same three output files. Paste the printed table into
  `docs/improvement-changelog.md` and `README.md` (the "Real agent comparison"
  sections), replacing the "pending real run" placeholders.

> `GEMINI_API_KEY` is accepted as an alias. The key can live in
> `.streamlit/secrets.toml` (`GOOGLE_API_KEY = "AIza..."`); the inference layer
> reads that file for **both** the Streamlit app and the CLI harness (the harness
> falls back to the same git-ignored secrets file, so one location works for
> both). Alternatively export the environment variable for the CLI run.

---

## 6. Expected output

A terminal table like:

```
| Case | Baseline accuracy | Agent accuracy | Δ | FP (base→agent) |
|------|------------------:|---------------:|:--:|:---:|
| case_01_backend_engineer | 20.0% | ... | ... | ... |
| ... |
| **Aggregate** | **...%** | **...%** | **+...pp** | **... → ...** |
```

Three files are written/overwritten:
- `evaluation/baseline_results.json` — per-case baseline detail (aligned
  requirements, quotes, correctness).
- `evaluation/agent_results.json` — per-case agent detail.
- `evaluation/comparison.md` — the markdown table for the changelog.

The current committed files reflect the last deterministic smoke-test run
(10 cases). After a real-key run, commit the three files plus the changelog/README
table updates.

---

## 7. Tool versions used for the committed results

| Component | Version |
|-----------|---------|
| Python | 3.12.x (results are Python-version-independent for the deterministic path; a real Gemini run depends only on the model) |
| google-genai | >= 0.3.0 |
| Gemini model | `gemini-2.5-flash` (configurable via `GEMINI_MODEL` env var) |
| streamlit | 1.58.0 |
| pandas | >= 2.2.3 |

---

## 8. Runtime & cost (real run)

**Runtime:** the deterministic smoke test completes in seconds (no network). A
full real run makes ~5 Gemini calls per case × 10 cases ≈ **50 calls**; at
3–8 s per call you should budget roughly **3–8 minutes** total.

**Cost:** `gemini-2.5-flash` is among the cheapest Gemini tiers. 50 calls on
short resume/JD inputs (a few thousand tokens each) typically cost well under
**$0.10**. The deterministic path costs nothing. Always set a hard API quota in
the Google AI Studio console if you are cost-sensitive.

**Reproducibility caveat:** model temperature is not set to 0 for generation
(verdict wording can vary run-to-run), so the *exact* per-case verdict strings
may differ between runs. What is reproducible is the **procedure** (same cases,
same harness, same alignment) and, for the deterministic path, byte-identical
outputs. If you need strict numeric reproducibility for the real run, set a fixed
`temperature=0` in `ai/inference/__init__.py` (the retry wrapper already accepts
a `temperature` kwarg).

---

## 9. Common problems

| Symptom | Fix |
|---------|-----|
| `No module named 'streamlit'` | Activate the venv / `pip install -r requirements.txt` |
| `Gemini client is not available` | Export `GOOGLE_API_KEY` (or `GEMINI_API_KEY`), or add it to `.streamlit/secrets.toml` |
| HTTP 404 `not found` on model | Set `GEMINI_MODEL` to a current model name (default `gemini-2.5-flash`) |
| Daily quota (HTTP 429 "per day") | The client does not retry daily-quota errors by design; wait for reset or raise the quota |
| The app crashes on Gemini errors | It shouldn't — `auto_evaluate()` falls back to the deterministic evaluator; check `st.secrets` config if it does |
