# RDEコンセプト

Resonant Deviation Evaluator（RDE）は、source context と generated output の間で生じる意味変化を監査するための枠組みです。

RDEは、factuality evaluator、safety filter、policy filter、generic LLM-as-a-judge pipelineを置き換えるものではありません。RDEが焦点を当てるのは、意味変換の許容性です。

## 操作的なDelta-M

このスキャフォールドでは、意味変化（Delta-M）を、観測可能な以下の変化として操作的に扱います。

- claim strength
- uncertainty and caveats
- intent
- responsibility structure
- value structure
- institutional implication
- context affinity

## ラベル

- Preserved
- Authorized Transformation
- Inferred Extension
- Unresolved Gap
- Suspicious Drift
- Critical Distortion

## ステータス

このリポジトリは、pilot studyのための実験用スキャフォールドです。検証済みbenchmarkではなく、本番用RDE engineでもありません。
