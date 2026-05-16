"""Sanity-check committed JSONL fixtures."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_m3_nli_notebook_smoke_fixture() -> None:
    path = REPO_ROOT / "data" / "fixtures" / "m3_nli_notebook_smoke.jsonl"
    assert path.is_file()
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    assert len(rows) == 3
    truncated_flags = [
        (r.get("baseline_scores") or {}).get("m3", {}).get("nli", {}).get("truncated") for r in rows
    ]
    assert True in truncated_flags
    assert False in truncated_flags
