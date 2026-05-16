# 論文準備キット（RDE パイロット・スキャフォールド）

> **使い方:** 本リポジトリでコード化されている実験（パイロット \(N=30\)、Milestone 3 ベースライン、人手注釈パイプライン）と、**論文で許容できる主張の境界**を揃えるための下書き・チェックリストです。英語の投稿を想定する場合は、フレーズ草案や BibTeX は [`paper_preparation.md`](paper_preparation.md) と併用してください。

## 1. スコープ：このリポジトリが支えられる主張／支えられない主張

本スキャフォールドは、**管理されたパイロットの実現可能性・タクソノミー適用研究**として報告する用途を想定します。

| キャリブレーション付きで主張しうること | 追加根拠なしでは主張しないこと |
|----------------------------------------|----------------------------------|
| 再現可能な**注釈ワークフロー**＋一次ラベル体系（＋リスクフラグ）を、構造化された source–output 対に適用したこと | 大規模な**妥当性検証済み**・**評価者間で十分に再現可能な**ベンチマークであること |
| タクソノミーラベル／フラグと補助ベースライン（字句類似、任意の BERTScore／NLI）との**探索的**な関連 | ベースラインが人手 RDE 裁定を**代替する**こと |
| プロンプト系評価器、`baseline_scores`、スキーマに対する**透明性** | RDE がファクトチェック、安全ポリシー、本番監査の**代替**であること |

形式的な注意書きは **`docs/experiment_plan.md`**（目的、探索的出力、単一注釈者に関する注）に沿ってください。

## 2. 問題設定・フレーム（下書き案・日本語）

**課題と目標（短文）。** source と生成物のペアにわたる意味のずれは、説明責任とガバナンスと結びつく。更新が静かに主張の強さ、不確実性、制度的責任、価値枠の見え方を変えうる。**Resonant Deviation Evaluator（RDE）** は、これを類似度や含意スコアだけに還元せず、監査志向の一次ラベル（`human_annotation`）と構造化されたリスクフラグとしてモデル化する。

**本成果物。** スキーマ、決定的なドライラン用ヒューリスティック、ベースライン書き込み、ノートブック探索を含む再現可能なスキャフォールドを配布する。対象は要約・リライト・仕様変換に着想を得たタスクの**パイロット**（**`data/pilot_30.jsonl`** で **\(N = 30\)**）。操作化された Δ-M の観点は **`docs/concept.md`**、裁定の意味論は **`docs/annotation_guide.md`** を参照。

文体は掲載誌（システムズ／HCI／NLP 評価など）に合わせて調整してください。

## 3. 実験デザイン（そのまま事実として書ける箇所）

- **サンプル:** **`data/pilot_30.jsonl`** に英語パイロット **\(N = 30\)**。**`task`** 列で **要約 10・リライト 10・仕様変換 10** に層化。根拠は **`docs/experiment_plan.md`** の初期設計表。
- **フィールド:** 必須の `source` / `output` / `risk_context` に加え、任意の日本語フィールド（`*_ja`）があれば分析対象として正確に記載する。
- **人手判断:** **`data/annotations/annotations.jsonl`** に **`id`** ごとに 1 行 1 オブジェクト。一次ラベル（**`human_annotation`**）、**`risk_flags`**、**`criticality`**、文言 **`explanation`**、（取得できていれば）**`task_intent`** / **`reconstructed_task_intent`** / **`task_intent_notes`**。注釈者の通称（**`annotator`**）と ISO 時刻（**`annotated_at`**）が各行に付く。

**統合分析用ファイル（コーパス本文と裁定の両方が要る分析向けの推奨手順）:** **`scripts/merge_pilot_human_labels.py`** で注釈をコーパスに重ねる（**`data/README.md`** 参照）。例: `results/pilot_30_with_human.jsonl` を得てから、任意でベースラインを付与する。

### タスク意図の再構成（Methods の任意の一文）

