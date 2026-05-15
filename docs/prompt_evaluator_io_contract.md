# Prompt Evaluator I/O Contract

## Purpose

This document defines the narrow I/O contract for the Milestone 2 prompt-based RDE evaluator.

The goal is to stabilize:

- prompt inputs
- normalized outputs
- failure handling
- provenance tracking
- JSONL persistence

before implementing live prompt-based evaluation.

This document does not define a prompt template or model integration.

## Scope

The evaluator consumes records derived from `pilot_30.jsonl` and produces normalized annotation JSONL records.

## Prompt Input Fields

### Canonical English fields

The following fields are canonical prompt inputs:

- `id`
- `task`
- `risk_context`
- `source`
- `output`
- `task_intent`
- `reconstructed_task_intent`
- `task_intent_notes`

These fields are schema authority.

### Japanese support fields

The following fields may optionally be passed into Japanese-first evaluator prompts:

- `source_ja`
- `output_ja`
- `task_intent_ja`
- `reconstructed_task_intent_ja`
- `task_intent_notes_ja`

Japanese fields are supplementary and must not replace canonical English fields.

## Output Record Schema

### Successful normalized record

```json
{
  "id": "pilot-sum-001",
  "annotator_type": "llm",
  "annotator_id": "deepseek",
  "model": "deepseek-r1",
  "prompt_version": "rde-prompt-eval-v1",
  "annotation_run_id": "deepseek-r1-20260514",
  "llm_annotation": "Suspicious Drift",
  "risk_flags": [
    "claim_strength_inflation",
    "uncertainty_loss"
  ],
  "criticality": "medium",
  "explanation": "...",
  "explanation_ja": "...",
  "raw_output": "...",
  "normalization_status": "ok"
}
```

## Failure Record Schema

Failed normalization results must still be persisted.

```json
{
  "id": "pilot-sum-001",
  "annotator_type": "llm",
  "annotator_id": "deepseek",
  "model": "deepseek-r1",
  "prompt_version": "rde-prompt-eval-v1",
  "annotation_run_id": "deepseek-r1-20260514",
  "normalization_status": "failed",
  "error_type": "invalid_json",
  "error_message": "Model output was not valid JSON.",
  "raw_output": "..."
}
```

## Normalization Rules

### Label normalization

`llm_annotation` must be one of:

- `Preserved`
- `Authorized Transformation`
- `Inferred Extension`
- `Unresolved Gap`
- `Suspicious Drift`
- `Critical Distortion`

Unknown labels must produce a failed normalization record unless explicitly mapped through a documented alias table.

## Risk flag normalization

`risk_flags` must contain only canonical identifiers:

- `claim_strength_inflation`
- `uncertainty_loss`
- `responsibility_shift`
- `value_simplification`
- `institutional_implication_loss`
- `context_drift`
- `theoretical_reduction`

Unknown flags must produce a failed normalization record unless explicitly mapped.

## Criticality normalization

`criticality` must be:

- `low`
- `medium`
- `high`

## Raw Output Preservation

Raw model output must always be preserved.

The evaluator must not discard:

- malformed JSON
- partial outputs
- ambiguous outputs
- normalization failures

## Failure Handling

Failed outputs must remain auditable.

The evaluator must not silently drop failed evaluations.

Each failed evaluation must be written as a JSONL record with:

```text
normalization_status = "failed"
```

## Provenance Preservation

The evaluator must preserve provenance metadata.

Required provenance fields:

- `annotator_type`
- `annotator_id`
- `model`
- `prompt_version`
- `annotation_run_id`

Prompt-based annotations remain separate from:

- human annotations
- adjudicated annotations
- benchmark labels

## Non-goals

This specification does not:

- define prompt templates
- define live API integration
- define retry logic
- establish benchmark validity
- define adjudication workflows
- replace human annotation

## RDE Drift-Control Boundary

This specification exists to prevent:

- prompt outputs from being mistaken for ground truth
- normalization failures from disappearing
- provenance collapse between annotation layers
- undocumented alias mappings

The evaluator output is an auditable candidate annotation layer, not a truth layer.

## Reference implementation (stub)

[`run_prompt_eval.py`](../scripts/run_prompt_eval.py) supports:

- **`--mode stub`** — one normalized record per input pilot row using a fixed in-process JSON payload (no network).
- **`--mode replay --raw-jsonl PATH`** — merge captured `id` + `raw_output` lines and normalize (for API responses saved offline).
- **`--mode live`** — call an OpenAI-compatible `/chat/completions` endpoint per row (`OPENAI_API_KEY` or `--api-key-env`), then normalize. Each row is **appended to `--output` immediately** (partial progress survives interruption). API failures become `api_error` failure rows.

Both stub/replay exercise `rde_eval.prompt_eval` normalization and provenance fields. Live mode uses `rde_eval.prompt_template` (`rde-prompt-eval-v1`) and `rde_eval.llm_client` (stdlib `urllib` only).
