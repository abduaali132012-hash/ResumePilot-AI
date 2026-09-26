# Requirements Report

Source: `speccheck/PRD.md` — ResumePilot AI v1.0

| ID | Requirement | Acceptance Criterion | Type | Testable |
|----|-------------|----------------------|------|----------|
| REQ-01 | The RequirementExtractor turns a job description into a typed list of requirements. | Compound items such as "Python and FastAPI" are split into separate requirements. | Functional | Yes |
| REQ-02 | The EvidenceExtractor reads a resume and outputs structured claims `{skill, exact quote, source section, confidence}`. | The extractor never produces a score or verdict; every claim includes a quote taken verbatim from the resume. | Functional | Yes |
| REQ-03 | The Matcher shortlists candidate quotes for each requirement using deterministic logic (no LLM call). | The same inputs always produce the same shortlist. | Functional | Yes |
| REQ-04 | The Verifier returns exactly one of `SUPPORTED \| PARTIALLY_SUPPORTED \| NOT_VERIFIED \| NOT_FOUND` for every requirement, plus the supporting quotes. | No requirement is left without a verdict; any non-NOT_FOUND verdict includes at least one quote. | Functional | Yes |
| REQ-05a | The Verifier must not mark a skill as SUPPORTED when it appears only in a skills list with no usage context. | A skill listed without usage context is not SUPPORTED. | Functional | Yes |
| REQ-05b | The Verifier must not treat a generic phrase as a specific technology (e.g. "cloud experience" is not AWS). | "cloud experience" does not resolve to an AWS verdict of SUPPORTED. | Functional | Yes |
| REQ-05c | The Verifier must not treat qualified experience phrases as full experience (e.g. "working knowledge of X" is not full X experience). | "working knowledge of X" is not given the same verdict as demonstrated X experience. | Functional | Yes |
| REQ-05d | The Verifier must never return SUPPORTED for a technology that is absent from the resume. | An absent technology always receives NOT_FOUND, never SUPPORTED. | Functional | Yes |
| REQ-06 | If `GOOGLE_API_KEY` is absent, the app and pipeline fall back to a deterministic evaluator. | No crash occurs and a valid result is returned when no API key is set. | Reliability | Yes |
| REQ-07 | `python evaluation/run_evaluation.py --heuristic` runs the 10 labelled cases and produces byte-identical results across repeated runs. | Results are byte-identical across repeated runs and different `PYTHONHASHSEED` values. | Reliability | Yes |
| REQ-08a | The evaluation harness writes `evaluation/baseline_results.json` after a run. | The file exists after `run_evaluation.py` completes. | Reliability | Yes |
| REQ-08b | The evaluation harness writes `evaluation/agent_results.json` after a run. | The file exists after `run_evaluation.py` completes. | Reliability | Yes |
| REQ-08c | The evaluation harness writes `evaluation/comparison.md` after a run. | The file exists after `run_evaluation.py` completes. | Reliability | Yes |
| REQ-09 | The Candidate Evaluation page lets a reviewer mark each verdict as Confirm / Reject / Needs-review. | All three actions are available for every verdict in the UI. | UX | Yes |
| REQ-10 | Reviewer decisions can be exported as JSON. | The export contains each requirement, its verdict, and the reviewer's decision. | UX | Yes |
| REQ-11 | The original ResumePilot resume-optimization app (`app.py` and its pages) remains runnable. | `streamlit run app.py` starts without errors. | Reliability | Yes |
| REQ-12 | A recruiter can evaluate several resumes against one job description and receive a ranked list. | Given N resumes, the output is a list of N candidates sorted by verified-requirement coverage. | Roadmap | No |
| REQ-13 | Every verdict and every reviewer decision is written to a timestamped audit log file. | After an evaluation and a review, the log contains one entry per verdict and per decision, each with a timestamp. | Roadmap | No |
