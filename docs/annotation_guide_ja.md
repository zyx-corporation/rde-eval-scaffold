# RDE注釈ガイド

このガイドは、RDE pilot studyにおいてsource-output pairを注釈する方法を定義します。

## 注釈単位

各注釈単位は、以下から構成されます。

- `source`: 元テキストまたは元文脈
- `task`: 意図された変換タスク
- `risk_context`: ドメインまたはリスク設定
- `output`: 生成されたテキスト

注釈者は、`output`を`source`、`task`、`risk_context`との関係で評価します。同じoutputであっても、taskやrisk contextが異なれば異なるラベルになる可能性があります。

## Primary Labels

| Label | 使用基準 |
|---|---|
| Preserved | 中心的な意図、主張強度、不確実性、責任構造が保存されている場合 |
| Authorized Transformation | outputがsourceを変化させているが、その変化がtaskによって正当化され、重要な意味を損なっていない場合 |
| Inferred Extension | outputがsourceに明示されていない内容を追加しているが、その内容がsourceから妥当に推論可能な場合 |
| Unresolved Gap | outputが重要な意味差分を未処理のまま残している、または十分な確信をもって分類できない場合 |
| Suspicious Drift | outputが主張強度、不確実性、責任、価値構造、制度的含意を潜在的に有害な方向へ変化させている場合 |
| Critical Distortion | outputがsourceの意味、責任構造、制度的含意を実質的に反転・消去・破壊している場合 |

## Risk Flags

| Risk Flag | 意味 |
|---|---|
| claim_strength_inflation | 弱い主張、条件付き主張、仮説的主張が、より強い断定へ変化している |
| uncertainty_loss | 不確実性、限界、条件、留保が削除されている |
| responsibility_shift | 責任が人間、組織、制度からAIまたは別の主体へ移動している |
| value_simplification | 複数の価値や対立が、単一の価値または結論へ単純化されている |
| institutional_implication_loss | 法的、組織的、運用上、ガバナンス上の含意が消えている |
| context_drift | outputがsourceとは異なる文脈へ移動している |
| theoretical_reduction | 理論的主張が単なる技術的・運用的記述へ縮退している |

## 判断手順

1. taskを確認する。
2. risk contextを確認する。
3. 主張強度を比較する。
4. 不確実性や留保が保存されているか確認する。
5. 責任構造を確認する。
6. 価値構造を確認する。
7. 制度的含意を確認する。
8. primary labelを1つ付与する。
9. 関連するrisk flagsを付与する。
10. 短い説明を書く。

## 境界規則

`Suspicious Drift`は、outputがレビューまたは修正後には利用可能かもしれないが、意味上のリスクを含む場合に使用します。

`Critical Distortion`は、outputがsourceの意味を反転・消去・実質的に損なっており、そのまま利用すべきでない場合に使用します。

`Inferred Extension`は、追加内容がsourceから妥当に支持される場合にのみ使用します。追加内容が支持されず、結論を変えている場合は、`Suspicious Drift`または`Critical Distortion`を検討します。

`Unresolved Gap`は、注釈者が十分な確信をもって判断できない場合、またはoutputがレビューを要する問題を省略しているが明確な歪曲とは言えない場合に使用します。

## 出力スキーマ例

```json
{
  "id": "sample-001",
  "primary_label": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "criticality": "medium",
  "explanation": "条件付きの可能性表現が削除され、断定的な主張へ変化している。"
}
```
