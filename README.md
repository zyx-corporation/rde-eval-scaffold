# rde-eval-scaffold

Experimental scaffold for evaluating the Resonant Deviation Evaluator (RDE) framework.

RDE is a framework for auditing meaning changes between a source context and a generated output. This repository is not a production implementation of RDE. It provides a minimal experimental pipeline for constructing source-output pairs, applying RDE labels, comparing baseline evaluators, and analyzing meaning drift.

## Goals

- Provide a small, reproducible evaluation scaffold for RDE.
- Support pilot studies on summarization, rewriting, and specification conversion.
- Represent meaning changes as structured labels, risk flags, criticality, task intent notes, and explanations.
- Compare RDE-style judgments with baseline methods such as semantic similarity, natural language inference, factuality evaluation, and generic LLM-as-a-judge.

## Non-goals

- This is not a production-grade RDE engine.
- This is not a replacement for safety filters, policy filters, or factuality evaluators.
- This repository does not claim that RDE is already validated at scale.
- This repository does not yet include OpenAyane, Kotonoha, SLS, vector DB, or UI integration.

## Runtime Requirement

This repository targets Python 3.12 or later.

## Current Implementation Status

The current implementation is Milestone 1: a deterministic heuristic scaffold for dry-run validation of the RDE schema, label taxonomy, risk flags, JSONL pipeline, CLI output, and basic tests.

Milestone 1 should not be interpreted as a full RDE evaluator or as empirical validation of RDE. It is a reproducibility layer that keeps the experimental format stable before prompt-based and model-based evaluators are introduced.

## Roadmap

### Milestone 1: Heuristic RDE Scaffold

Goal: establish a reproducible scaffold for RDE pilot studies. Scope and completion criteria: [`docs/milestone1_implementation_plan.md`](docs/milestone1_implementation_plan.md).

### Milestone 2: Prompt-based RDE Evaluator

Goal: add a prompt-based evaluator using the same schema and annotation guide.

### Milestone 3: Baseline Comparison

Goal: compare RDE-style evaluation against existing methods.

### Milestone 4: Annotation Reliability

Goal: evaluate whether RDE labels and risk flags can be applied consistently.

## Repository Structure

```text
rde-eval-scaffold/
  README.md
  README_ja.md
  LICENSE
  pyproject.toml
  docs/
    concept.md
    annotation_guide.md
    experiment_plan.md
    milestone1_implementation_plan.md
    repository_operation.md
  data/
    samples.jsonl
    README.md
  rde_eval/
    __init__.py
    schema.py
    classifier.py
    evaluator.py
  scripts/
    run_eval.py
    export_results.py
  tests/
    test_schema.py
    test_classifier.py
    test_evaluator.py
    test_export_results.py
  results/
    .gitkeep
```

## Data Format

Each sample is represented as one JSON object per line.

The current `data/samples.jsonl` file contains minimal dry-run examples for schema and pipeline validation. The planned pilot dataset consists of 30 source-output pairs.

## Invoking repository scripts

Several scripts under `scripts/` import the `rde_eval` package (for example `run_eval.py` and `annotate_pilot.py`). From a plain checkout, running `python scripts/…` without installing the package fails with `ModuleNotFoundError: No module named 'rde_eval'` because the project directory is not on `sys.path`.

Use either of the following from the **repository root**:

1. **Editable install (recommended for development)**

   ```bash
   python -m pip install -e .[dev]
   ```

2. **Set `PYTHONPATH` for ad-hoc runs** — prefix each script invocation:

   ```bash
   PYTHONPATH=. python scripts/run_eval.py --help
   ```

`scripts/export_results.py` does not import `rde_eval`, so it may run without these steps, but using the same environment keeps behavior consistent.

## Minimal Usage

After `python -m pip install -e .` (or by prefixing each `python` line with `PYTHONPATH=.`):

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
python scripts/export_results.py --input results/rde_results.jsonl --format csv --output results/rde_results.csv
```

The evaluation CLI exits with status **1** on invalid JSONL, schema errors, or I/O failures; **0** on success.

## Development

```bash
python -m pip install -e .[dev]
pytest
```
