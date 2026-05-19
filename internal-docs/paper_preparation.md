# Paper preparation kit (RDE pilot scaffold)

> **Internal draft note:** This document contains manuscript-preparation notes and claim-boundary drafts. It is kept under `internal-docs/` so the public artifact surface remains focused on reproducible data, code, schemas, and documentation.

> **読者ノート（日本語）:** フル日本語の同型ドキュメントは **[`paper_preparation_ja.md`](paper_preparation_ja.md)** にあります。以下は英語ドラフト・BibTeX を中心とした版です。

> **読者ノート（日本語）:** この文書は、本リポジトリで実際にコード化されている実験（パイロット `N=30`、Milestone 3 ベースライン、人手注釈パイプライン）と**論文で許容できる主張の境界**を揃えるための下書き集です。**本文ドラフトは英語セクションが中心**です（国際論文・英語紀要を想定）。リポジトリの一次情報は各リンクを参照してください。

## 1. Scope: what this repository can and cannot support

Use this scaffold to report a **controlled pilot feasibility / taxonomy-use study**.

| Safe to claim (with calibration) | Do **not** claim without extra evidence |
|-----------------------------------|----------------------------------------|
| A reproducible **annotation workflow** + label taxonomy (+ risk flags) applied to structured source–output pairs | A **validated**, **inter-annotator–reliable** benchmark at scale |
| **Exploratory** correlations between taxonomy labels / flags and auxiliary baselines (lexical similarity, optional BERTScore / NLI) | That baselines **replace** human RDE adjudication |
| Transparency on **prompt evaluators**, baselines (`baseline_scores`), and schema | That RDE substitutes for factuality, safety policy, or production auditing |

Formal caveats belong in **`docs/experiment_plan.md`** (purpose, exploratory outputs; single-annotator note).

## 2. Contributing / framing paragraphs (draft, English)

**Problem & goal (short).** Meaning drift across source–generation pairs interacts with accountability and governance: updates can quietly alter claim strength, uncertainty, institutional responsibility, and value framing. **Resonant Deviation Evaluator (RDE)** models these effects as audit-oriented primary labels (`human_annotation`) and structured risk flags, rather than collapsing judgment to similarity or entailment scores alone.

**This artifact.** We distribute a reproducible scaffold (schema, deterministic dry-run heuristic, baseline writers, notebook exploration) oriented to **pilot** studies on summarization, rewriting, and specification-conversion-inspired tasks (**`N = 30`** in `data/pilot_30.jsonl`). See **`docs/concept.md`** for the operational Δ-M perspectives and **`docs/annotation_guide.md`** for adjudication semantics.

Adjust tone to venue (systems vs. HCI vs. NLP evaluation).

## 3. Experimental design paragraph (verbatim-friendly facts)

- **Samples:** \(N = 30\) English pilot instances in **`data/pilot_30.jsonl`**, stratified **10 summarization**, **10 rewriting**, **10 specification conversion** (**`task`** column), motivated by **`docs/experiment_plan.md`** §Initial Design table.
- **Fields:** Required `source` / `output` / `risk_context` / plus optional bilingual strings (`*_ja`) when present — report exactly what you analyse.
- **Human judgments:** Stored one JSON object per line in **`data/annotations/annotations.jsonl`**, keyed by **`id`**, including primary label (**`human_annotation`**), **`risk_flags`**, **`criticality`**, textual **`explanation`**, and (**when captured**) **`task_intent`** / **`reconstructed_task_intent`** / **`task_intent_notes`**. Annotator pseudonym (**`annotator`**) and ISO timestamp (**`annotated_at`**) accompany each row.

**Merged analysis file (recommended for analyses that need both corpus text and adjudication):** overlay annotations onto the corpus with **`scripts/merge_pilot_human_labels.py`** (see **`data/README.md`**), producing e.g. `results/pilot_30_with_human.jsonl`, before optional baseline attachment.

### Task-intention reconstruction sentence (optional Methods)

Annotators reconstructed underspecified prompts under **`task_intent`**, **`reconstructed_task_intent`**, and **`task_intent_notes`**, documenting why reconstruction was necessary (**`docs/experiment_plan.md`**, **`docs/annotation_guide.md`** boundary rules).

### Single annotator caveat (recommended Limitations boilerplate)

If only **one primary human annotator** contributed the released labels, describe the dataset explicitly as **pilot annotation**, not validated inter-rater-agreement adjudication (**`docs/experiment_plan.md`**, Notes).

## 4. Automated baselines (Milestone 3) — wording for Methods

Baseline metrics are persisted under **`baseline_scores.m3`** (**`docs/milestone3_baseline_plan.md`**).

| Component | Implemented in repo | Typical reporting knobs |
|-----------|---------------------|--------------------------|
| **Lexical similarity** (`difflib.SequenceMatcher`-style ratio → `baseline_scores.m3.lexical.sequence_ratio`) | Always on when **`scripts/run_baselines.py`** writes `m3` | Deterministic across Python builds; cite method string on disk (`lexical.method`) |
| **BERTScore F1 (+ P/R)** | Optional **`--bertscore`**, `[baseline]` extra | Record `lang`, **`bert-score` package + PyTorch pins**, checkpoint family |
| **NLI softmax + argmax label** | Optional **`--nli`**, `[baseline-nli]` + PyTorch | Record **`model_id`**, **`m3.nli.scores`** key ordering, and **`truncated`** when fused token length exceeds **`--nli-max-length`** |

