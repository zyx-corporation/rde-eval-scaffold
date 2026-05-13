# Data

This directory contains JSONL samples for RDE pilot studies.

Each line is a JSON object with the following fields:

- `id`: stable sample identifier
- `task`: task type, such as `summarization`, `rewriting`, or `specification_conversion`
- `risk_context`: domain or risk context
- `source`: original text or context
- `output`: generated output to evaluate
- `human_annotation`: optional primary RDE label
- `risk_flags`: optional list of human-assigned risk flags
- `notes`: optional annotation notes

The initial `samples.jsonl` file is intentionally small and illustrative. It is not a validated benchmark.
