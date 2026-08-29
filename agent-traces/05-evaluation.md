# 05 — Evaluation

## Objective
Create a controlled benchmark to compare the baseline evaluator with the evidence-based pipeline using the same case set for both systems.

## Method
- Build a small but representative set of candidate profiles and job descriptions.
- Add gold-truth expected evidence for each requirement.
- Score the baseline and agent outputs against the same expected labels.
- Report accuracy, false positives, and false negatives.

## Key result
The final benchmark shows a measurable improvement:

| Metric | Baseline | Agent | Improvement |
| --- | ---: | ---: | ---: |
| Evidence accuracy | 74.51% | 88.24% | +13.73% |
| False-positive claims | 7 | 2 | -5 |
| False-negative misses | 1 | 0 | -1 |

## Conclusion
The evaluation suite successfully demonstrates that the evidence pipeline is more trustworthy and less prone to hallucinated requirement matches than the single-pass baseline.
