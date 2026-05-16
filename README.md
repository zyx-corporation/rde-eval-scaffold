# rde-eval-scaffold

Experimental scaffold for evaluating the Resonant Deviation Evaluator (RDE) framework.

RDE is a framework for auditing meaning changes between a source context and a generated output. This repository is not a production implementation of RDE. It provides a minimal experimental pipeline for constructing source-output pairs, applying RDE labels, comparing baseline evaluators, and analyzing meaning drift.

## Goals

- Provide a small, reproducible evaluation scaffold for RDE.
- Support pilot studies on summarization, rewriting, and specification conversion.
- Represent meaning changes as structured labels, risk flags, criticality, task intent notes, and explanations.
- Compare RDE-style judgments with baseline methods such as semantic similarity, natural language inference, factuality evaluation, and generic LLM-as-a-judge.

## Non-goals

- This is not a production-grade RDE engine.
- This is not a replacement for safety filters, policy filters, or factuality evaluators.
- This repository does not claim that RDE is already validated at scale.
- This repository does not yet include OpenAyane, Kotonoha, SLS, vector DB, or UI integration.

## Runtime Requirement

This repository targets Python 3.12 or later.

## Current Implementation Status

The current implementation is Milestone 1: a deterministic heuristic scaffold for dry-run validation of the RDE schema, label taxonomy, risk flags, JSONL pipeline, CLI output, and basic tests.

Milestone 1 should not be interpreted as a full RDE evaluator or as empirical validation of RDE. It is a reproducibility layer that keeps the experimental format stable before prompt-based and model-based evaluators are introduced.

## Roadmap

### Milestone 1: Heuristic RDE Scaffold

Goal: establish a reproducible scaffold for RDE pilot studies. Scope and completion criteria: [`docs/milestone1_implementation_plan.md`](docs/milestone1_implementation_plan.md).

### Milestone 2: Prompt-based RDE Evaluator

Goal: add a prompt-based evaluator using the same schema and annotation guide.

I/O contract: [`docs/prompt_evaluator_io_contract.md`](docs/prompt_evaluator_io_contract.md). Entrypoints:

```bash
# Stub — fixed JSON per row
python scripts/run_prompt_eval.py \
  --input data/pilot_30.jsonl \
  --output results/prompt_eval_stub.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-stub-local"

# Replay — normalize captured raw_output JSONL (id + raw_output per line)
python scripts/run_prompt_eval.py \
  --mode replay \
  --input data/pilot_30.jsonl \
  --raw-jsonl path/to/captures.jsonl \
  --output results/prompt_eval_replay.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-replay-local"

# Live — OpenAI-compatible chat API (requires API key in env)
export OPENAI_API_KEY=...   # or use --api-key-env
python scripts/run_prompt_eval.py \
  --mode live \
  --model gpt-4o-mini \
  --annotator-id openai \
  --input data/samples.jsonl \
  --output results/prompt_eval_live.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-live" \
  --limit 2 \
  --raw-captures-out results/prompt_eval_captures.jsonl

# Live — DeepSeek (OpenAI-compatible endpoint)
export DEEPSEEK_API_KEY=...
python scripts/run_prompt_eval.py \
  --mode live \
  --model deepseek-chat \
  --api-base-url https://api.deepseek.com/v1 \
  --api-key-env DEEPSEEK_API_KEY \
  --annotator-id deepseek \
  --prompt-version rde-prompt-eval-v1 \
  --input data/pilot_30.jsonl \
  --output results/prompt_eval_deepseek_live.jsonl \
  --raw-captures-out results/prompt_eval_deepseek_captures.jsonl \
  --annotation-run-id "$(date +%Y%m%d)-deepseek-live" \
  --limit 3
```

**Live mode** appends each normalized row to `--output` as it completes (partial results survive Ctrl-C). Re-run with `--resume` to skip IDs already in `--output` (and in `--raw-captures-out`, when set) and append the rest. Transient API errors (429/5xx/network) retry with `--max-retries` and `--retry-backoff-sec`; pace calls with `--request-delay-sec`. Use `--raw-captures-out` to save model JSON for `--mode replay`.

Prompt assembly: `rde_eval.prompt_template` (`rde-prompt-eval-v1`). HTTP client: `rde_eval.llm_client`.

`compare_annotations.py` excludes candidate rows with `normalization_status: failed` from agreement metrics and lists them under `candidate_normalization_failed`. Add `--summary` to print agreement rates and disagreement counts to stdout.

### Milestone 3: Baseline Comparison

Goal: compare RDE-style evaluation against existing methods.

**Phase 1 (in repo):** deterministic lexical overlap via `difflib` — no extra dependencies. See [`docs/milestone3_baseline_plan.md`](docs/milestone3_baseline_plan.md). CLI:

```bash
python scripts/run_baselines.py --input data/samples.jsonl --output results/samples_with_m3.jsonl
```

**Phase 2 (optional):** BERTScore via `pip install -e '.[baseline]'`, then `--bertscore` / `--bertscore-lang`.

