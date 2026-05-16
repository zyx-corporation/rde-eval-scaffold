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

## リポジトリ構成（抜粋）

リポジトリ全体のツリーは英語 [`README.md`](README.md) の Repository Structure を参照。`scripts/` には次があります。

```text
scripts/
  annotate_pilot.py
  compare_annotations.py
  merge_pilot_human_labels.py
  export_results.py
  run_baselines.py
  run_eval.py
  run_prompt_eval.py
```

`compare_annotations.py` と `export_results.py`、`merge_pilot_human_labels.py` は `rde_eval` を import しません（ルートでそのまま `python scripts/...` でも実行可）。`run_baselines.py` は `rde_eval.baselines` を使うため、editable install または `PYTHONPATH=.` が必要です。

## データ（パイロット）

人手によるパイロット注釈は [`data/annotations/annotations.jsonl`](data/annotations/annotations.jsonl) に 30 行（全 `id` が [`data/pilot_30.jsonl`](data/pilot_30.jsonl) と対応）。タスクはそれぞれ 10 件ずつ — 要約・リライト・仕様変換 —（[`docs/experiment_plan.md`](docs/experiment_plan.md)）。

`pilot_30.jsonl` に含まれる先行ラベルより **注釈 JSONL が優先**されるよう統合するときは、[`scripts/merge_pilot_human_labels.py`](scripts/merge_pilot_human_labels.py) を使います（例は `data/README.md`）。

## Milestone 1（現在）

実装スコープと完了条件は [`docs/milestone1_implementation_plan.md`](docs/milestone1_implementation_plan.md) を参照してください。

## Milestone 2（着手済み・スタブ）

入出力の契約は [`docs/prompt_evaluator_io_contract.md`](docs/prompt_evaluator_io_contract.md)。

- **`--mode stub`** … API なし。固定 JSON を行ごとに正規化。
- **`--mode replay --raw-jsonl PATH`** … 保存済み `id` + `raw_output` をマージして正規化。
- **`--mode live`** … OpenAI 互換 API。各行を処理するたびに `--output` へ追記（中断しても途中まで残る）。

プロンプト: `rde_eval.prompt_template`（`rde-prompt-eval-v1`）。HTTP: `rde_eval.llm_client`（標準ライブラリのみ）。

DeepSeek 例（`--api-base-url https://api.deepseek.com/v1`、`--api-key-env DEEPSEEK_API_KEY`）は英語 README の Milestone 2 節を参照。

live 実行時は行ごとに `--output` へ追記され、中断しても部分結果が残ります。`--resume` で `--output`（および `--raw-captures-out` 指定時は captures）の既存 ID をスキップして追記再開できます。429/5xx/ネットワーク障害は `--max-retries` と `--retry-backoff-sec` でリトライし、`--request-delay-sec` で呼び出し間隔を調整できます。`--raw-captures-out` で replay 用の `id` + `raw_output` を保存できます。`compare_annotations.py` は candidate の `normalization_status: failed` を一致率から除外し、`candidate_normalization_failed` に列挙します。`--summary` で一致率・不一致件数を標準出力に表示します。

```bash
python scripts/run_prompt_eval.py \
  --input data/pilot_30.jsonl \
  --output results/prompt_eval_stub.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-stub-local"
```

## Milestone 3（ベースライン）

方針は [`docs/milestone3_baseline_plan.md`](docs/milestone3_baseline_plan.md)。

- **フェーズ1:** `difflib` による字句類似度（追加依存なし）。`baseline_scores.m3` にマージする。
- **フェーズ2（任意）:** BERTScore。`python -m pip install -e '.[baseline]'` のうえ `--bertscore`（必要なら `--bertscore-lang`）。詳細は同ドキュメント。

```bash
python scripts/run_baselines.py --input data/samples.jsonl --output results/samples_with_m3.jsonl --bertscore
```

字句のみ（フェーズ1のみ）の例:

```bash
python scripts/run_baselines.py --input data/samples.jsonl --output results/samples_with_m3.jsonl
```

**フェーズ3（実装完了・ラン時の依存のみ任意）:** `python -m pip install -e '.[baseline-nli]'` と PyTorch を入れたうえで、`--nli`、`--nli-model`（既定: `facebook/roberta-large-mnli`）、`--nli-batch-size`、`--nli-max-length`（既定: 512）。`--bertscore` と併用可。完了条件は [`docs/milestone3_baseline_plan.md`](docs/milestone3_baseline_plan.md) の Phase 3 節を参照。

```bash
python scripts/run_baselines.py \
  --input data/samples.jsonl \
  --output results/samples_with_m3.jsonl \
  --nli \
  --nli-model facebook/roberta-large-mnli \
  --nli-batch-size 8 \
  --nli-max-length 512
```

英語以外のソース／出力のみのパイロットでは、`--nli-model` に**多言語向けチェックポイント**を指定してください。`m3.nli.scores` のクラス名はモデル依存なので、再現報告には **`model_id`** を必ず載せます。

オフライン確認用の **`data/fixtures/m3_nli_notebook_smoke.jsonl`**（3 行、`m3.nli.truncated` の真偽を含む）に **`M3_JSONL`** を向けても動作します。

探索用ノートブック: [`notebooks/m3_lexical_vs_human.ipynb`](notebooks/m3_lexical_vs_human.ipynb)（ベースラインと `human_annotation` の対比）。環境変数 **`M3_JSONL`** で JSONL を指定可能。NLI は **`m3.nli.truncated`** で `--nli-max-length` 超過を記録。

`run_baselines.py` は `rde_eval` を import するため、`run_eval.py` 等と同様に editable install または `PYTHONPATH=.` が必要です。

## スクリプト実行の前提

`scripts/run_eval.py` や `scripts/annotate_pilot.py`、`scripts/run_baselines.py`、`scripts/run_prompt_eval.py` など、パッケージ `rde_eval` を import するスクリプトは、**editable install も `PYTHONPATH` も無い**状態で `python scripts/…` と実行すると `ModuleNotFoundError: No module named 'rde_eval'` になります。リポジトリのルートをカレントにして、次のいずれかを行ってください。

1. **開発用の推奨:** `python -m pip install -e '.[dev]'`（Zsh では `.[dev]` をクォート）
2. **一時的な実行:** コマンドの先頭に `PYTHONPATH=.` を付ける（例: `PYTHONPATH=. python scripts/run_eval.py --help`）

`rde_eval` を import しないスクリプトは上記「リポジトリ構成（抜粋）」節に記載。

## 最小の利用例

`python -m pip install -e '.[dev]'` を済ませたあと（または各行の `python` の前に `PYTHONPATH=.` を付けて）:

```bash
python scripts/run_eval.py --input data/samples.jsonl --output results/rde_results.jsonl
python scripts/export_results.py --input results/rde_results.jsonl --format csv --output results/rde_results.csv
python scripts/merge_pilot_human_labels.py --pilot data/pilot_30.jsonl --annotations data/annotations/annotations.jsonl --output results/pilot_30_with_human.jsonl
python scripts/run_baselines.py --input data/samples.jsonl --output results/samples_with_m3.jsonl
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
