from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDNAMES = [
    "id",
    "primary_label",
    "risk_flags",
    "criticality",
    "explanation",
    "expected_label",
    "matches_expected",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export RDE JSONL results.")
    parser.add_argument("--input", required=True, help="Input JSONL result file.")
    parser.add_argument("--format", default="csv", choices=["csv"], help="Export format.")
    parser.add_argument("--output", required=True, help="Output file path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _load_jsonl(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            normalized = {field: row.get(field) for field in FIELDNAMES}
            normalized["risk_flags"] = ",".join(row.get("risk_flags") or [])
            writer.writerow(normalized)

    print(f"Exported {len(rows)} rows -> {args.output}")


def _load_jsonl(path: str) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    main()
