"""Ensure human pilot annotations cover every pilot_30.jsonl sample."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_annotations_cover_all_pilot30_ids() -> None:
    pilot_ids: list[str] = []
    for line in (REPO_ROOT / "data" / "pilot_30.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            pilot_ids.append(json.loads(line)["id"])

    anno_ids: list[str] = []
    anno_path = REPO_ROOT / "data" / "annotations" / "annotations.jsonl"
    for line in anno_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            anno_ids.append(json.loads(line)["id"])

    assert len(pilot_ids) == 30
    assert set(anno_ids) == set(pilot_ids)


def test_annotation_rows_match_pilot_tasks_ten_each() -> None:
    pilot_task: dict[str, str] = {}
    for line in (REPO_ROOT / "data" / "pilot_30.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            pilot_task[r["id"]] = r["task"]

    counts: dict[str, int] = {}
    for line in (
        (REPO_ROOT / "data" / "annotations" / "annotations.jsonl")
        .read_text(
            encoding="utf-8",
        )
        .splitlines()
    ):
        if line.strip():
            row = json.loads(line)
            t = pilot_task[row["id"]]
            counts[t] = counts.get(t, 0) + 1

    assert counts == {
        "summarization": 10,
        "rewriting": 10,
        "specification_conversion": 10,
    }
