# SpecCheck Demo Script

## 1. Introduction — 20 seconds

Hello, I'm Abdu, and this is SpecCheck.

SpecCheck is a development-time workflow for verifying software against
written product requirements.

For this demonstration, we use ResumePilot AI as the target project.

An important point is that we did not modify the ResumePilot AI application
code for this evaluation.

---

## 2. Requirements — 30 seconds

We start with the product requirements in:

`speccheck/PRD.md`

These requirements are converted into a structured requirements set.

Here we can see the 18 requirements used for the evaluation.

The corresponding requirements report is:

`speccheck/reports/01_requirements.md`

This gives us an explicit starting point for traceability.

---

## 3. Evidence and Verification — 60–90 seconds

Next we move to:

`speccheck/reports/02_evidence.md`

This report connects individual requirements to evidence found in the
repository.

The evidence includes file and line references where available.

Next is:

`speccheck/reports/03_verdicts.md`

This is where the requirements receive verification verdicts based on the
available evidence.

The workflow also identifies cases that require stricter verification.

---

## 4. Tests — 45 seconds

Next we look at:

`speccheck/reports/04_tests.md`

This connects requirements with tests and identifies test-backed coverage.

The evaluation resulted in:

- 50 passed
- 6 skipped
- 12 strict xfailed

for 62 labeled test cases.

The strict xfail cases are intentionally preserved as cases where the
current implementation does not satisfy the required verification condition.

---

## 5. Final Traceability Report — 45–60 seconds

Finally, we open:

`speccheck/reports/05_TRACE_REPORT.md`

This brings the previous stages together into a final traceability view.

The test-backed requirement coverage increased from:

5.6 percent, or 1 of 18 requirements,

to:

38.9 percent, or 7 of 18 requirements.

This metric represents test-backed requirement coverage.

It should not be interpreted as a measure of overall AI accuracy or proof
that the application is completely correct.

---

## 6. Limitations — 30 seconds

There are limitations to this evaluation.

The clean-checkout evaluation harness has an issue, so we do not run
`evaluation/run_evaluation.py` live during this demonstration.

We also preserve the reported test breakdown rather than presenting it as
proof of complete software correctness.

Most importantly, the demonstration does not modify the ResumePilot AI
application code.

---

## 7. Closing — 15 seconds

SpecCheck provides a traceable workflow from written requirements to
repository evidence, verification, tests, and a final report.

The goal is to make software requirement verification more explicit,
reproducible, and easier to inspect.
