#!/usr/bin/env python3
"""Merge human annotation records into pilot JSONL samples by ``id``.

``data/pilot_30.jsonl`` may contain placeholder labels; authoritative primary
annotations from ``annotate_pilot.py`` live in ``data/annotations/annotations.jsonl``.
This CLI writes one JSON object per pilot line with annotation fields overlaid.

Example:

    PYTHONPATH=. python scripts/merge_pilot_human_labels.py \\
      --pilot data/pilot_30.jsonl \\
      --annotations data/annotations/annotations.jsonl \\
      --output results/pilot_30_with_human.jsonl

The ``rde_eval`` package is not imported; editable install is optional.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge pilot JSONL with human annotation JSONL (matched by id).",
    )
    parser.add_argument("--pilot", required=True, type=Path, help="Pilot corpus JSONL.")
    parser.add_argument(
        "--annotations",
        required=True,
        type=Path,
        help="Human annotation JSONL from annotate_pilot or equivalent.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output JSONL path.")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: line {line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}: line {line_number}: expected JSON object")
            rows.append(row)
    return rows


def index_annotations(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        raw_id = row.get("id")
        if raw_id is None:
            raise ValueError("annotation row missing 'id'")
        sid = str(raw_id)
        if sid in by_id:
            raise ValueError(f"duplicate annotation id: {sid!r}")
        by_id[sid] = row
    return by_id


def merge_pilot_rows(
    pilot_rows: list[dict[str, Any]],
    annotation_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for row in pilot_rows:
        raw_id = row.get("id")
        if raw_id is None:
            raise ValueError("pilot row missing 'id'")
        sid = str(raw_id)
        anno = annotation_by_id.get(sid)
        if anno is None:
            raise ValueError(f"no annotation for pilot id: {sid!r}")
        out = dict(row)
        for key, value in anno.items():
            if key == "id":
                continue
            out[key] = value
        merged.append(out)
    return merged


def main() -> None:
    args = parse_args()
    pilot_path = args.pilot
    anno_path = args.annotations
    output_path = args.output
    try:
        pilot_rows = load_jsonl(pilot_path)
        anno_rows = load_jsonl(anno_path)
        annotation_by_id = index_annotations(anno_rows)
        merged = merge_pilot_rows(pilot_rows, annotation_by_id)
        pilot_ids = {str(r.get("id")) for r in pilot_rows if r.get("id") is not None}
        extra = set(annotation_by_id) - pilot_ids
        if extra:
            raise ValueError(
                "annotation ids not present in pilot file: " + ", ".join(sorted(extra)[:10])
                + (" ..." if len(extra) > 10 else "")
            )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in merged:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(merged)} rows -> {output_path}")


if __name__ == "__main__":
    main()
