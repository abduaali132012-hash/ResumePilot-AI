# Baseline Record

Captured BEFORE any Micro1 (Frontier Engineering Challenge 2026) changes, so the
challenge work is cleanly separable from pre-existing functionality.

| Field | Value |
|-------|-------|
| Project | ResumePilot AI |
| Branch | `main` |
| Existing workflow | Resume + Job Description → single-pass AI analysis → ATS/fit report |
| Analysis model | `gemini-2.5-flash` |
| Date | 2026 (start of challenge window) |
| Challenge changes | None |

## What the baseline does (pre-existing functionality)

- Upload / parse resume (PDF, DOCX, TXT)
- Paste up to 3 job descriptions
- Single-pass Gemini analysis: ATS score, strengths, weaknesses, keyword-gap
  analysis, interview prep, resume rewrite, cover letter, career coach
- Additional tools: job recommendations, LinkedIn profile analyzer, career gap
  analyzer, salary insights, application tracker, version history
- Roadmap pages (Multi-language, Recruiter dashboard, Interview coach)

## Known baseline limitation this challenge addresses

The baseline produces a **single-pass holistic judgement** ("Candidate score:
82%") with no per-requirement, quoted evidence. It can silently claim a
requirement is met on weak or indirect evidence (e.g. "cloud experience" scored
as AWS) — the failure mode this project exists to fix.

## How the baseline is measured

The evaluation suite (`evaluation/`) runs the baseline single-pass evaluator and
the new evidence-based agent over the same controlled cases and compares each
against human-labelled ground truth. See `evaluation/README.md`.
