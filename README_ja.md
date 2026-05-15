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

## 実行環境

本リポジトリは Python 3.12 以上を対象とします。

## Milestone 1（現在）

実装スコープと完了条件は [`docs/milestone1_implementation_plan.md`](docs/milestone1_implementation_plan.md) を参照してください。

## Milestone 2（着手済み・スタブ）

入出力の契約は [`docs/prompt_evaluator_io_contract.md`](docs/prompt_evaluator_io_contract.md)。

- **`--mode stub`** … API なし。固定 JSON を行ごとに正規化。
- **`--mode replay --raw-jsonl PATH`** … 保存済み `id` + `raw_output` をマージして正規化。

プロンプト文面は `rde_eval.prompt_template`（`rde-prompt-eval-v1`）。

```bash
python scripts/run_prompt_eval.py \
  --input data/pilot_30.jsonl \
  --output results/prompt_eval_stub.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-stub-local"
```

## スクリプト実行の前提

`scripts/run_eval.py` や `scripts/annotate_pilot.py`、`scripts/run_prompt_eval.py` など、パッケージ `rde_eval` を import するスクリプトは、**editable install も `PYTHONPATH` も無い**状態で `python scripts/…` と実行すると `ModuleNotFoundError: No module named 'rde_eval'` になります。リポジトリのルートをカレントにして、次のいずれかを行ってください。

1. **開発用の推奨:** `python -m pip install -e '.[dev]'`（Zsh では `.[dev]` をクォート）
2. **一時的な実行:** コマンドの先頭に `PYTHONPATH=.` を付ける（例: `PYTHONPATH=. python scripts/run_eval.py --help`）

`export_results.py` は `rde_eval` に依存しませんが、他と同じ環境で動かすのが無難です。

## 最小の利用例

`python -m pip install -e '.[dev]'` を済ませたあと（または各行の `python` の前に `PYTHONPATH=.` を付けて）:

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
python scripts/export_results.py --input results/rde_results.jsonl --format csv --output results/rde_results.csv
python scripts/run_prompt_eval.py \
  --input data/samples.jsonl \
  --output results/prompt_eval_stub.jsonl \
  --annotation-run-id local-stub-1
```

## 開発

```bash
python -m pip install -e '.[dev]'
pytest
```
