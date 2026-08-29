# 03 — Evidence Agent

## Objective
Add a structured evidence extraction step so the system identifies actual textual proof in the resume before deciding whether a requirement is supported.

## Design
The evidence agent reads the resume and job requirement, then extracts the exact supporting sentences or phrases that justify the classification. This creates a better bridge between raw resume text and requirement assessment.

## Observed benefit
The evidence-focused step reduces the tendency to label broad contextual similarity as direct evidence. It makes classification more explainable and gives the evaluation a cleaner chain of reasoning.

## Result
The agent improved the benchmark to:
- Evidence accuracy: 82.35%
- False-positive claims: 4
- False-negative misses: 0

## Decision
Kept

This stage materially improved precision by grounding decisions in explicit or near-explicit resume evidence, even though some ambiguous cases still needed a stricter verification pass.
