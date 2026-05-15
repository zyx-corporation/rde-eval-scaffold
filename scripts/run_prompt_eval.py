#!/usr/bin/env python3
"""Milestone 2 prompt-evaluator pipeline entrypoint.

Reads pilot-style JSONL and writes normalized LLM annotation JSONL per
``docs/prompt_evaluator_io_contract.md``.

Modes:
  stub   — fixed in-process JSON per row (no network)
  replay — normalize captured ``raw_output`` rows from ``--raw-jsonl``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from rde_eval.prompt_eval import (
    build_failure_record,
    load_raw_outputs_by_id,
    normalize_model_output,
    stub_model_raw_output,
)


def _load_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(data, dict):
                raise ValueError(f"Line {line_number}: expected JSON object")
            rows.append(data)
    return rows


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Milestone 2 prompt evaluator (stub / replay normalization; no live API)."
    )
    parser.add_argument(
        "--input", required=True, help="Input pilot JSONL (e.g. data/pilot_30.jsonl)."
    )
    parser.add_argument("--output", required=True, help="Output JSONL path for normalized records.")
    parser.add_argument(
        "--mode",
        choices=("stub", "replay"),
        default="stub",
        help="stub: fixed JSON per row; replay: normalize --raw-jsonl captures by id.",
    )
    parser.add_argument(
        "--raw-jsonl",
        help="Replay mode: JSONL with id + raw_output per line (model capture).",
    )
    parser.add_argument("--annotator-type", default="llm", help="Provenance: annotator_type.")
    parser.add_argument("--annotator-id", default="stub", help="Provenance: annotator_id.")
    parser.add_argument("--model", default="stub-model", help="Provenance: model identifier.")
    parser.add_argument(
        "--prompt-version",
        default="rde-prompt-eval-stub-v1",
        help="Provenance: prompt_version string.",
    )
    parser.add_argument(
        "--annotation-run-id",
        required=True,
        help="Provenance: annotation_run_id (caller-supplied run label).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        print(f"Error: input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "replay" and not args.raw_jsonl:
        print("Error: --mode replay requires --raw-jsonl", file=sys.stderr)
        sys.exit(1)

    provenance = {
        "annotator_type": args.annotator_type,
        "annotator_id": args.annotator_id,
        "model": args.model,
        "prompt_version": args.prompt_version,
        "annotation_run_id": args.annotation_run_id,
    }

    try:
        records_in = _load_jsonl_objects(input_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    raw_by_id: dict[str, str] = {}
    if args.mode == "replay":
        raw_path = Path(args.raw_jsonl)
        if not raw_path.is_file():
            print(f"Error: raw JSONL not found: {raw_path}", file=sys.stderr)
            sys.exit(1)
        try:
            raw_by_id = load_raw_outputs_by_id(raw_path)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    raw_stub = stub_model_raw_output()
    out_rows: list[dict[str, Any]] = []
    for row in records_in:
        if "id" not in row:
            print("Error: input row missing required field 'id'", file=sys.stderr)
            sys.exit(1)
        sample_id = str(row["id"])
        if args.mode == "stub":
            out_rows.append(normalize_model_output(sample_id, provenance, raw_stub))
        elif args.mode == "replay":
            raw = raw_by_id.get(sample_id)
            if raw is None:
                out_rows.append(
                    build_failure_record(
                        sample_id,
                        provenance,
                        error_type="missing_raw_output",
                        error_message=f"No raw_output for id {sample_id!r} in replay file.",
                        raw_output="",
                    )
                )
            else:
                out_rows.append(normalize_model_output(sample_id, provenance, raw))

    try:
        _write_jsonl(output_path, out_rows)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    ok_count = sum(1 for r in out_rows if r.get("normalization_status") == "ok")
    print(f"Wrote {len(out_rows)} prompt-eval records ({ok_count} ok) -> {output_path}")


if __name__ == "__main__":
    main()
