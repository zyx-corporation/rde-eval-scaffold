# rde-eval-scaffold

Resonant Deviation Evaluator（RDE）フレームワークを評価するための実験用スキャフォールドです。

RDEは、source context と generated output の間で生じる意味変化を監査するための枠組みです。このリポジトリはRDEの本番実装ではありません。source-output pairの構築、RDEラベルの付与、baseline evaluatorとの比較、meaning driftの分析を行うための最小限の実験パイプラインを提供します。

## 目的

- RDEのための小さく再現可能な評価スキャフォールドを提供する。
- 要約、リライト、仕様書変換に関するpilot studyを支援する。
- 意味変化を、structured labels、risk flags、criticality、task intent notes、explanationsとして表現する。
- semantic similarity、natural language inference、factuality evaluation、generic LLM-as-a-judgeなどのbaseline手法と、RDE形式の判断を比較できるようにする。

## 対象外

- 本リポジトリは本番用のRDE engineではない。
- safety filter、policy filter、factuality evaluatorを置き換えるものではない。
- RDEが大規模に検証済みであるとは主張しない。
- 現時点ではOpenAyane、Kotonoha、SLS、vector DB、UI統合は含まない。

## Milestone 1（現在）

実装スコープと完了条件は [`docs/milestone1_implementation_plan.md`](docs/milestone1_implementation_plan.md) を参照してください。

## リポジトリ構成

```text
rde-eval-scaffold/
  README.md
  README_ja.md
  LICENSE
  pyproject.toml
  docs/
    concept.md
    concept_ja.md
    annotation_guide.md
    annotation_guide_ja.md
    experiment_plan.md
    experiment_plan_ja.md
    milestone1_implementation_plan.md
    repository_operation.md
    repository_operation_ja.md
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
    test_evaluator.py
    test_export_results.py
  results/
    .gitkeep
```

## データ形式

各サンプルは、1行につき1つのJSON objectとして表現します。

最小の後方互換サンプル:

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

タスク意図再構成フィールドを含むpilot形式サンプル:

```json
{
  "id": "pilot-001",
  "task": "summarization",
  "risk_context": "policy_discussion",
  "source": "This policy may reduce user protection under specific conditions.",
  "output": "This policy reduces user protection.",
  "human_annotation": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "criticality": "medium",
  "explanation": "条件付き表現が削除され、断定へ変化している。",
  "task_intent": "Summarize faithfully without removing caveats.",
  "reconstructed_task_intent": "Faithful risk-sensitive summarization.",
  "task_intent_notes": "The explicit task was underspecified, so risk context is used.",
  "notes": "Pilot annotation sample."
}
```

## RDEラベル

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

## 最小利用例

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
python scripts/export_results.py --input results/rde_results.jsonl --format csv --output results/rde_results.csv
```

パッケージ未インストール時は `PYTHONPATH=.` を付けて実行してください。`run_eval` は JSONL／スキーマエラーまたは I/O 失敗時に終了コード **1**、成功時 **0** です。

## 開発

```bash
python -m pip install -e .[dev]
pytest
```

## リポジトリ運用

このリポジトリはIssue駆動のワークフローに従います。実装作業はGitHub Issueに紐づけて行います。Pull Requestとmergeは、明示的な指示がある場合にのみ実施します。

## ライセンス

コードはApache License 2.0でライセンスされます。

ドキュメントおよびサンプルデータは、別途明記がない限りCC BY 4.0で公開可能とします。
