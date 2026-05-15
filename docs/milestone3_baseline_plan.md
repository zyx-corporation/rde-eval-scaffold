# Milestone 3 — Baseline Comparison (Plan)

## Purpose

Milestone 3 compares RDE-style judgments with lighter-weight signals recorded on each sample under `baseline_scores` (see [`experiment_plan.md`](experiment_plan.md) and [`milestone1_implementation_plan.md`](milestone1_implementation_plan.md)).

This document describes **phase 1** implemented in-repo: deterministic lexical overlap with **no new Python dependencies**.

## `baseline_scores` shape (phase 1)

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

- **`m3.version`**: schema version for the `m3` subtree (increment when fields change).
- **`lexical.sequence_ratio`**: `difflib.SequenceMatcher` ratio between `source` and `output` (required sample fields).
- **`lexical.method`**: fixed string for reproducibility and exports.

Future phases may add sibling keys under `m3` (for example `nli`, `llm_judge`) without renaming `lexical`.

## CLI

[`scripts/run_baselines.py`](../scripts/run_baselines.py) reads an input JSONL of samples, computes phase-1 metrics, **merges** into `baseline_scores`, and writes JSONL. Extra per-line keys (for example `source_ja`) are preserved.

## Related work (not in phase 1)

BERTScore, NLI, factuality APIs, and LLM-as-a-judge require optional dependencies and/or network; they should be specified in a later revision of this plan before implementation.
