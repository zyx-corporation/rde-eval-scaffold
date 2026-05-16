"""Tests for ``scripts/merge_pilot_human_labels.py``."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "merge_pilot_human_labels.py"


def test_merge_prefers_annotation_fields(tmp_path: Path) -> None:
    pilot_path = tmp_path / "p.jsonl"
    anno_path = tmp_path / "a.jsonl"
    out_path = tmp_path / "out.jsonl"

    pilot_path.write_text(
        json.dumps({"id": "x-1", "source": "a", "output": "b", "human_annotation": "Preserved"})
        + "\n",
        encoding="utf-8",
    )
    anno_path.write_text(
        json.dumps(
            {
                "id": "x-1",
                "human_annotation": "Critical Distortion",
                "risk_flags": ["uncertainty_loss"],
            },
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--pilot",
            str(pilot_path),
            "--annotations",
            str(anno_path),
            "--output",
            str(out_path),
        ],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )

    row = json.loads(out_path.read_text(encoding="utf-8").strip().splitlines()[0])
    assert row["human_annotation"] == "Critical Distortion"
    assert row["risk_flags"] == ["uncertainty_loss"]
    assert row["source"] == "a"


def test_merge_reports_missing_annotation(tmp_path: Path) -> None:
    pilot_path = tmp_path / "p.jsonl"
    anno_path = tmp_path / "a.jsonl"
    pilot_path.write_text(
        json.dumps({"id": "one", "source": "a", "output": "b"}) + "\n"
        + json.dumps({"id": "two", "source": "c", "output": "d"})
        + "\n",
        encoding="utf-8",
    )
    anno_path.write_text(
        json.dumps({"id": "one", "human_annotation": "Preserved"}) + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--pilot",
            str(pilot_path),
            "--annotations",
            str(anno_path),
            "--output",
            str(tmp_path / "out.jsonl"),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "no annotation" in proc.stderr


def test_merge_repo_pilot_matches_annotations_overlay(tmp_path: Path) -> None:
    pilot = REPO_ROOT / "data" / "pilot_30.jsonl"
    anno = REPO_ROOT / "data" / "annotations" / "annotations.jsonl"
    out_path = tmp_path / "merged.jsonl"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--pilot",
            str(pilot),
            "--annotations",
            str(anno),
            "--output",
            str(out_path),
        ],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )

    anno_map: dict[str, dict] = {}
    for line in anno.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            anno_map[row["id"]] = row

    merged_lines = [ln for ln in out_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(merged_lines) == 30

    pilot_sum001 = json.loads(merged_lines[0])
    assert pilot_sum001["id"] == "pilot-sum-001"
    assert pilot_sum001["human_annotation"] == anno_map["pilot-sum-001"]["human_annotation"]
