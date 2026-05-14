# Pilot Dataset Design

## Purpose

`pilot_30.jsonl` is the first empirical pilot dataset for the RDE evaluation scaffold.

The dataset is intended for:

- annotation usability checks
- drift-category coverage checks
- deterministic scaffold inspection
- baseline-comparison preparation
- Japanese/English side-by-side human review

The dataset is not a validated benchmark.

## Dataset Structure

The dataset contains 30 records.

| Task | Count |
|---|---:|
| summarization | 10 |
| rewriting | 10 |
| specification_conversion | 10 |

## Label Coverage

The dataset attempts to cover:

- Preserved
- Authorized Transformation
- Suspicious Drift
- Critical Distortion

Milestone 1 does not guarantee balanced statistical coverage.

## Risk Flag Coverage

The dataset attempts to exercise:

- claim_strength_inflation
- uncertainty_loss
- responsibility_shift
- value_simplification
- institutional_implication_loss
- context_drift
- theoretical_reduction

## Japanese Review Fields

The dataset includes Japanese inspection fields:

- `source_ja`
- `output_ja`
- `explanation_ja`
- `task_intent_ja`
- `reconstructed_task_intent_ja`
- `task_intent_notes_ja`

These fields are intended for:

- human review
- annotation inspection
- bilingual semantic comparison
- drift inspection during pilot analysis

The English canonical fields remain the schema authority.

## Placeholder Policy

`baseline_scores` remains a Milestone 1 placeholder.

The dataset may contain empty `{}` objects for schema continuity.

## Non-goals

This dataset does not:

- prove RDE validity
- establish benchmark quality
- provide statistical significance
- establish inter-annotator agreement
- validate prompt-based evaluators

## Future Work

Future milestones may add:

- multi-annotator review
- baseline metric population
- disagreement analysis
- benchmark splits
- regression datasets