**Integrity rule:** **`m3.version`** is **`"3"`** when NLI rows exist (**`"2"`** BERT-only, **`"1"`** lexical-only).

## 5. Computational reproduction (paper appendix / artifact checklist)

Minimal sequence for the **combined pilot + adjudication + optional neural baselines** path:

```bash
python -m pip install -e '.[dev]'
# optional heavy stacks (pin for camera-ready):
# python -m pip install -e '.[baseline]'        # BERTScore
# python -m pip install -e '.[baseline-nli]'   # transformers NLI (+ torch)

python scripts/merge_pilot_human_labels.py \
  --pilot data/pilot_30.jsonl \
  --annotations data/annotations/annotations.jsonl \
  --output results/pilot_30_with_human.jsonl

PYTHONPATH=. python scripts/run_baselines.py \
  --input results/pilot_30_with_human.jsonl \
  --output results/pilot_30_with_m3.jsonl
# Append --bertscore / --nli ... as analysed in the manuscript.
```

Notebook / exploratory alignment: **`notebooks/m3_lexical_vs_human.ipynb`** auto-prefers `results/pilot_30_with_m3.jsonl` unless **`M3_JSONL`** overrides (see README Milestone 3 section).

Regression coverage: **`tests/test_pilot_annotation_coverage.py`** (ID completeness + balanced task counts) and **`tests/test_merge_pilot_human_labels.py`**.

Report **exact** commit hash (**`git rev-parse HEAD`**), **`python`** version (**>=3.12** per `pyproject.toml`), **`pytest`** pass status for that hash, GPU/CPU, and (**if neural baselines**) model download provenance (**Hugging Face** hub ids recorded in **`m3.nli.model_id`**, etc.).

## 6. Optional prompt-based evaluator positioning

Prompt evaluation (`scripts/run_prompt_eval.py`, **`docs/prompt_evaluator_io_contract.md`**) is **separate from** adjudicated human labels unless you deliberately merge/normalize outputs upstream. Mention **modes** (**stub**, **replay**, **live**) and reproducibility artefacts (`--raw-captures-out`) if the paper cites LLM-produced candidate labels vs. human adjudication (**`scripts/compare_annotations.py`**).

## 7. Figures & tables backlog (submission checklist)

- [ ] Stratified **`task`** counts (10 / 10 / 10).
- [ ] Primary label histogram + risk-flag co-occurrence (sankey / heatmaps).
- [ ] (**If baselines**) Distributional overlays: lexical ratio, optional BERTScore F1, NLI label probabilities — align with notebooks or export scripts.
- [ ] Mention **`m3.nli.truncated`** prevalence if truncation materially affects entailment-heavy rows.
- [ ] Transparency table: corpus version (commit), annotator pseudonym logic, adjudication timestamps.

## 8. Starter BibTeX / citation placeholders

Populate venue pages / DOIs before submission; keep software versions mirrored in an artifact appendix.

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

## 9. Editorial hygiene before submission

- [ ] Harmonize nomenclature: **Δ-M axes** (**`concept.md`**), **`human_annotation`** label set vs. prose names.
- [ ] Decide whether bilingual fields (`*_ja`) enter analysis scope; cite if excluded.
- [ ] Register limitations: pilot power, taxonomy scope, evaluator stack scope.
- [ ] IRB / human-subjects wording if annotations involve sensitive domains (risk contexts enumerated per row).

## 10. jXiv-oriented manuscript checklist (GitHub **`#2`**)

RDE論文本体の TeX / Word は**本リポ外**で管理されていますが、改版時は次で Issue のスコープと整合させます。

### Related Work & citations

- [ ] Related Work の各項に**本文引用**を付ける（会誌スタイルに合わせる）。
- [ ] 「既存評価指標」の批判と、「Δ-M 受容可否をラベル＋フラグで監査する RDE」の立場を峻別する（詳細語彙は **`concept.md`** / **`annotation_guide.md`** と一致させる）。

### 構成・重複削除

- [ ] **比較節（metric comparison）**と**問題提起（missing layer）**の重複を削る。
- [ ] Problem 節では、字面類似や単一要約指標だけでは覆い切れない**制度的・責任・不確実性**の監査必要性を論じる。

### パイロット記述の事実確認

- [ ] **実施済み**の人手ラベルを書く場合は、このリポの **`data/annotations/annotations.jsonl`** と **`merge_pilot_human_labels.py`** での証跡・コミットを指す（「計画のみ」なら明示）。
- [ ] Appendix では GitHub README の転載は避け、**`annotation_guide.md`** / **`experiment_plan.md`** を主付録にする。

### 限界（必須）

- [ ] 現状レポでは**単一または限定された Annotator のパイロット**であり、**一般化された検証**ではないと明記する（なければ多評者kappa等は主張しない）。
- [ ] **`pilot_30_reference_placeholder.jsonl`** を触れるときは「スモーク用・非ゴールド」と明記する。
