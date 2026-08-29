# Step 8 — Requirement Verification Layer

## Goal

Add a verification stage after evidence extraction so each requirement is classified as:
- SUPPORTED
- PARTIALLY SUPPORTED
- NOT VERIFIED

This makes the evaluation explainable and defensible instead of a single opaque score.

## Flow

Requirement
↓
Evidence Matcher
↓
Evidence
↓
Verification

## Verification rules

1. Supported
   - Direct match to a skill, tool, platform, or credential in the resume
   - Example: Python, FastAPI, Docker, PostgreSQL

2. Partially Supported
   - A related or indirect statement exists, but the exact requirement is not explicitly proven
   - Example: Cloud experience mentioned, but AWS is not explicitly named

3. Not Verified
   - No direct or indirect evidence is found
   - Example: Kubernetes appears nowhere in the resume

## Example output

- Python
  - SUPPORTED
  - Evidence: "Developed Python automation scripts for deployment workflows."

- Kubernetes
  - NOT VERIFIED
  - Evidence: no explicit or indirect mention found.

- AWS
  - PARTIALLY SUPPORTED
  - Evidence: "Worked with cloud platforms and deployed services in the cloud."
  - Reason: cloud experience exists, but AWS is not explicitly identified.

## Why this is useful

This avoids the false confidence of a single ATS percentage while still giving a recruiter an actionable breakdown.

The evaluator can explain:
- what was supported,
- what was partially supported,
- what could not be verified.

That is a much stronger signal than a raw score alone.
