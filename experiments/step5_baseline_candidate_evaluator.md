# Step 5 — Baseline Candidate Evaluator Experiment

## Objective

We are not building five agents yet. The first experiment is a controlled baseline that checks whether the existing ResumePilot flow can correctly decide whether a resume actually supports a job requirement.

Input:
- Resume
- Job description
- Existing Gemini-based analysis

Output of interest:
- Requirement-by-requirement evidence classification
- Whether the AI result matches the actual evidence in the resume

## Primary metric

Evidence-grounded requirement accuracy

For each requirement, we ask three questions:

1. Does the resume provide direct evidence?
2. Does the resume provide indirect evidence?
3. Did the AI classify the requirement correctly?

Formally:

Accuracy = number of correct requirement classifications / total requirement checks

## Evidence labels

- Explicit: direct, concrete proof in the resume
- Indirect: implied or weakly supported through context
- None: no meaningful evidence in the resume
- Conflicting: evidence both supports and contradicts the requirement

## Controlled evaluation set

We will avoid a single resume and instead use a small curated set with known job requirements and known evidence patterns.

### Candidate 1 — Python backend engineer

| Requirement | Resume evidence | Baseline result | Gold label | Notes |
| --- | --- | --- | --- | --- |
| Python | Explicit | Supported | Supported | Clear language and project examples |
| FastAPI | Explicit | Supported | Supported | Named in stack and project list |
| Kubernetes | None | ? | Unsupported | No deployment or orchestration evidence |
| AWS | Indirect | ? | Partially supported | Mentioned via cloud hosting but not direct platform depth |
| Leadership | Indirect | ? | Partially supported | Mentorship implied, not explicit |

### Candidate 2 — DevOps / platform engineer

| Requirement | Resume evidence | Baseline result | Gold label | Notes |
| --- | --- | --- | --- | --- |
| Kubernetes | Explicit | Supported | Supported | Direct orchestration examples |
| Terraform | Explicit | Supported | Supported | Infra-as-code shown in project work |
| Docker | Explicit | Supported | Supported | Containerization experience present |
| AWS | Explicit | Supported | Supported | Hands-on cloud deployment work |
| Python | Indirect | ? | Partially supported | Used as a scripting language, but not core requirement |

### Candidate 3 — Data/ML engineer

| Requirement | Resume evidence | Baseline result | Gold label | Notes |
| --- | --- | --- | --- | --- |
| Python | Explicit | Supported | Supported | Core technical language |
| Machine Learning | Explicit | Supported | Supported | Model training and evaluation included |
| Kubernetes | None | ? | Unsupported | No container orchestration examples |
| SQL | Explicit | Supported | Supported | Data engineering tasks described |
| Spark | Indirect | ? | Partially supported | Some data processing context but not clear mastery |

## Experimental protocol

1. Select a small controlled set of candidate profiles and job descriptions.
2. For each requirement, mark the gold truth manually using the resume text.
3. Run the existing ResumePilot analysis on each candidate-job pair.
4. Record requirement-level results from the AI output.
5. Compare AI classification against the gold label.
6. Compute accuracy, false positives, and false negatives.

## Success criteria

The baseline is acceptable if the evaluation shows:
- High agreement on explicit requirements
- Conservative handling of missing evidence
- Clear separation between supported and unsupported requirements

A weak result is one where the model hallucinates support from generic or indirect wording, or where it fails to mark absent evidence as unsupported.

## What this experiment is meant to reveal

This first experiment answers a core question:

Can the current Gemini-powered evaluator distinguish between actual evidence and vague similarity?

That is the foundational requirement before expanding into multi-agent or multi-step workflows.
