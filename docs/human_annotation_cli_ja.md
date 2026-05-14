# 人手アノテーション CLI

## 目的

この CLI は `data/pilot_30.jsonl` を対象とした、日本語中心の人手アノテーション用ツールです。

このツールは human annotator 向けであり、自動 RDE 判定や LLM annotation は行いません。

## 実行例

```bash
python scripts/annotate_pilot.py \
  --input data/pilot_30.jsonl \
  --output data/annotations/pilot_30_human_tomyuk.jsonl \
  --annotator tomyuk
```

## 表示内容

CLI は以下を日本語中心で表示します。

- `source_ja`
- `output_ja`
- `task_intent_ja`
- `reconstructed_task_intent_ja`
- `task_intent_notes_ja`
- `explanation_ja`

`--show-english` 指定時は English canonical fields も表示します。

## 入力内容

annotator は各 record に対して:

1. explanation_ja
2. label
3. risk_flags
4. criticality

を入力します。

## ラベル選択肢

| No. | 表示 | 保存値 |
|---:|---|---|
| 1 | 保持 | `Preserved` |
| 2 | 許可された変換 | `Authorized Transformation` |
| 3 | 推論された拡張 | `Inferred Extension` |
| 4 | 未解決のギャップ | `Unresolved Gap` |
| 5 | 疑わしい逸脱 | `Suspicious Drift` |
| 6 | 重大な歪曲 | `Critical Distortion` |

## risk_flags 選択肢

| No. | 表示 | 保存値 |
|---:|---|---|
| 1 | 主張強度の上昇 | `claim_strength_inflation` |
| 2 | 不確実性の喪失 | `uncertainty_loss` |
| 3 | 責任の移動 | `responsibility_shift` |
| 4 | 価値の単純化 | `value_simplification` |
| 5 | 制度的含意の喪失 | `institutional_implication_loss` |
| 6 | 文脈逸脱 | `context_drift` |
| 7 | 理論的縮減 | `theoretical_reduction` |

複数指定例:

```text
1,2,6
```

## criticality 選択肢

| No. | 表示 | 保存値 |
|---:|---|---|
| 1 | 低 | `low` |
| 2 | 中 | `medium` |
| 3 | 高 | `high` |

## 出力形式

annotation は JSONL として `data/annotations/` に保存します。

例:

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

## resume 動作

既存 output JSONL がある場合、既に annotation 済みの ID は skip されます。

`--overwrite` で再 annotation を許可します。

`--no-resume` で既存 annotation を無視して新規開始します。

## canonical-value rule

日本語ラベルや説明は display-only です。

保存値は canonical English schema values を保持します。

- English RDE labels
- English risk flag identifiers
- `low`, `medium`, `high`

CLI は日本語 schema を新設してはなりません。

## 非目標

この CLI は:

- automatic RDE judgment
- LLM annotation
- adjudication
- inter-annotator agreement calculation
- benchmark ground truth creation

を目的としません。
