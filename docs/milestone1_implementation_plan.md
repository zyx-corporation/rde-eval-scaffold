# Milestone 1 Implementation Plan

## Status

**Completed (2026-05-16).** Deliverables and completion criteria in this document are satisfied. Subsequent milestones extend the same schema; see the repository README roadmap.

## Purpose

Milestone 1 defines the deterministic heuristic scaffold layer of the RDE evaluation repository.

The purpose of Milestone 1 is not to fully implement RDE. The purpose is to establish a reproducible experimental scaffold for:

- schema validation
- label taxonomy validation
- risk flag validation
- JSONL pipeline validation
- deterministic dry-run evaluation
- CLI reproducibility
- baseline infrastructure preparation

Milestone 1 is the reproducibility layer that stabilizes the evaluation format before prompt-based and model-based evaluators are introduced.

## Non-goals

Milestone 1 does not attempt to:

- implement a production-grade RDE engine
- validate RDE empirically at scale
- replace factuality evaluators or safety systems
- implement semantic reasoning through LLM prompting
- implement multi-agent evaluation
- implement OpenAyane, Kotonoha, or SLS integration
- provide statistically validated benchmark claims

## Scope

### Included Components

#### 1. Data Schema

Required:

- `id`
- `task`
- `risk_context`
- `source`
- `output`

Optional annotation fields:

- `human_annotation`
- `risk_flags`
- `criticality`
- `explanation`
- `task_intent`
- `reconstructed_task_intent`
- `task_intent_notes`
- `notes`
- `baseline_scores` (optional **schema-compatible placeholder**; see below)

In Milestone 1 the heuristic scaffold **does not populate or interpret** `baseline_scores`; the field is retained so pilot JSONL and later milestones share a stable, reproducible record shape.

##### Placeholder: `baseline_scores` (Milestone 1)

- **Role in Milestone 1**: optional field reserved for a stable on-record shape; may be empty, omitted, or filled manually for dry-runs. The heuristic scaffold **does not compute or consume** it.
- **Milestone 3**: same field becomes **active** for baseline comparison (e.g. BERTScore, NLI, factuality, LLM-as-a-judge), with values written according to the Milestone 3 specification.

#### 2. Label Taxonomy

Milestone 1 stabilizes the following primary labels:

- Preserved
- Authorized Transformation
- Inferred Extension
- Unresolved Gap
- Suspicious Drift
- Critical Distortion

#### 3. Risk Flags

Milestone 1 stabilizes the following initial risk flags:

- claim_strength_inflation
- uncertainty_loss
- responsibility_shift
- value_simplification
- institutional_implication_loss
- context_drift
- theoretical_reduction

#### 4. Deterministic Heuristic Classifier

Milestone 1 uses deterministic heuristics rather than prompt-based judgment.

The heuristic classifier is intended only for:

- dry-run reproducibility
- schema validation
- pipeline validation
- CLI testing
- output formatting validation

The heuristic classifier must not be interpreted as a full RDE evaluator.

#### 5. CLI Pipeline

Milestone 1 must support the following invocation from the repository root when `rde_eval` is importable (for example after `python -m pip install -e .` or with `PYTHONPATH=.`):

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
```

Required behavior:

- JSONL loading
- schema validation (required fields; optional fields preserved as documented)
- deterministic evaluation
- JSONL output generation
- stable serialization
- reproducible output

#### 6. Tests

Milestone 1 tests should validate:

- schema validation
- required field handling
- deterministic classifier behavior
- output serialization
- invalid JSON handling
- invalid schema handling

## Planned Dataset Structure

Milestone 1 includes only minimal dry-run examples.

The planned pilot dataset structure is:

| Task | Planned Samples |
|---|---:|
| Summarization | 10 |
| Rewriting | 10 |
| Specification Conversion | 10 |

Total planned pilot samples: 30.

These samples are planned pilot-study inputs and not benchmark-quality validation data.

## Completion Criteria

Milestone 1 is considered complete when:

- schema definitions are stable
- label taxonomy is stable
- risk flags are stable
- CLI pipeline is reproducible
- deterministic outputs are reproducible
- tests pass consistently
- dry-run examples execute correctly
- documentation is internally consistent

## Deliverables

Expected Milestone 1 deliverables:

- schema.py
- classifier.py
- evaluator.py
- sample JSONL dataset
- annotation guide
- experiment plan
- deterministic CLI pipeline
- unit tests
- implementation documentation

## RDE Drift Control

Milestone 1 intentionally separates:

- reproducibility scaffolding
- prompt-based reasoning
- empirical validation
- production RDE implementation

This separation prevents the deterministic heuristic scaffold from being misrepresented as a complete implementation of RDE.

## Next Step

Milestone 2 is **complete** — [`milestone2_implementation_plan.md`](milestone2_implementation_plan.md). Milestone 3 (baselines) is **complete** — [`milestone3_implementation_plan.md`](milestone3_implementation_plan.md). **Milestone 4** continues with annotation reliability (see repository README).
