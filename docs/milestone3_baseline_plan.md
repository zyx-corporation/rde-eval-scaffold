# Milestone 3 — Baseline Comparison (Plan)

## Purpose

Milestone 3 compares RDE-style judgments with lighter-weight signals recorded on each sample under `baseline_scores` (see [`experiment_plan.md`](experiment_plan.md) and [`milestone1_implementation_plan.md`](milestone1_implementation_plan.md)).

This document describes **phase 1** (lexical, always-on) and **phase 2** (optional neural baselines), plus how they appear on disk.

## Optional dependencies (`[baseline]`)

Lexical baselines use only the Python standard library. BERTScore and similar methods add heavy dependencies (PyTorch via `bert-score`).

Install for local or notebook experiments:

```bash
python -m pip install -e '.[dev,baseline]'
```

CI keeps the default install (`-e ".[dev]"` only) so unit tests must not require `bert-score` unless injected (see tests).

## `baseline_scores` shape (phase 1 — lexical)

Writers MUST keep `baseline_scores` JSON-serializable (same rule as Milestone 1 schema validation).

Phase 1 merges under a **`m3` namespace** so pilots can retain other keys (for example reserved or experimental entries):

```json
{
  "baseline_scores": {
    "bertscore": { "f1": 0.42 },
    "m3": {
      "version": "1",
      "lexical": {
        "sequence_ratio": 0.73,
        "method": "difflib.SequenceMatcher"
      }
    }
  }
}
```

- **`m3.version`**: `"1"` when only lexical metrics are present; **`"2"`** when `m3.bertscore` is also written (phase 2).
- **`lexical.sequence_ratio`**: `difflib.SequenceMatcher` ratio between `source` and `output` (required sample fields).
- **`lexical.method`**: fixed string for reproducibility and exports.

## Phase 2 — BERTScore (optional)

### Role

BERTScore treats each `output` as a **candidate** and each `source` as the **reference** (semantic similarity of generation vs premise). It is a common baseline for summary / rewrite pairs; it does **not** replace RDE’s obligation-aware taxonomy.

### Recording shape

[`rde_eval.bertscore_m3`](../rde_eval/bertscore_m3.py) stores one dict per line under **`m3.bertscore`** (alongside `m3.lexical`):

```json
{
  "m3": {
    "version": "2",
    "lexical": { "sequence_ratio": 0.73, "method": "difflib.SequenceMatcher" },
    "bertscore": {
      "precision": 0.81,
      "recall": 0.79,
      "f1": 0.80,
      "lang": "en",
      "method": "bert-score"
    }
  }
}
```

- **`lang`**: passed to `bert-score` (control with `--bertscore-lang` on the CLI).
- **`method`**: fixed sentinel `bert-score` for exports.

### CLI

With `[baseline]` installed:

```bash
python scripts/run_baselines.py \
  --input data/samples.jsonl \
  --output results/samples_with_m3.jsonl \
  --bertscore \
  --bertscore-lang en
```

Batch scoring is used internally (one model load for all lines). First run may download model weights.

### Implementation notes (reproducibility)

- Pin environments (Python, `bert-score`, and transitive `torch`) when publishing numbers.
- Default model family follows the `bert-score` package defaults for the chosen `lang`; record versions in paper / appendix, not only JSON rows.

### Future work (not implemented)

| Direction | Notes |
|-----------|--------|
| **NLI** | Entailment between `source` and `output` as a numeric or label feature; needs `transformers` + model choice and latency budget. |
| **Factuality / claim checks** | Often API or task-specific; define I/O in a follow-on doc before coding. |
| **LLM-as-judge** | Align with existing `run_prompt_eval` provenance patterns; separate from `bert-score` to avoid double-counting cost. |

These should extend `m3` with new sibling keys (for example `m3.nli`) and bump **`m3.version`** when the subtree contract changes.

## CLI (phase 1)

[`scripts/run_baselines.py`](../scripts/run_baselines.py) reads an input JSONL of samples, computes phase-1 metrics, **merges** into `baseline_scores`, and writes JSONL. With **`--bertscore`**, it also merges phase 2 after `[baseline]` is installed. Extra per-line keys (for example `source_ja`) are preserved.

## Related work (historical)

Phase 1 originally excluded neural baselines; phase 2 adds BERTScore as the first optional neural metric behind `[baseline]`.