注釈者は、不十分なプロンプトに対して **`task_intent`**、**`reconstructed_task_intent`**、**`task_intent_notes`** のもとで意図を再構成し、なぜ再構成が必要だったかを記録した（**`docs/experiment_plan.md`**、**`docs/annotation_guide.md`** の境界ルール）。

### 単一（または限定された）注釈者の注意（Limitations の推奨ボイラープレート）

公開ラベルが**主たる人手注釈者が一人**（または少数に限られる）場合、データセットを**パイロット注釈**として記述し、評価者間一致が検証済みの裁定データではないと明記する（**`docs/experiment_plan.md`** Notes）。

## 4. 自動ベースライン（Milestone 3）— Methods 向けの言い回し

ベースライン指標は **`baseline_scores.m3`** に保存する（**`docs/milestone3_baseline_plan.md`**）。

| 要素 | リポジトリ内の実装 | 報告で触れるとよい点 |
|------|---------------------|----------------------|
| **字句類似**（`difflib.SequenceMatcher` 系 ratio → `baseline_scores.m3.lexical.sequence_ratio`） | **`scripts/run_baselines.py`** が `m3` を書くとき常に含まれる | Python 実装間で決定的；ディスク上の `lexical.method` を引用可能 |
| **BERTScore F1（+ P/R）** | 任意 **`--bertscore`**、`[baseline]` extra | `lang`、**`bert-score` パッケージと PyTorch のピン**、チェックポイント系 |
| **NLI の softmax と argmax ラベル** | 任意 **`--nli`**、`[baseline-nli]` + PyTorch | **`model_id`**、**`m3.nli.scores`** のキー順、融合トークン長が **`--nli-max-length`** を超えた場合の **`truncated`** |

**整合ルール:** NLI 行があるとき **`m3.version`** は **`"3"`**（**`"2"`** は BERT のみ、**`"1"`** は字句のみ）。

## 5. 計算上の再現（論文付録／成果物チェックリスト）

**パイロット＋裁定＋任意のニューラルベースライン**をまとめる最小例:

```bash
python -m pip install -e '.[dev]'
# 重い依存（カメラレディではピンを固定）:
# python -m pip install -e '.[baseline]'        # BERTScore
# python -m pip install -e '.[baseline-nli]'   # transformers NLI (+ torch)

python scripts/merge_pilot_human_labels.py \
  --pilot data/pilot_30.jsonl \
  --annotations data/annotations/annotations.jsonl \
  --output results/pilot_30_with_human.jsonl

PYTHONPATH=. python scripts/run_baselines.py \
  --input results/pilot_30_with_human.jsonl \
  --output results/pilot_30_with_m3.jsonl
# 本論で分析する場合のみ --bertscore / --nli ... を付与
```

探索用ノートブック: **`notebooks/m3_lexical_vs_human.ipynb`** は **`M3_JSONL`** が無ければ `results/pilot_30_with_m3.jsonl` を優先（英語 README の Milestone 3 節）。

回帰テスト: **`tests/test_pilot_annotation_coverage.py`**（ID の網羅とタスク件数バランス）、**`tests/test_merge_pilot_human_labels.py`**。

報告すべき例: **正確なコミットハッシュ**（**`git rev-parse HEAD`**）、**`python`** 版（**`pyproject.toml`** どおり **>=3.12**）、そのハッシュでの **`pytest`** 成否、GPU/CPU、（ニューラルベースライン使用時は）モデル入手経路（**Hugging Face** の hub id は **`m3.nli.model_id`** 等に記録）。

## 6. プロンプト系評価器の位置づけ（任意）

プロンプト評価（**`scripts/run_prompt_eval.py`**、**`docs/prompt_evaluator_io_contract.md`**）は、上流で明示的にマージしない限り**人手裁定とは別層**である。**モード**（**stub**、**replay**、**live**）と再現用成果物（**`--raw-captures-out`**）を、LLM 候補ラベルと人手裁定を対比して引用する場合に記す（**`scripts/compare_annotations.py`**）。

