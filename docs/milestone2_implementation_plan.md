# Milestone 2 Implementation Plan

## Status

**Completed (2026-05-16).** Behavior matches [`prompt_evaluator_io_contract.md`](prompt_evaluator_io_contract.md). See **Completion Criteria** below.

## Purpose

Milestone 2 adds a **prompt-based RDE evaluator** on top of the Milestone 1 scaffold: same record shape and annotation guide, with LLM-produced candidate labels that are **normalized, auditable, and provenance-tagged** rather than treated as ground truth.

Normative I/O rules live in the contract document; this plan records scope, deliverables, and what “done” means for the repository.

## Non-goals

Milestone 2 does not:

- claim benchmark validity or replace human annotation
- define adjudication workflows
- prove semantic correctness of model judgments
- integrate OpenAyane, Kotonoha, SLS, or production RDE routing

## Scope

### Contract alignment

[`prompt_evaluator_io_contract.md`](prompt_evaluator_io_contract.md) defines:

- canonical prompt input fields (English authority; optional Japanese supplements)
- normalized success and failure JSONL records
- label, risk flag, and criticality validation (unknown values → failed normalization unless a **documented** alias map applies; this repo uses strict validation with no alias table)
- raw output preservation on success and failure
- required provenance: `annotator_type`, `annotator_id`, `model`, `prompt_version`, `annotation_run_id`

### Pipeline modes

_entrypoint:_ [`scripts/run_prompt_eval.py`](../scripts/run_prompt_eval.py)

| Mode   | Role |
|--------|------|
| `stub` | Fixed in-process JSON per row; no network |
| `replay` | Normalize captured `id` + `raw_output` JSONL |
| `live` | OpenAI-compatible `/chat/completions`; append per row; optional `--resume`, retries, pacing, `--raw-captures-out` |

Live assembly uses [`rde_eval.prompt_template`](../rde_eval/prompt_template.py) and [`rde_eval.llm_client`](../rde_eval/llm_client.py) as described in the I/O contract.

### Core library

[`rde_eval.prompt_eval`](../rde_eval/prompt_eval.py) — extract prompt inputs, parse model JSON, validate payload, build success/failure records.

## Completion Criteria

Milestone 2 is **complete** when:

- the CLI and library satisfy the **I/O contract** (inputs, outputs, failures, provenance, raw retention)
- **stub**, **replay**, and **live** modes behave as specified in the contract and README
- **CI passes**: `ruff check`, `ruff format --check`, `pytest`
- documentation is **internally consistent** (root README, Japanese README, this plan, contract)

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Normalization + provenance helpers | `rde_eval/prompt_eval.py` |
| Prompt assembly | `rde_eval/prompt_template.py`, `rde_eval/prompts.py` |
| HTTP client + retry | `rde_eval/llm_client.py`, `rde_eval/llm_retry.py` |
| CLI | `scripts/run_prompt_eval.py` |
| Contract (normative) | `docs/prompt_evaluator_io_contract.md` |
| Tests | `tests/test_prompt_eval.py`, `tests/test_prompt_template.py`, `tests/test_run_prompt_eval_*.py`, `tests/test_llm_*.py` |

## Next step

**Milestone 3** (baseline comparison) is **complete** — see [`milestone3_implementation_plan.md`](milestone3_implementation_plan.md). **Milestone 4** — annotation reliability (repository README).