```bash
python scripts/run_baselines.py \
  --input data/samples.jsonl \
  --output results/samples_with_m3.jsonl \
  --bertscore
```

**Phase 3 (implemented; install optional):** NLI via `pip install -e '.[baseline-nli]'` plus PyTorch for your platform; then `--nli`, `--nli-model`, **`--nli-max-length`**, and `--nli-batch-size` (completion checklist in [`docs/milestone3_baseline_plan.md`](docs/milestone3_baseline_plan.md)):

```bash
python scripts/run_baselines.py \
  --input data/samples.jsonl \
  --output results/samples_with_m3.jsonl \
  --nli \
  --nli-model facebook/roberta-large-mnli \
  --nli-batch-size 8 \
  --nli-max-length 512
```

Use **`--nli-model`** with a multilingual checkpoint when the pilot rows are not English; `m3.nli.scores` keys follow that model’s `id2labels`.

BERTScore + NLI can be combined (`--bertscore` and `--nli` together).

**Notebook:** [`notebooks/m3_lexical_vs_human.ipynb`](notebooks/m3_lexical_vs_human.ipynb) — baselines vs `human_annotation`; optional **`M3_JSONL`** selects the JSONL path. For the **30-sample pilot corpus**, combine [`scripts/merge_pilot_human_labels.py`](scripts/merge_pilot_human_labels.py) with `run_baselines.py --output results/pilot_30_with_m3.jsonl` — the notebook prefers that artifact when present. Offline smoke data: **`data/fixtures/m3_nli_notebook_smoke.jsonl`** (three rows with `m3.nli.truncated`). **`m3.nli.truncated`** is true when the source–output pair exceeded **`--nli-max-length`** tokens after tokenizer fusion.

(`PYTHONPATH=.` or `pip install -e '.[dev]'` required so `rde_eval` imports resolve.)

### Milestone 4: Annotation Reliability

Goal: evaluate whether RDE labels and risk flags can be applied consistently.

## Repository Structure

```text
rde-eval-scaffold/
  README.md
  README_ja.md
  LICENSE
  pyproject.toml
  docs/
    concept.md
    annotation_guide.md
    experiment_plan.md
    milestone1_implementation_plan.md
    milestone3_baseline_plan.md
    repository_operation.md
  data/
    samples.jsonl
    pilot_30.jsonl
    README.md
    annotations/
      annotations.jsonl
    fixtures/
      m3_nli_notebook_smoke.jsonl
  notebooks/
    m3_lexical_vs_human.ipynb
  rde_eval/
    __init__.py
    baselines.py
    bertscore_m3.py
    nli_m3.py
    schema.py
    classifier.py
    evaluator.py
    prompt_eval.py
    llm_client.py
  scripts/
    annotate_pilot.py
    compare_annotations.py
    merge_pilot_human_labels.py
    export_results.py
    run_baselines.py
    run_eval.py
    run_prompt_eval.py
  tests/
    test_schema.py
    test_classifier.py
    test_evaluator.py
    test_export_results.py
  results/
    .gitkeep
```

## Data Format

Each sample is represented as one JSON object per line.

The current `data/samples.jsonl` file contains minimal dry-run examples for schema and pipeline validation.

The **`data/pilot_30.jsonl`** file is the pilot corpus (30 paired samples). Primary human annotations for those IDs are recorded one-per-line in **`data/annotations/annotations.jsonl`**, aligned with [`docs/experiment_plan.md`](docs/experiment_plan.md) (10 summarization / 10 rewriting / 10 specification conversion).

[`scripts/merge_pilot_human_labels.py`](scripts/merge_pilot_human_labels.py) writes a combined JSONL (pilot bodies + authoritative annotation overlay) suitable for **`run_baselines.py`** / analysis — see **`data/README.md`**.

## Invoking repository scripts

Several scripts under `scripts/` import the `rde_eval` package (for example `run_eval.py`, `annotate_pilot.py`, `run_baselines.py`, and `run_prompt_eval.py`). From a plain checkout, running `python scripts/…` without installing the package fails with `ModuleNotFoundError: No module named 'rde_eval'` because the project directory is not on `sys.path`.

Use either of the following from the **repository root**:

1. **Editable install (recommended for development)**

   ```bash
   python -m pip install -e '.[dev]'
   ```

   (Zsh treats `.[dev]` as a glob unless quoted.)

2. **Set `PYTHONPATH` for ad-hoc runs** — prefix each script invocation:

   ```bash
   PYTHONPATH=. python scripts/run_eval.py --help
   ```

`scripts/compare_annotations.py`, `scripts/export_results.py`, and `scripts/merge_pilot_human_labels.py` do not import `rde_eval`, so they may run without these steps, but using the same environment keeps behavior consistent.

## Minimal Usage

After `python -m pip install -e '.[dev]'` (or by prefixing each `python` line with `PYTHONPATH=.`):

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

The evaluation CLI exits with status **1** on invalid JSONL, schema errors, or I/O failures; **0** on success.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
