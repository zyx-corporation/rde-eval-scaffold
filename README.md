# rde-eval-scaffold

Experimental scaffold for evaluating the Resonant Deviation Evaluator (RDE) framework.

RDE is a framework for auditing meaning changes between a source context and a generated output. This repository is not a production implementation of RDE. It provides a minimal experimental pipeline for constructing source-output pairs, applying RDE labels, comparing baseline evaluators, and analyzing meaning drift.

## Goals

- Provide a small, reproducible evaluation scaffold for RDE.
- Support pilot studies on summarization, rewriting, and specification conversion.
- Represent meaning changes as structured labels, risk flags, criticality, and explanations.
- Compare RDE-style judgments with baseline methods such as semantic similarity, natural language inference, factuality evaluation, and generic LLM-as-a-judge.

## Non-goals

- This is not a production-grade RDE engine.
- This is not a replacement for safety filters, policy filters, or factuality evaluators.
- This repository does not claim that RDE is already validated at scale.
- This repository does not yet include OpenAyane, Kotonoha, SLS, vector DB, or UI integration.

## Repository Structure

```text
rde-eval-scaffold/
  README.md
  LICENSE
  pyproject.toml
  docs/
    concept.md
    annotation_guide.md
    experiment_plan.md
  data/
    samples.jsonl
    README.md
  rde_eval/
    __init__.py
    schema.py
    analyzers.py
    diff.py
    classifier.py
    prompts.py
    evaluator.py
  scripts/
    run_eval.py
    export_results.py
  tests/
    test_schema.py
    test_classifier.py
  results/
    .gitkeep
```

## Data Format

Each sample is represented as one JSON object per line.

```json
{
  "id": "sample-001",
  "task": "summarization",
  "risk_context": "policy_discussion",
  "source": "This policy may reduce user protection under specific conditions.",
  "output": "This policy reduces user protection.",
  "human_annotation": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "notes": "The output removes conditionality and strengthens the claim."
}
```

## RDE Labels

- `Preserved`
- `Authorized Transformation`
- `Inferred Extension`
- `Unresolved Gap`
- `Suspicious Drift`
- `Critical Distortion`

## Risk Flags

- `claim_strength_inflation`
- `uncertainty_loss`
- `responsibility_shift`
- `value_simplification`
- `institutional_implication_loss`
- `context_drift`
- `theoretical_reduction`

## Minimal Usage

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
python scripts/export_results.py --input results/rde_results.jsonl --format csv --output results/rde_results.csv
```

## Development

```bash
python -m pip install -e .[dev]
pytest
```

## Repository Operation

This repository follows an issue-driven workflow. Implementation work should be tied to GitHub issues. Pull requests and merges are performed only after explicit instruction.

## License

Code is licensed under the Apache License 2.0.

Documentation and sample data may be released under CC BY 4.0 unless otherwise specified.
