# 02 — Baseline

## Objective
Establish a baseline evaluator that marks requirements as supported, partially supported, or not verified using a single-pass interpretation of the resume against the job description.

## Observed failure mode
The single-pass baseline tends to over-claim support when the resume only contains weak context or vague similarity. It frequently mistakes indirect references for direct evidence.

## Example issue
A requirement like Kubernetes, AWS, GraphQL, or Customer Research can be incorrectly treated as supported even when the resume never provides explicit proof or only alludes to the concept.

## Result
The baseline benchmark produced:
- Evidence accuracy: 74.51%
- False-positive claims: 7
- False-negative misses: 1

## Conclusion
This baseline is usable as a starting point, but it is not reliable enough for a strong hackathon claim because it lacks an evidence gate and tends to inflate confidence.
