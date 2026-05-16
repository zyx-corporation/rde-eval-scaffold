# Milestone 3 Implementation Plan

## Status

**Completed (2026-05-16).** Closure criteria below are satisfied. Normative on-disk shapes and CLI flags remain in [`milestone3_baseline_plan.md`](milestone3_baseline_plan.md).

## Purpose

Milestone 3 compares lighter-weight signals (lexical overlap, optional BERTScore, optional NLI) with RDE-style records by writing **`baseline_scores.m3`** on each JSON line. It does **not** replace human adjudication or prove benchmark claims.

## Non-goals

- Production factuality or safety certification
- LLM-as-judge or claim-level checks inside `m3` (may be a future milestone; see baseline plan “Future extensions”)
- Statistical guarantees for pilot-scale rows

## Scope

| Layer | Role |
|-------|------|
| **Phase 1** | Always-on lexical ratio under `m3.lexical` (`rde_eval.baselines`) |
| **Phase 2** | Optional BERTScore under `m3.bertscore` (`[baseline]`) |
| **Phase 3** | Optional NLI under `m3.nli` (`[baseline-nli]` + PyTorch) |
| **CLI** | [`scripts/run_baselines.py`](../scripts/run_baselines.py) |
| **Analysis** | [`notebooks/m3_lexical_vs_human.ipynb`](../notebooks/m3_lexical_vs_human.ipynb), merge path via [`scripts/merge_pilot_human_labels.py`](../scripts/merge_pilot_human_labels.py) |

Phase 3 implementation exit criteria in the baseline plan are satisfied; milestone closure additionally required the workflow and documentation items below.

## Completion criteria (milestone closure)

Milestone 3 is **complete** when:

1. **Specification:** `baseline_scores` / `m3` behavior matches [`milestone3_baseline_plan.md`](milestone3_baseline_plan.md) (version rules, lexical, optional bertscore/nli, `truncated`).
2. **CLI:** `run_baselines.py` supports documented flags; invalid inputs fail with clear errors.
3. **Tests & CI:** default `pytest` + `ruff` pass on `[dev]` without downloading torch or BERTScore weights (mocks / skips as today).
4. **Pilot path:** README and `data/README.md` describe **merge pilot + run baselines + notebook** in one place; smoke fixture `data/fixtures/m3_nli_notebook_smoke.jsonl` remains valid.
5. **Consistency:** root README, Japanese README, this plan, and the baseline plan stay aligned on scope and commands.

All items are **satisfied** in the repository as of the completion date above.

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Lexical merge + versioning | `rde_eval/baselines.py` |
| Optional BERTScore batch | `rde_eval/bertscore_m3.py` |
| Optional NLI batch | `rde_eval/nli_m3.py` |
| CLI | `scripts/run_baselines.py` |
| Technical spec (normative) | `docs/milestone3_baseline_plan.md` |
| Tests | `tests/test_baselines.py`, `tests/test_bertscore_m3.py`, `tests/test_nli_m3.py`, `tests/test_run_baselines_cli.py`, … |

## Next step

**Milestone 4** — annotation reliability (see [`README.md`](../README.md) roadmap).
