# Data

This directory contains JSONL samples for RDE pilot studies.

Each line is a JSON object. The current schema is backward-compatible with the initial minimal sample format and supports richer pilot annotation fields.

## Required fields

- `id`: stable sample identifier
- `task`: task type, such as `summarization`, `rewriting`, or `specification_conversion`
- `risk_context`: domain or risk context
- `source`: original text or context
- `output`: generated output to evaluate

## Optional annotation fields

- `human_annotation`: primary RDE label
- `risk_flags`: list of human-assigned risk flags
- `criticality`: `low`, `medium`, or `high`
- `explanation`: short explanation for the annotation
- `task_intent`: explicit user or system task intent
- `reconstructed_task_intent`: evaluator-reconstructed task intent when the explicit task is underspecified or conflicting
- `task_intent_notes`: notes explaining why task-intent reconstruction was needed
- `notes`: additional annotation notes

The initial `samples.jsonl` file is intentionally small and illustrative. It is not a validated benchmark.
