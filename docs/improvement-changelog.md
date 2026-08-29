# Improvement Changelog

## Baseline

Single-pass candidate evaluation.

Result:
- Evidence accuracy: 74.51%
- False-positive claims: 7
- False-negative misses: 1

This baseline treated resume requirements as a quick keyword or shallow semantic match. It was fast, but it was prone to over-crediting weak or indirect evidence and missing cases where the resume never directly supported a requirement.

## Experiment 1

Added structured evidence extraction.

Why:
The baseline conflated broad contextual similarity with direct proof. In several cases, the model claimed support for requirements like Kubernetes, AWS, GraphQL, and Customer Research even when the resume only hinted at the area or never named it explicitly. This created false positives and inflated confidence in weak matches.

Result:
- Evidence accuracy: 82.35%
- False-positive claims: 4
- False-negative misses: 0

Decision:
Kept

The evidence extraction step improved classification quality by forcing the system to identify specific resume language before deciding whether a requirement was supported. It reduced over-claiming, though some ambiguous requirements still needed stricter verification rules.

## Experiment 2

Added evidence verification.

Why:
Even after structured extraction, the system still struggled to distinguish between direct evidence, indirect support, and missing proof. This caused a small number of borderline requirements to be labeled as fully supported when they were only partially supported or absent. The key failure was a lack of a verification gate between evidence collection and final classification.

Result:
- Evidence accuracy: 88.24%
- False-positive claims: 2
- False-negative misses: 0

Decision:
Kept

This verification stage was the decisive improvement. It tightened the logic around what counts as support, preserved partial-credit cases, and reduced unsupported requirement claims without sacrificing sensitivity on genuinely present skills.

## Overall takeaway

The experiment log shows a clear pattern:
- Baseline: fast but noisy and overly confident
- Experiment 1: better evidence grounding, fewer hallucinated matches
- Experiment 2: stronger verification logic, best balance of precision and recall

This is the engineering story judges can follow: we started with a single-pass evaluator, then added structured evidence extraction and a final proof check, which reduced false positives and improved requirement classification accuracy from 74.51% to 88.24%.
