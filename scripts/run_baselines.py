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
        description="Merge Milestone 3 phase-1 baselines (lexical) into baseline_scores."
    )
    parser.add_argument("--input", required=True, help="Input sample JSONL.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    return parser.parse_args()


def _process_line(data: dict[str, Any], *, line_number: int) -> dict[str, Any]:
    missing = [k for k in ("id", "source", "output") if not data.get(k)]
    if missing:
        raise ValueError(
            f"line {line_number}: missing required fields for baselines: {', '.join(missing)}"
        )
    source = str(data["source"])
    output = str(data["output"])
    existing = data.get("baseline_scores")
    merged = merge_milestone3_baseline(existing, source=source, output=output)
    out = dict(data)
    out["baseline_scores"] = merged
    return out


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    try:
        with (
            input_path.open("r", encoding="utf-8") as in_handle,
            output_path.open("w", encoding="utf-8") as out_handle,
        ):
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
                row = _process_line(data, line_number=line_number)
                out_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {n} samples with Milestone 3 baselines -> {args.output}")


if __name__ == "__main__":
    main()
