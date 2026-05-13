# Pilot Experiment Plan

## Purpose

The pilot study tests whether RDE labels and risk flags can be applied consistently to source-output meaning changes.

This is not intended to validate RDE at scale. It is intended to test the usability of the taxonomy and identify annotation difficulties.

## Initial Design

| Task | N | Main Observations |
|---|---:|---|
| Summarization | 10 | caveat loss, uncertainty loss, claim-strength inflation |
| Rewriting | 10 | intent change, hypothesis-to-assertion drift, value simplification |
| Specification Conversion | 10 | theoretical reduction, responsibility shift, institutional implication loss |

## Per-sample Fields

- `id`
- `task`
- `risk_context`
- `source`
- `output`
- `human_annotation`
- `risk_flags`
- `notes`
- `baseline_scores`

## Baselines

Initial baselines may include:

- semantic similarity / BERTScore
- natural language inference
- factuality evaluation
- generic LLM-as-a-judge

## Metrics

- agreement with human annotation
- recall for `Suspicious Drift`
- recall for `Critical Distortion`
- false-positive rate
- risk flag quality
- explanation quality

## Notes

If only one annotator is available at the beginning, the dataset should be described as pilot annotation rather than validation.
