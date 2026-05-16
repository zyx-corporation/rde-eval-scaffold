"""Smoke tests for issue #58 reference placeholder JSONL and compare CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPARE_SCRIPT = REPO_ROOT / "scripts" / "compare_annotations.py"


def test_placeholder_annotation_file_covers_all_pilot_ids() -> None:
    pilot_ids: list[str] = []
    for line in (REPO_ROOT / "data" / "pilot_30.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            pilot_ids.append(json.loads(line)["id"])

    path = REPO_ROOT / "data" / "annotations" / "pilot_30_reference_placeholder.jsonl"
    seen: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            seen[row["id"]] = row

    assert sorted(seen) == sorted(pilot_ids)
    assert all(row.get("reference_placeholder") is True for row in seen.values())
    assert "PLACEHOLDER" in seen[pilot_ids[0]]["explanation"].upper()


def test_compare_placeholder_vs_deepseek_smoke_cli(tmp_path: Path) -> None:
    placeholder = REPO_ROOT / "data" / "annotations" / "pilot_30_reference_placeholder.jsonl"
    deepseek = REPO_ROOT / "data" / "annotations" / "pilot_30_deepseek.jsonl"
    pilot30 = REPO_ROOT / "data" / "pilot_30.jsonl"
    for p in (placeholder, deepseek, pilot30):
        assert p.is_file(), str(p)

    out = tmp_path / "comparison.json"
    subprocess.run(
        [
            sys.executable,
            str(COMPARE_SCRIPT),
            "--reference",
            str(placeholder),
            "--candidate",
            str(deepseek),
            "--source",
            str(pilot30),
            "--output",
            str(out),
        ],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )

    blob = json.loads(out.read_text(encoding="utf-8"))
    assert blob["total"] == 30
    assert blob["comparable"] == 30
    assert blob["source_id_coverage"]["missing_in_source"] == []
    assert isinstance(blob["label_agreement"], float)
