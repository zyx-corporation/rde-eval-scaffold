#!/usr/bin/env python3
"""Milestone 3 — attach deterministic baseline scores to each JSONL sample line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from rde_eval.baselines import merge_milestone3_baseline

DEFAULT_NLI_MODEL = "facebook/roberta-large-mnli"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge Milestone 3 baselines (lexical; optional BERTScore; optional NLI) "
            "into baseline_scores."
        ),
    )
    parser.add_argument("--input", required=True, help="Input sample JSONL.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    parser.add_argument(
        "--bertscore",
        action="store_true",
        help="Also compute BERTScore (requires: pip install -e '.[baseline]').",
    )
    parser.add_argument(
        "--bertscore-lang",
        default="en",
        help="Language code passed to bert-score (default: en).",
    )
    parser.add_argument(
        "--nli",
        action="store_true",
        help="Also compute NLI (requires: pip install -e '.[baseline-nli]' + PyTorch).",
    )
    parser.add_argument(
        "--nli-model",
        default=DEFAULT_NLI_MODEL,
        help=f"Hugging Face model id for sequence NLI (default: {DEFAULT_NLI_MODEL}).",
    )
    parser.add_argument(
        "--nli-batch-size",
        type=int,
        default=8,
        help="Inference batch size for NLI (default: 8).",
    )
    parser.add_argument(
        "--nli-max-length",
        type=int,
        default=512,
        help="Tokenizer max_length for NLI pairs (default: 512).",
    )
    return parser.parse_args()


def _require_row_fields(data: dict[str, Any], *, line_number: int) -> None:
    missing = [k for k in ("id", "source", "output") if not data.get(k)]
    if missing:
        raise ValueError(
            f"line {line_number}: missing required fields for baselines: {', '.join(missing)}"
        )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    try:
        parsed_rows: list[dict[str, Any]] = []
        with input_path.open("r", encoding="utf-8") as in_handle:
            for line_number, line in enumerate(in_handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    data = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
                if not isinstance(data, dict):
                    raise ValueError(f"line {line_number}: expected JSON object")
                _require_row_fields(data, line_number=line_number)
                parsed_rows.append(dict(data))

        for row in parsed_rows:
            merged = merge_milestone3_baseline(
                row.get("baseline_scores"),
                source=str(row["source"]),
                output=str(row["output"]),
            )
            row["baseline_scores"] = merged

        if args.bertscore:
            from rde_eval.bertscore_m3 import compute_bertscore_batch

            bscores = compute_bertscore_batch(
                [str(r["source"]) for r in parsed_rows],
                [str(r["output"]) for r in parsed_rows],
                lang=str(args.bertscore_lang),
            )
            if len(bscores) != len(parsed_rows):
                raise ValueError("internal error: BERTScore batch length mismatch")
            for row, bs in zip(parsed_rows, bscores, strict=True):
                merged = merge_milestone3_baseline(
                    row["baseline_scores"],
                    source=str(row["source"]),
                    output=str(row["output"]),
                    bertscore=bs,
                )
                row["baseline_scores"] = merged

        if args.nli:
            if int(args.nli_max_length) < 8:
                raise ValueError("--nli-max-length must be at least 8")

            from rde_eval.nli_m3 import compute_nli_batch

            nli_scores = compute_nli_batch(
                [str(r["source"]) for r in parsed_rows],
                [str(r["output"]) for r in parsed_rows],
                model_id=str(args.nli_model),
                batch_size=int(args.nli_batch_size),
                max_length=int(args.nli_max_length),
            )
            if len(nli_scores) != len(parsed_rows):
                raise ValueError("internal error: NLI batch length mismatch")
            for row, nd in zip(parsed_rows, nli_scores, strict=True):
                merged = merge_milestone3_baseline(
                    row["baseline_scores"],
                    source=str(row["source"]),
                    output=str(row["output"]),
                    nli=nd,
                )
                row["baseline_scores"] = merged

        with output_path.open("w", encoding="utf-8") as out_handle:
            for row in parsed_rows:
                out_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
    except (ImportError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {n} samples with Milestone 3 baselines -> {args.output}")


if __name__ == "__main__":
    main()
