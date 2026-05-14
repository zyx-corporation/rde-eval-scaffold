# Testing Policy

This repository follows a Kotonoha-style testing policy adapted for the RDE experimental scaffold.

## Purpose

Testing exists to:

- preserve deterministic scaffold behavior
- preserve schema compatibility
- preserve reproducibility
- detect unintended meaning drift in implementation behavior
- prevent repository state from diverging from documented Milestone scope

This testing policy does not claim empirical validation of RDE.

## Scope

The repository currently targets:

- Python 3.12+
- pytest
- Ruff
- GitHub Actions CI

Milestone 1 testing focuses on deterministic scaffold behavior rather than semantic intelligence.

## TDD Policy

This repository follows a lightweight Test-Driven Development (TDD) policy.

Expected workflow:

1. define expected behavior
2. add or update tests
3. implement or modify behavior
4. confirm deterministic reproducibility
5. update documentation if behavior changes

Behavior-changing implementation work should normally include tests in the same Issue or PR.

## Allowed Exceptions

TDD is not required for:

- documentation-only changes
- repository management tasks
- exploratory research notes
- temporary scaffolding during issue decomposition
- unfinished experimental spikes that are explicitly marked as non-production

If tests are intentionally deferred, the PR or Issue should explicitly state:

- why tests are deferred
- expected future test coverage
- unresolved risks

## Testing Layers

### 1. Schema Validation Tests

Validate:

- required fields
- optional fields
- `baseline_scores` placeholder behavior
- `risk_flags` validation
- `human_annotation` normalization
- JSON-compatible serialization

Primary files:

- `tests/test_schema.py`
- `rde_eval/schema.py`

### 2. Deterministic Classifier Tests

Validate:

- deterministic heuristic behavior
- reproducible risk-flag generation
- stable primary label mapping
- deterministic `context_drift` behavior

Primary files:

- `tests/test_classifier.py`
- `rde_eval/classifier.py`

## 3. Evaluator and Pipeline Tests

Validate:

- JSONL loading
- invalid JSON handling
- invalid schema handling
- deterministic JSONL output
- stable serialization ordering
- round-trip evaluation behavior

Primary files:

- `tests/test_evaluator.py`
- `rde_eval/evaluator.py`
- `scripts/run_eval.py`

## 4. Export Tests

Validate:

- CSV export correctness
- output field consistency
- compatibility with `EvaluationResult.to_dict()`

Primary files:

- `tests/test_export_results.py`
- `scripts/export_results.py`

## CI Policy

GitHub Actions CI must execute:

```bash
ruff check .
ruff format --check .
pytest
```

CI targets Python 3.12 only.

## Determinism Requirement

Milestone 1 outputs must be deterministic.

Requirements:

- stable JSON key ordering
- reproducible output serialization
- deterministic heuristic execution
- stable CLI exit behavior

## Placeholder Policy

`baseline_scores` is treated as:

- optional
- schema-compatible
- JSON-compatible
- inactive during Milestone 1

Milestone 1 tests validate placeholder compatibility only.

## Drift-Control Review

All substantial PRs should include:

- preserved elements
- transformed elements
- inferred or added elements
- unresolved elements
- drift risks

Testing should verify not only correctness but also alignment between:

- repository documentation
- implementation behavior
- declared milestone scope
- runtime environment

## Non-goals

Testing does not currently attempt to:

- prove semantic correctness
- validate RDE empirically
- measure intelligence
- benchmark LLM reasoning
- validate prompt-based evaluators
- replace human annotation review

## Future Work

Future milestones may add:

- prompt-based evaluator tests
- baseline metric comparison tests
- annotation agreement analysis
- statistical evaluation tests
- CI artifact preservation
- regression-drift datasets
