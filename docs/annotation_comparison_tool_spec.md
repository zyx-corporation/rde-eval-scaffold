# Annotation Comparison Tool Specification

## Purpose

`compare_annotations.py` compares reference annotations and candidate annotations for the same source dataset.

The initial target is `pilot_30`.

The tool is intended for:

- disagreement inspection
- annotation consistency inspection
- human vs LLM comparison
- drift-pattern analysis
- pilot-study analysis

The tool is not intended to prove RDE validity.

## Command

```bash
python scripts/compare_annotations.py \
  --reference data/annotations/annotations.jsonl \
  --candidate data/annotations/pilot_30_deepseek.jsonl \
  --source data/pilot_30.jsonl \
  --output results/annotation_comparison_deepseek.json
```

## Input Roles

### Reference annotation

The reference file is typically human annotation.

Supported fields:

- `id`
- `human_annotation`
- `risk_flags`
- `criticality`
- `explanation`
- `explanation_ja`

The reference annotation is not automatically treated as absolute truth.

### Candidate annotation

The candidate file is typically LLM annotation.

Supported fields:

- `id`
- `llm_annotation`
- `risk_flags`
- `criticality`
- `explanation`
- `explanation_ja`
- provenance fields

## Matching Rule

Records are matched by `id`.

If an ID exists in one file but not the other, the comparison result must record:

- missing reference record
- missing candidate record

Candidate rows with `normalization_status: failed` (API or normalization failures from `run_prompt_eval`) are listed under `candidate_normalization_failed` and excluded from label/criticality/risk-flag agreement denominators. Legacy candidate files without `normalization_status` are treated as normalized.

## Aggregate Metrics

### Label Agreement

Fraction of records where:

```text
reference.human_annotation == candidate.llm_annotation
```

### Criticality Agreement

Fraction of records where:

```text
reference.criticality == candidate.criticality
```

### Risk Flag Exact Agreement

Fraction of records where:

```text
set(reference.risk_flags) == set(candidate.risk_flags)
```

### Risk Flag Precision / Recall / F1

Treat risk flags as unordered sets.

Definitions:

```text
precision = overlap / candidate_flags
recall    = overlap / reference_flags
f1        = harmonic_mean(precision, recall)
```

## Disagreement Records

The tool must emit disagreement records.

Example:

```json
{
  "id": "pilot-sum-008",
  "reference_label": "Suspicious Drift",
  "candidate_label": "Critical Distortion",
  "reference_flags": ["claim_strength_inflation"],
  "candidate_flags": [
    "claim_strength_inflation",
    "context_drift"
  ],
  "reference_criticality": "medium",
  "candidate_criticality": "high"
}
```

## Output JSON Schema

```json
{
  "total": 30,
  "label_agreement": 0.73,
  "criticality_agreement": 0.80,
  "risk_flag_exact_agreement": 0.60,
  "risk_flag_precision": 0.75,
  "risk_flag_recall": 0.70,
  "risk_flag_f1": 0.72,
  "disagreements": []
}
```

## Provenance Preservation

The comparison tool must preserve provenance separation.

Reference and candidate annotations remain separate layers.

The tool must not:

- overwrite annotations
- merge annotations automatically
- adjudicate disagreements
- replace human annotation with LLM annotation

## Non-goals

The tool does not:

- prove RDE validity
- establish benchmark quality
- provide statistical significance
- calculate inter-annotator kappa
- create adjudicated gold labels

## Future Work

Future versions may add:

- confusion matrices
- label-level precision/recall
- disagreement clustering
- adjudication support
- visualization output
- temporal comparison across annotation versions
