from __future__ import annotations

import json
from pathlib import Path

from rde_eval.schema import KNOWN_RISK_FLAGS, PRIMARY_LABEL_VALUES

VALID_CRITICALITY = {"low", "medium", "high"}


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_pilot_ids() -> set[str]:
    records = _load_jsonl(_repo_root() / "data" / "pilot_30.jsonl")
    return {str(record["id"]) for record in records}


def load_deepseek_annotations() -> list[dict]:
    return _load_jsonl(_repo_root() / "data" / "annotations" / "pilot_30_deepseek.jsonl")


def test_deepseek_annotation_count() -> None:
    records = load_deepseek_annotations()
    assert len(records) == 30


def test_deepseek_annotation_ids_match_pilot_dataset() -> None:
    pilot_ids = load_pilot_ids()
    records = load_deepseek_annotations()
    annotation_ids = {str(record["id"]) for record in records}
    assert annotation_ids == pilot_ids


def test_deepseek_annotation_provenance_fields() -> None:
    records = load_deepseek_annotations()
    for record in records:
        assert record["annotator_type"] == "llm"
        assert record["annotator_id"] == "deepseek"
        assert record["model"]
        assert record["prompt_version"]
        assert record["annotation_run_id"]


def test_deepseek_annotation_values_are_valid() -> None:
    records = load_deepseek_annotations()
    for record in records:
        assert record["llm_annotation"] in PRIMARY_LABEL_VALUES
        assert record["criticality"] in VALID_CRITICALITY
        for flag in record.get("risk_flags", []):
            assert flag in KNOWN_RISK_FLAGS


def test_deepseek_annotations_are_not_human_annotations() -> None:
    records = load_deepseek_annotations()
    for record in records:
        assert "human_annotation" not in record
        assert "llm_annotation" in record


def test_deepseek_annotation_explanations_are_japanese_text() -> None:
    records = load_deepseek_annotations()
    for record in records:
        explanation = record.get("explanation_ja")
        assert isinstance(explanation, str)
        assert explanation.strip()
