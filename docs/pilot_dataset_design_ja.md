# pilot dataset 設計

## 目的

`pilot_30.jsonl` は、RDE evaluation scaffold の最初の empirical pilot dataset です。

この dataset は以下を目的とします。

- annotation usability checks
- drift-category coverage checks
- deterministic scaffold inspection
- baseline-comparison preparation
- 和英並列の human review

この dataset は validated benchmark ではありません。

## Dataset 構成

[`data/pilot_30.jsonl`](../data/pilot_30.jsonl) が 30 records を収録。**確定人手ラベル**は **`data/annotations/annotations.jsonl`** に **`id`** 単位で格納（[`annotate_pilot.py`](../scripts/annotate_pilot.py)。ベースライン前には [`merge_pilot_human_labels.py`](../scripts/merge_pilot_human_labels.py) でマージ、[論文準備メモ](paper_preparation.md) 参照）。

| Task | Count |
|---|---:|
| summarization | 10 |
| rewriting | 10 |
| specification_conversion | 10 |

## 日本語確認フィールド

以下の日本語 inspection fields を含みます。

- `source_ja`
- `output_ja`
- `explanation_ja`
- `task_intent_ja`
- `reconstructed_task_intent_ja`
- `task_intent_notes_ja`

これらは:

- human review
- bilingual semantic comparison
- drift inspection
- annotation discussion

のために追加されています。

schema authority は English canonical fields です。

## Placeholder Policy

`baseline_scores` は Milestone 1 placeholder のままです。

## 非目標

この dataset は:

- RDE validity の証明
- benchmark quality の確立
- statistical significance の確立
- inter-annotator agreement の確立

を目的としません。
