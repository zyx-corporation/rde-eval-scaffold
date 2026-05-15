#!/usr/bin/env python3
"""Milestone 2 prompt-evaluator pipeline entrypoint.

Reads pilot-style JSONL and writes normalized LLM annotation JSONL per
``docs/prompt_evaluator_io_contract.md``.

Modes:
  stub   — fixed in-process JSON per row (no network)
  replay — normalize captured ``raw_output`` rows from ``--raw-jsonl``
  live   — OpenAI-compatible chat API per row, then normalize
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rde_eval.llm_client import LlmApiError, chat_completion
from rde_eval.prompt_eval import (
    build_failure_record,
    extract_prompt_input,
    load_raw_outputs_by_id,
    normalize_model_output,
    stub_model_raw_output,
)
from rde_eval.prompt_template import PROMPT_VERSION_V1, build_chat_messages


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


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def evaluate_row(
    row: dict[str, Any],
    *,
    mode: str,
    provenance: dict[str, str],
    raw_stub: str,
    raw_by_id: dict[str, str],
    prompt_version: str,
    llm_call: Callable[[list[dict[str, str]]], str] | None = None,
) -> tuple[dict[str, Any], str | None]:
    """Evaluate one pilot row.

    Returns ``(normalized_record, raw_capture)``. *raw_capture* is set only in
    live mode when the API returns a body (including when normalization later fails).
    """
    if "id" not in row:
        raise ValueError("input row missing required field 'id'")
    sample_id = str(row["id"])

    if mode == "stub":
        return normalize_model_output(sample_id, provenance, raw_stub), None

    if mode == "replay":
        raw = raw_by_id.get(sample_id)
        if raw is None:
            return (
                build_failure_record(
                    sample_id,
                    provenance,
                    error_type="missing_raw_output",
                    error_message=f"No raw_output for id {sample_id!r} in replay file.",
                    raw_output="",
                ),
                None,
            )
        return normalize_model_output(sample_id, provenance, raw), None

    if mode == "live":
        if llm_call is None:
            raise ValueError("live mode requires llm_call")
        prompt_input = extract_prompt_input(row)
        messages = build_chat_messages(prompt_input, prompt_version=prompt_version)
        try:
            raw_output = llm_call(messages)
        except LlmApiError as exc:
            return (
                build_failure_record(
                    sample_id,
                    provenance,
                    error_type="api_error",
                    error_message=str(exc),
                    raw_output="",
                ),
                None,
            )
        return normalize_model_output(sample_id, provenance, raw_output), raw_output

    raise ValueError(f"Unknown mode: {mode!r}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Milestone 2 prompt evaluator (stub / replay / live OpenAI-compatible API)."
    )
    parser.add_argument(
        "--input", required=True, help="Input pilot JSONL (e.g. data/pilot_30.jsonl)."
    )
    parser.add_argument("--output", required=True, help="Output JSONL path for normalized records.")
    parser.add_argument(
        "--mode",
        choices=("stub", "replay", "live"),
        default="stub",
        help="stub | replay (--raw-jsonl) | live (chat API).",
    )
    parser.add_argument(
        "--raw-jsonl",
        help="Replay mode: JSONL with id + raw_output per line (model capture).",
    )
    parser.add_argument(
        "--api-base-url",
        default="https://api.openai.com/v1",
        help="Live mode: API base URL (OpenAI-compatible /chat/completions).",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Live mode: environment variable holding the API key.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=120.0,
        help="Live mode: HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N input rows (useful for dry-runs).",
    )
    parser.add_argument(
        "--raw-captures-out",
        help="Live mode: append id + raw_output JSONL for replay (--mode replay).",
    )
    parser.add_argument("--annotator-type", default="llm", help="Provenance: annotator_type.")
    parser.add_argument("--annotator-id", default="stub", help="Provenance: annotator_id.")
    parser.add_argument("--model", default="stub-model", help="Provenance / live: model id.")
    parser.add_argument(
        "--prompt-version",
        default=None,
        help="Prompt template version (default: stub-v1 for stub, rde-prompt-eval-v1 for live).",
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

    if args.mode == "live" and args.model == "stub-model":
        print("Error: --mode live requires --model (not stub-model)", file=sys.stderr)
        sys.exit(1)

    if args.raw_captures_out and args.mode != "live":
        print("Error: --raw-captures-out is only valid with --mode live", file=sys.stderr)
        sys.exit(1)

    prompt_version = args.prompt_version
    if prompt_version is None:
        prompt_version = PROMPT_VERSION_V1 if args.mode == "live" else "rde-prompt-eval-stub-v1"

    provenance = {
        "annotator_type": args.annotator_type,
        "annotator_id": args.annotator_id,
        "model": args.model,
        "prompt_version": prompt_version,
        "annotation_run_id": args.annotation_run_id,
    }

    try:
        records_in = _load_jsonl_objects(input_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.limit is not None:
        if args.limit < 1:
            print("Error: --limit must be >= 1", file=sys.stderr)
            sys.exit(1)
        records_in = records_in[: args.limit]

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

    llm_call: Callable[[list[dict[str, str]]], str] | None = None
    if args.mode == "live":
        api_key = os.environ.get(args.api_key_env, "")
        if not api_key.strip():
            print(
                f"Error: live mode requires {args.api_key_env} to be set in the environment.",
                file=sys.stderr,
            )
            sys.exit(1)

        def _call(messages: list[dict[str, str]]) -> str:
            return chat_completion(
                messages,
                model=args.model,
                api_key=api_key,
                base_url=args.api_base_url,
                timeout_sec=args.timeout_sec,
            )

        llm_call = _call

    raw_stub = stub_model_raw_output()
    captures_path = Path(args.raw_captures_out) if args.raw_captures_out else None
    if captures_path is not None and captures_path.exists():
        captures_path.unlink()

    out_rows: list[dict[str, Any]] = []
    try:
        for row in records_in:
            rec, raw_capture = evaluate_row(
                row,
                mode=args.mode,
                provenance=provenance,
                raw_stub=raw_stub,
                raw_by_id=raw_by_id,
                prompt_version=prompt_version,
                llm_call=llm_call,
            )
            out_rows.append(rec)
            if raw_capture is not None and captures_path is not None:
                _append_jsonl(
                    captures_path,
                    {"id": str(row["id"]), "raw_output": raw_capture},
                )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        _write_jsonl(output_path, out_rows)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    ok_count = sum(1 for r in out_rows if r.get("normalization_status") == "ok")
    msg = f"Wrote {len(out_rows)} prompt-eval records ({ok_count} ok) -> {output_path}"
    if captures_path is not None:
        msg += f"; raw captures -> {captures_path}"
    print(msg)


if __name__ == "__main__":
    main()
