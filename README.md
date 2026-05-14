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

### Milestone 3: Baseline Comparison

Goal: compare RDE-style evaluation against existing methods.

### Milestone 4: Annotation Reliability

Goal: evaluate whether RDE labels and risk flags can be applied consistently.
