from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rde_eval.schema import KNOWN_RISK_FLAGS, PRIMARY_LABEL_VALUES


def load_dataset() -> list[dict]:
    repo_root = Path(__file__).resolve().parent.parent
    path = repo_root / "data" / "pilot_30.jsonl"
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            records.append(json.loads(line))
    return records


def test_pilot_dataset_count() -> None:
    records = load_dataset()
    assert len(records) == 30


def test_pilot_dataset_task_distribution() -> None:
    records = load_dataset()
    counts = Counter(record["task"] for record in records)
    assert counts["summarization"] == 10
    assert counts["rewriting"] == 10
    assert counts["specification_conversion"] == 10


def test_pilot_dataset_labels_are_valid() -> None:
    records = load_dataset()
    for record in records:
        assert record["human_annotation"] in PRIMARY_LABEL_VALUES


def test_pilot_dataset_risk_flags_are_valid() -> None:
    records = load_dataset()
    for record in records:
        for flag in record.get("risk_flags", []):
            assert flag in KNOWN_RISK_FLAGS


def test_pilot_dataset_contains_japanese_review_fields() -> None:
    records = load_dataset()
    required_ja_fields = {
        "source_ja",
        "output_ja",
        "explanation_ja",
        "task_intent_ja",
        "reconstructed_task_intent_ja",
        "task_intent_notes_ja",
    }
    for record in records:
        for field in required_ja_fields:
            assert field in record
            assert isinstance(record[field], str)
            assert record[field]
