# ResumePilot AI - Hackathon MVP

> Working scope proposal for team agreement. Reuse the existing candidate-evaluation workflow; do not rebuild the app.
>
> Hackathon: IBM Bob 2.0, September 25-27, 2026. The event page showed submissions open and an end-of-event countdown on September 26. Confirm the exact submission cutoff in the event portal before planning the final demo.

## 1. Problem

Recruiters compare resumes against job descriptions under time pressure. A single match score does not show whether a candidate's experience actually supports each requirement, making false positives difficult to catch.

## 2. Target User

Recruiters screening one candidate against one job description. The MVP is decision support, not automated rejection or candidate ranking.

## 3. Solution

ResumePilot extracts job requirements, finds resume evidence, evaluates each requirement, and presents evidence and verdicts for human review. The recruiter gets an auditable first pass rather than an unexplained score.

## 4. User Workflow

1. Open **Candidate Evaluation**.
2. Upload a TXT, PDF, or DOCX resume, or paste resume text.
3. Paste the job description.
4. Run the evaluation.
5. Review requirements, verdicts, evidence quotes, and confidence.
6. Confirm, reject, or flag each verdict for review.
7. Export the reviewed evaluation as JSON.

## 5. Core Features

- Resume and job-description input with validation for empty input.
- Requirement extraction, evidence extraction, matching, and verification.
- Per-requirement statuses: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `NOT_VERIFIED`, and `NOT_FOUND`.
- Visible evidence quotes and human review controls.
- JSON export including review decisions.
- Deterministic fallback when Gemini is unavailable; the UI must identify fallback results as heuristic, not present them as equivalent to agent results.

**Existing implementation:** `pages/7_📋_Candidate_Evaluation.py` and `ai/pipeline.py` already provide the core flow. Keep the demo focused on this page; the resume-optimization and other dashboard pages are outside this MVP.

## 6. AI Workflow

1. `RequirementExtractor` turns the job description into requirements.
2. `EvidenceExtractor` finds quoted claims and source context in the resume.
3. `Matcher` selects relevant evidence for each requirement.
4. `Verifier` assigns a status and explanation based on the matched evidence.
5. The page displays results for recruiter review; the human owns the final decision.

## 7. Human Review

The recruiter can set each result to `confirm`, `reject`, or `needs_review`. The export should preserve the original AI verdict, evidence, and review choice. Do not market an unreviewed model result as a hiring decision.

## 8. Team Responsibilities

- **Abdu (Product/MVP, research, integration, documentation/demo):** keep the scope user-centered, maintain this plan, prepare the demo, and verify results reach the page and export.
- **Arshad_99 (AI/backend):** own agent architecture, prompts, schemas, and pipeline behavior; flag changes that affect result interpretation.
- **Naheed (project management/QA):** prioritize tasks, coordinate ownership, and track acceptance checks and demo blockers.

These assignments reflect the proposed team roles and should be confirmed by the team.

## 9. Testing Requirements

| Scenario | Expected result |
|---|---|
| Resume and job description supplied | Evaluation completes and results render. |
| Empty resume or job description | Friendly validation message; no pipeline call. |
| PDF, DOCX, and TXT inputs | Text is extracted, or a clear recovery message is shown. |
| Python and FastAPI described in work experience | Evidence quote is shown and the expected verdict is supported. |
| Generic cloud-hosting claim, no named AWS service | Must not be treated as strong AWS evidence; the labelled fixture expects `PARTIALLY_SUPPORTED`. |
| Message queue absent from resume | `NOT_FOUND`, with no invented supporting quote. |
| Skill appears only in a skills list | Do not claim strong experience without contextual evidence. |
| Gemini unavailable | Evaluation remains usable, and heuristic mode is clearly disclosed. |
| Human review changed before export | Export contains the review choice. |

Run the existing labelled evaluation cases in `evaluation/cases/` for evidence-quality checks. Heuristic-mode smoke tests prove wiring and determinism only; they do not measure Gemini-agent accuracy. Do not claim an accuracy improvement until the real comparison has been run and recorded.

## 10. Demo Scenario

Use the existing Backend Engineer fixture in `evaluation/cases/case_01_backend_engineer/` rather than creating a second synthetic resume. It includes Python, FastAPI, PostgreSQL, Kubernetes, Docker, automated tests, a generic cloud claim, and no message-queue evidence.

Demo the recruiter workflow and call attention to two meaningful checks: generic cloud hosting should not be inflated into definite AWS experience (the labelled target is `PARTIALLY_SUPPORTED`), and absent message-queue evidence should remain `NOT_FOUND`. Show the resume quote, change one review decision, and export JSON. Treat these as acceptance expectations to verify against the live model, not guaranteed model output.

## 11. Future Improvements

- Persistent review history and multi-candidate comparison.
- More labelled cases for ambiguous, compound, and conflicting requirements.
- Better parsing and recovery for scanned or malformed resumes.
- Additional audit and fairness evaluation before any production hiring use.

## Integration and Demo Risks

- The deployed URL could not be verified in the current browser session: it showed the Streamlit shell/loading state and 403/404 resource errors. Confirm the Cloud deployment and public page before recording or presenting the demo.
- `ai/inference` accepts `GOOGLE_API_KEY` or `GEMINI_API_KEY`; the legacy root `app.py` initialization reads only `GEMINI_API_KEY`. Use the Candidate Evaluation page for this MVP and set the required key in Streamlit Cloud Secrets, never in a committed file.
- The agent comparison in the README is pending a real Gemini run. Keep results labeled by mode and avoid presenting heuristic output as agent validation.

## References

- [IBM Bob 2.0 hackathon](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/live)
- [Candidate evaluation page](../pages/7_%F0%9F%93%8B_Candidate_Evaluation.py)
- [Agent pipeline](../ai/pipeline.py)
- [Evaluation cases](../evaluation/cases/)