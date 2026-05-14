# Human Annotation CLI

## Purpose

The human annotation CLI supports Japanese-first manual annotation of `data/pilot_30.jsonl`.

The tool is intended for human annotators. It does not perform automatic RDE judgment and does not use an LLM.

## Command

```bash
python scripts/annotate_pilot.py \
  --input data/pilot_30.jsonl \
  --output data/annotations/pilot_30_human_tomyuk.jsonl \
  --annotator tomyuk
```

Optional flags:

```bash
--show-english
--overwrite
--no-resume
```

## Display Policy

The CLI displays each task primarily in Japanese.

Displayed fields:

- `id`
- `task`
- `risk_context`
- `source_ja`
- `output_ja`
- `task_intent_ja`
- `reconstructed_task_intent_ja`
- `task_intent_notes_ja`
- `explanation_ja`

When `--show-english` is enabled, the CLI also displays:

- `source`
- `output`
- `task_intent`
- `reconstructed_task_intent`
- `task_intent_notes`
- `explanation`

## Annotation Flow

For each record, the annotator enters:

1. Japanese explanation
2. RDE label
3. risk flags
4. criticality

The CLI repeats this flow until all records are annotated or the user exits.

## Label Choices

Labels are displayed in Japanese with canonical English values.

| No. | Japanese Display | Saved Value |
|---:|---|---|
| 1 | 保持 | `Preserved` |
| 2 | 許可された変換 | `Authorized Transformation` |
| 3 | 推論された拡張 | `Inferred Extension` |
| 4 | 未解決のギャップ | `Unresolved Gap` |
| 5 | 疑わしい逸脱 | `Suspicious Drift` |
| 6 | 重大な歪曲 | `Critical Distortion` |

## Risk Flag Choices

Risk flags are displayed in Japanese with canonical English values.

| No. | Japanese Display | Saved Value |
|---:|---|---|
| 1 | 主張強度の上昇 | `claim_strength_inflation` |
| 2 | 不確実性の喪失 | `uncertainty_loss` |
| 3 | 責任の移動 | `responsibility_shift` |
| 4 | 価値の単純化 | `value_simplification` |
| 5 | 制度的含意の喪失 | `institutional_implication_loss` |
| 6 | 文脈逸脱 | `context_drift` |
| 7 | 理論的縮減 | `theoretical_reduction` |

Multiple flags are entered as comma-separated numbers, for example:

```text
1,2,6
```

An empty input means no risk flags.

## Criticality Choices

| No. | Japanese Display | Saved Value |
|---:|---|---|
| 1 | 低 | `low` |
| 2 | 中 | `medium` |
| 3 | 高 | `high` |

## Output Format

Annotations are saved as JSONL under `data/annotations/`.

Example:

```json
{
  "id": "pilot-sum-001",
  "annotator_type": "human",
  "annotator_id": "tomyuk",
  "human_annotation": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "criticality": "medium",
  "explanation_ja": "条件付きの可能性が削除され、断定表現になっている。",
  "annotation_status": "completed"
}
```

## Resume Behavior

By default, the CLI resumes from an existing output file.

If an ID already exists in the output JSONL, that record is skipped.

Use `--overwrite` to re-annotate existing records.

Use `--no-resume` to ignore existing annotations and start a new run.

## Canonical-Value Rule

Japanese labels and descriptions are display-only.

Saved values must remain canonical schema values:

- English RDE label values
- English risk flag identifiers
- `low`, `medium`, `high` for criticality

The CLI must not create a separate Japanese schema.

## Non-goals

This CLI does not:

- perform automatic RDE judgment
- run LLM annotation
- adjudicate annotator disagreement
- calculate inter-annotator agreement
- create benchmark ground truth
