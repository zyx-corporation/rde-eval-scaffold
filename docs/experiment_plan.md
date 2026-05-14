# Pilot Experiment Plan

## Purpose

The pilot study tests whether RDE labels and risk flags can be applied consistently to source-output meaning changes.

This is not intended to validate RDE at scale. It is intended to test the usability of the taxonomy, identify annotation difficulties, and prepare the next empirical phase.

## Initial Design

| Task | N | Main Observations |
|---|---:|---|
| Summarization | 10 | caveat loss, uncertainty loss, claim-strength inflation |
| Rewriting | 10 | intent change, hypothesis-to-assertion drift, value simplification |
| Specification Conversion | 10 | theoretical reduction, responsibility shift, institutional implication loss |

## Per-sample Fields

Required fields:

- `id`
- `task`
- `risk_context`
- `source`
- `output`

Pilot annotation fields:

- `human_annotation`
- `risk_flags`
- `criticality`
- `explanation`
- `task_intent`
- `reconstructed_task_intent`
- `task_intent_notes`
- `notes`
- `baseline_scores`

`baseline_scores` is optional and schema-compatible in Milestone 1. The deterministic heuristic scaffold does not populate or interpret this field. It is reserved for the baseline comparison milestone.

## Task-intent reconstruction

When the explicit task is underspecified or conflicts with the risk context, annotators may reconstruct the task intent. This reconstruction must be recorded rather than silently assumed.

- `task_intent`: explicit user or system task intent.
- `reconstructed_task_intent`: evaluator-reconstructed task intent.
- `task_intent_notes`: explanation of why reconstruction was needed.

## Baselines

Initial baselines may include:

- semantic similarity / BERTScore
- natural language inference
- factuality evaluation
- generic LLM-as-a-judge

## Exploratory outputs

The pilot study should produce exploratory findings rather than final validation claims:

- category usability
- Delta-M axis redundancy or gaps
- differences from baseline distributions
- annotator disagreement patterns
- risk flag quality
- explanation quality

## Notes

If only one annotator is available at the beginning, the dataset should be described as pilot annotation rather than validation.
