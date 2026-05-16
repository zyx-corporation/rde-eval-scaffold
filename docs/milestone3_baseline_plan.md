# Milestone 3 — Baseline Comparison (Plan)

## Purpose

Milestone 3 compares RDE-style judgments with lighter-weight signals recorded on each sample under `baseline_scores` (see [`experiment_plan.md`](experiment_plan.md) and [`milestone1_implementation_plan.md`](milestone1_implementation_plan.md)).

This document describes **phase 1** (lexical, always-on), **phase 2** (optional BERTScore), and **phase 3** (optional NLI), plus how metrics appear on disk.

## Optional dependencies (`[baseline]`, `[baseline-nli]`)

Lexical baselines use only the Python standard library. BERTScore and similar methods add heavy dependencies (PyTorch via `bert-score`).

Install for local or notebook experiments:

```bash
python -m pip install -e '.[dev,baseline]'
```

For the NLI stack (phase 3), add **`[baseline-nli]`** (`transformers`; PyTorch as required by your platform).

```bash
python -m pip install -e '.[dev,baseline,baseline-nli]'
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

- **`m3.version`**: `"1"` lexical only; **`"2"`** when `m3.bertscore` is present and NLI is absent; **`"3"`** when `m3.nli` is present (BERTScore may also be present).
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

### Future extensions (not implemented)

| Direction | Notes |
|-----------|--------|
| **Factuality / claim checks** | Often API or task-specific; define I/O in a follow-on doc before coding. |
| **LLM-as-judge** | Align with existing `run_prompt_eval` provenance patterns; separate from `bert-score` to avoid double-counting cost. |

## Phase 3 — NLI (optional dependency; implementation **complete**)

### Role

A standard **premise–hypothesis** NLI model scores whether `output` (**hypothesis**) is entailed by `source` (**premise**). This is a blunt signal: it does **not** encode caveat preservation, institutional responsibility, or RDE risk flags.

Implementation: [`rde_eval.nli_m3`](../rde_eval/nli_m3.py) uses `transformers` **sequence classification** (one forward pass per batch); heavy imports stay inside the helper and the CLI.

### Optional dependencies

Install **`[baseline-nli]`** from `pyproject.toml` (see repository) **and** a PyTorch build for your platform. Typical install:

```bash
python -m pip install -e '.[dev,baseline,baseline-nli]'
```

Omit **`[baseline]`** if BERTScore is not needed. Pin `transformers` / `torch` / CUDA for published results.

### Recording shape

[`rde_eval.nli_m3.compute_nli_batch`](../rde_eval/nli_m3.py) writes **`m3.nli`** next to `lexical` / `bertscore`:

```json
{
  "m3": {
    "version": "3",
    "lexical": {
      "sequence_ratio": 0.73,
      "method": "difflib.SequenceMatcher"
    },
    "bertscore": {
      "precision": 0.81,
      "recall": 0.79,
      "f1": 0.80,
      "lang": "en",
      "method": "bert-score"
    },
    "nli": {
      "method": "transformers-sequence-classification",
      "model_id": "facebook/roberta-large-mnli",
      "premise": "source",
      "hypothesis": "output",
      "label": "neutral",
      "scores": {
        "entailment": 0.12,
        "neutral": 0.55,
        "contradiction": 0.33
      },
      "truncated": false
    }
  }
}
```

- **`label`**: argmax class name (lowercase; keys follow the model’s `id2label` strings).
- **`scores`**: softmax probabilities keyed by normalized class name; keys must stay stable for a given **`model_id`**.
- **`model_id`**: Hugging Face hub id or local path string used for reproducibility.

- **`truncated`**: `true` when the tokenized source–output pair was longer than **`--nli-max-length`** (inference still uses truncation).

**Version rule:** set **`m3.version` to `"3"`** whenever **`m3.nli`** is written, even if BERTScore is omitted (lexical + NLI only).

### Operational notes

1. **Batching:** the model and tokenizer load **once**; use `--nli-batch-size` to tune memory.
2. **Truncation:** tokenizer uses **`--nli-max-length`** (default 512) with truncation; each row records **`m3.nli.truncated`** when the full pair would have exceeded that budget.
3. **Multilingual pilots:** pick a multilingual NLI checkpoint and pass it via **`--nli-model`**, or filter rows by language.
4. **First run:** Hugging Face may download weights for **`--nli-model`** (default `facebook/roberta-large-mnli`).

### CLI

With `[baseline-nli]` and PyTorch installed:

```bash
python scripts/run_baselines.py \
  --input data/samples.jsonl \
  --output results/samples_with_m3.jsonl \
  --nli \
  --nli-model facebook/roberta-large-mnli \
  --nli-batch-size 8 \
  --nli-max-length 512
```

Combine with **`--bertscore`** when `[baseline]` is also installed.

### Phase 3 exit criteria (all satisfied)

- [x] `m3.nli` subtree on disk matches the schema (`label`, `scores`, `model_id`, **`truncated`**, premise/hypothesis sentinels).
- [x] `m3.version` is **`"3"`** whenever **`m3.nli`** is present (BERTScore optional).
- [x] CLI **`--nli`**, **`--nli-model`**, **`--nli-batch-size`**, **`--nli-max-length`** wired in `scripts/run_baselines.py`.
- [x] **`truncated`** is derived from tokenizer length **without truncation** versus **`max_length`** (truncation still applies at inference).
- [x] Tests cover merge/versioning via mocks; optional stack remains off the default **`[dev]`** CI install.

Future work (explicitly **out of Phase 3**): factuality / LLM-as-a-judge rows in the plan’s “future extensions” table.

## CLI (summary)

[`scripts/run_baselines.py`](../scripts/run_baselines.py) reads JSONL samples, merges **lexical** baselines, optionally **`--bertscore`** (requires `[baseline]`), and optionally **`--nli`** (requires `[baseline-nli]` + PyTorch). Extra per-line keys (for example `source_ja`) are preserved.

## Related work (historical)

Phase 1 excluded neural baselines; phase 2 adds BERTScore behind `[baseline]`; phase 3 adds NLI behind `[baseline-nli]` with `m3.nli` on disk.
