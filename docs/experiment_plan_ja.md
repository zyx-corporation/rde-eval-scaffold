# Pilot Experiment Plan

## 目的

pilot studyは、RDE labels と risk flags をsource-output meaning changesに対して一貫して適用できるかを確認するためのものです。

これはRDEを大規模に検証することを目的としません。taxonomyの使いやすさ、注釈上の難しさ、次の実証段階に向けた課題を特定することを目的とします。

## 初期設計

| Task | N | 主な観察対象 |
|---|---:|---|
| Summarization | 10 | caveat loss, uncertainty loss, claim-strength inflation |
| Rewriting | 10 | intent change, hypothesis-to-assertion drift, value simplification |
| Specification Conversion | 10 | theoretical reduction, responsibility shift, institutional implication loss |

### 実装状況（パイロットコーパス）

[`data/pilot_30.jsonl`](../data/pilot_30.jsonl) が上記 30 件設計を実データ化している（各タスク 10 件）。確定人手ラベルは **`id`** 単位で [`data/annotations/annotations.jsonl`](../data/annotations/annotations.jsonl) に蓄積する。複数 Annotator での検証済みベンチマークではなく、パイロット用途に限定すること（末尾 Notes 参照）。

## サンプルごとのフィールド

必須フィールド:

- `id`
- `task`
- `risk_context`
- `source`
- `output`

pilot annotation fields:

- `human_annotation`
- `risk_flags`
- `criticality`
- `explanation`
- `task_intent`
- `reconstructed_task_intent`
- `task_intent_notes`
- `notes`
- `baseline_scores`

## Task-intent reconstruction

明示されたtaskが不十分である場合、またはrisk contextと矛盾する場合、注釈者はtask intentを再構成できます。この再構成は暗黙に行わず、必ず記録します。

- `task_intent`: 明示されたuserまたはsystemのtask intent
- `reconstructed_task_intent`: 評価者が再構成したtask intent
- `task_intent_notes`: 再構成が必要だった理由

## Baselines

初期baselineとして、以下を検討します。

- semantic similarity / BERTScore
- natural language inference
- factuality evaluation
- generic LLM-as-a-judge

## 探索的出力

pilot studyは、最終的なvalidation claimではなく、以下の探索的知見を出力することを目指します。

- category usability
- Delta-M axis redundancy or gaps
- differences from baseline distributions
- annotator disagreement patterns
- risk flag quality
- explanation quality

## Notes

初期段階で注釈者が1名しか確保できない場合、そのdatasetはvalidationではなくpilot annotationとして扱います。