## 7. 図表の下書き（投稿前チェックリスト）

- [ ] **`task`** の層化件数（10 / 10 / 10）。
- [ ] 一次ラベルヒストグラム＋リスクフラグ共起（サンキー／ヒートマップ等）。
- [ ] （ベースライン使用時）字句 ratio、任意の BERTScore F1、NLI ラベル確率の分布比較 — ノートブックや export と一致させる。
- [ ] 含意に依存する行で打ち切りが材料に効く場合、**`m3.nli.truncated`** の割合に触れる。
- [ ] 透明性表: コーパス版（コミット）、注釈者通称の扱い、裁定タイムスタンプ。

## 8. 入門用 BibTeX（引用プレースホルダ）

掲載確定後にページ／DOI を埋める。ソフトウェア版は成果物付録と整合させる。

```bibtex
@inproceedings{zhang2020bertscore,
  title     = {{BERTScore}: Evaluating Text Generation with {BERT}},
  author    = {Zhang, Tianyi and others},
  booktitle = {ICLR},
  year      = {2020},
  note      = {\texttt{pip} package \texttt{bert-score}}
}

@inproceedings{liu2019roberta,
  title        = {{RoBERTa}: A Robustly Optimized {BERT} Pretraining Approach},
  author       = {Liu, Yinhan and others},
  booktitle    = {ArXiv preprint},
  year         = {2019},
  note         = {checkpoint family incl. sentence-pair NLU models}
}

@manual{rde-eval-scaffold,
  title        = {rde-eval-scaffold},
  author       = {{Kano, Tomoyuki}},
  organization = {ZyX Corporation repository},
  year         = {2026},
  url          = {https://github.com/zyx-corporation/rde-eval-scaffold},
  note         = {Version \texttt{v0.1.0}; commit hash \& environment pins required in appendix}
}
```

## 9. 投稿前の編集上の整理

- [ ] 用語の統一: **Δ-M 軸**（**`concept.md`**）、**`human_annotation`** のラベル集合と本文中の名称。
- [ ] 二言語フィールド（`*_ja`）を分析に含めるか否か；除外するなら理由を書く。
- [ ] 限界の登録: パイロットの検出力、タクソノミーの射程、評価器スタックの射程。
- [ ] リスクコンテキストがセンシティブな領域を含む場合の IRB・被験者取り扱いの文言。

## 10. jXiv 向け原稿チェックリスト（GitHub **`#2`**）

RDE 論文本体の TeX / Word はリポ外で管理されていても、改版時は次で Issue スコープと整合させます。

### Related Work・引用

- [ ] Related Work の各項目に**本文引用**を付ける（会誌スタイルに合わせる）。
- [ ] 「既存評価指標」への批判と、「Δ-M 受容可否をラベル＋フラグで監査する RDE」の立場を峻別する（語彙は **`concept.md`** / **`annotation_guide.md`** と一致）。

### 構成・重複削減

- [ ] **比較節（metric comparison）**と**問題提起（missing layer）**の重複を削る。
- [ ] Problem 節では、字面類似や単一要約指標だけでは覆い切れない**制度的・責任・不確実性**の監査必要性を論じる。

### パイロット記述の事実確認

- [ ] **実施済み**の人手ラベルを書く場合は **`data/annotations/annotations.jsonl`** と **`merge_pilot_human_labels.py`** の証跡・コミットを指す（計画のみなら明示）。
- [ ] 付録では GitHub README の転載を避け、**`annotation_guide.md`** / **`experiment_plan.md`** を主付録にする。

### 限界（必須）

- [ ] 現状レポは**単一または限定された Annotator のパイロット**であり、**一般化された検証**ではないと明記する（多評者 κ 等は主張しない）。
- [ ] **`pilot_30_reference_placeholder.jsonl`** に触れるときは「スモーク用・非ゴールド」と明記する。

---

**関連:** 英語版・国際投稿向けの英語フレーズ草案は [`paper_preparation.md`](paper_preparation.md)。
