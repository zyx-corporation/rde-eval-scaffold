#!/usr/bin/env python3
"""Milestone 3 — attach deterministic baseline scores to each JSONL sample line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from rde_eval.baselines import merge_milestone3_baseline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge Milestone 3 baselines (lexical; optional BERTScore) into baseline_scores."
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
    return parser.parse_args()


def _require_row_fields(data: dict[str, Any], *, line_number: int) -> tuple[str, str, str]:
    missing = [k for k in ("id", "source", "output") if not data.get(k)]
    if missing:
        raise ValueError(
            f"line {line_number}: missing required fields for baselines: {', '.join(missing)}"
        )
    return str(data["id"]), str(data["source"]), str(data["output"])


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
