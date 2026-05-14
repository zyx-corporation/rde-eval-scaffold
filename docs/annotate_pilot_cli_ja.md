# annotate_pilot CLI — 使用ガイド

`scripts/annotate_pilot.py` は、RDE パイロット研究サンプルを人手で注釈するための  
日本語優先インタラクティブ CLI ツールです。

## `rde_eval` の import について

`annotate_pilot.py` はパッケージ `rde_eval` を import します。リポジトリルートで、**editable install**（`python -m pip install -e .[dev]`）を済ませるか、コマンド先頭に **`PYTHONPATH=.`** を付けてください（ルートの [`README_ja.md`](../README_ja.md) も参照）。どちらも無いと `ModuleNotFoundError: No module named 'rde_eval'` になります。

以下の例は、いずれかの方法で import が通る前提です。

---

## クイックスタート

```bash
python scripts/annotate_pilot.py
```

`data/pilot_30.jsonl` を読み込み、注釈結果を  
`data/annotations/annotations.jsonl` へ書き出します。

---

## オプション

| オプション | デフォルト | 説明 |
|---|---|---|
| `--input PATH` | `data/pilot_30.jsonl` | 注釈対象の入力 JSONL ファイル |
| `--output PATH` | `data/annotations/annotations.jsonl` | 注釈結果の出力 JSONL ファイル |
| `--annotator NAME` | `anonymous` | 各レコードに記録される注釈者識別子 |
| `--no-resume` | なし | 出力ファイル内の既存 ID を無視し、先頭からやり直す |
| `--overwrite` | なし | 開始前に出力ファイルを削除する |
| `--skip-pilot-task-meta` | なし | 入力行の `task_intent` 等4フィールドを注釈行にコピーしない |

使用例：

```bash
# 注釈者名を指定する
python scripts/annotate_pilot.py --annotator alice

# パスをすべて指定する
python scripts/annotate_pilot.py \
  --input data/pilot_30.jsonl \
  --output data/annotations/alice_session1.jsonl \
  --annotator alice
```

---

## 再開モード（Resume mode）

**選択した `--output` ファイルだけ**を読み、既に存在する `id` のサンプルをスキップします。  
同じディレクトリにある別名の JSONL は参照しません（再開時も同じ出力パスを指定してください）。

```bash
# 1回目のセッション — 途中で Ctrl-C して中断
python scripts/annotate_pilot.py --output data/annotations/alice.jsonl --annotator alice

# 2回目のセッション — 中断した続きから自動的に再開
python scripts/annotate_pilot.py --output data/annotations/alice.jsonl --annotator alice
```

---

## 注釈の流れ

各レコードに対して、以下の日本語フィールドが表示されます：

| フィールド | 表示ラベル |
|---|---|
| `task_intent_ja` | タスク意図 (日本語) |
| `reconstructed_task_intent_ja` | 再構成タスク意図 (日本語) |
| `task_intent_notes_ja` | タスク意図注記 (日本語) |
| `risk_context` | リスク文脈 |
| `source_ja` | ソース (日本語) |
| `output_ja` | 出力 (日本語) |
| `explanation_ja` | 説明 (日本語・参考) |

その後、3つの選択肢と自由記述の説明を入力するよう促されます。

### 1. Primary Label（1〜6）

```
1. 保存済み                → Preserved
2. 許可された変換          → Authorized Transformation
3. 推論的拡張              → Inferred Extension
4. 未解決のギャップ        → Unresolved Gap
5. 疑わしい逸脱            → Suspicious Drift
6. 重大な歪曲              → Critical Distortion
```

数字1文字を入力してください。

### 2. Risk Flags（a〜g、複数選択可）

```
a. 主張強度の強化          → claim_strength_inflation
b. 不確実性の喪失          → uncertainty_loss
c. 責任の移動              → responsibility_shift
d. 価値の単純化            → value_simplification
e. 制度的含意の喪失        → institutional_implication_loss
f. 文脈の漂流              → context_drift
g. 理論的縮退              → theoretical_reduction
```

文字を連結（`ab`）またはカンマ区切り（`a,b`）で入力してください。  
リスクフラグなしの場合は Enter だけで進めます。

### 3. Criticality（1〜3）

```
1. 低    → low
2. 中    → medium
3. 高    → high
```

数字1文字を入力してください。

### 4. 説明

自由記述の説明を入力します。日本語で入力することを推奨します。

---

## 出力形式

注釈は1レコードにつき1行の JSON として保存されます：

```json
{
  "id": "pilot-sum-001",
  "human_annotation": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "criticality": "medium",
  "explanation": "条件付き表現が削除され、可能性の主張が断定へ変化している。",
  "annotator": "alice",
  "annotated_at": "2026-05-14T09:00:00+00:00",
  "task_intent": "Summarize the policy risk while preserving uncertainty and conditions.",
  "reconstructed_task_intent": "Faithful risk-sensitive summarization.",
  "task_intent_notes": "The task requires preserving caveats because the risk context is policy discussion.",
  "notes": "Pilot summarization sample."
}
```

`task_intent` / `reconstructed_task_intent` / `task_intent_notes` / `notes` は、入力 `pilot_30.jsonl` などに値がある場合に限り、英語フィールドを優先し不足時は対応する `*_ja` からコピーして出力に含めます（空・未設定のキーは行に含めません）。従来どおり最小行にしたい場合は `--skip-pilot-task-meta` を付けます。

### 正規値ルール（Canonical-value rule）

保存される値は、日本語で表示されていても常に英語の正規識別子を使用します：

- `human_annotation` — 6種類の `RdeLabel` 値のいずれか
- `risk_flags` — `KNOWN_RISK_FLAGS` 識別子のリスト
- `criticality` — `low` / `medium` / `high`

---

## 中断と保存

**Ctrl-C** をいつでも押して中断できます。  
既に注釈したレコードは保存済みです。次回のセッションで中断した続きから再開します。

---

## テストの実行

```bash
python -m pytest tests/test_annotate_pilot.py -v
```

選択肢のパース・出力形式・I/O ヘルパー・再開動作を対象としたユニットテストが含まれています。
