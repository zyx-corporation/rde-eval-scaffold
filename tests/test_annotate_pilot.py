"""Tests for scripts/annotate_pilot.py — written TDD-first before implementation."""

from __future__ import annotations

import json

import annotate_pilot as ap
import pytest

# ---------------------------------------------------------------------------
# parse_label_choice
# ---------------------------------------------------------------------------


def test_parse_label_choice_returns_preserved():
    assert ap.parse_label_choice("1") == "Preserved"


def test_parse_label_choice_returns_suspicious_drift():
    assert ap.parse_label_choice("5") == "Suspicious Drift"


def test_parse_label_choice_returns_critical_distortion():
    assert ap.parse_label_choice("6") == "Critical Distortion"


def test_parse_label_choice_returns_authorized_transformation():
    assert ap.parse_label_choice("2") == "Authorized Transformation"


def test_parse_label_choice_rejects_unknown_key():
    with pytest.raises(ValueError, match="無効な選択"):
        ap.parse_label_choice("9")


def test_parse_label_choice_rejects_empty_string():
    with pytest.raises(ValueError, match="無効な選択"):
        ap.parse_label_choice("")


# ---------------------------------------------------------------------------
# parse_risk_flags
# ---------------------------------------------------------------------------


def test_parse_risk_flags_single_letter():
    flags = ap.parse_risk_flags("a")
    assert flags == ["claim_strength_inflation"]


def test_parse_risk_flags_multiple_letters():
    flags = ap.parse_risk_flags("ab")
    assert set(flags) == {"claim_strength_inflation", "uncertainty_loss"}


def test_parse_risk_flags_comma_separated():
    flags = ap.parse_risk_flags("a,c")
    assert set(flags) == {"claim_strength_inflation", "responsibility_shift"}


def test_parse_risk_flags_empty_string_returns_empty_list():
    assert ap.parse_risk_flags("") == []


def test_parse_risk_flags_none_returns_empty_list():
    assert ap.parse_risk_flags(None) == []


def test_parse_risk_flags_whitespace_only_returns_empty_list():
    assert ap.parse_risk_flags("   ") == []


def test_parse_risk_flags_all_flags():
    result = ap.parse_risk_flags("abcdefg")
    assert len(result) == 7
    assert "claim_strength_inflation" in result
    assert "theoretical_reduction" in result


def test_parse_risk_flags_rejects_unknown_key():
    with pytest.raises(ValueError, match="無効なリスクフラグ"):
        ap.parse_risk_flags("z")


def test_parse_risk_flags_deduplicates():
    flags = ap.parse_risk_flags("aa")
    assert flags.count("claim_strength_inflation") == 1


# ---------------------------------------------------------------------------
# parse_criticality_choice
# ---------------------------------------------------------------------------


def test_parse_criticality_low():
    assert ap.parse_criticality_choice("1") == "low"


def test_parse_criticality_medium():
    assert ap.parse_criticality_choice("2") == "medium"


def test_parse_criticality_high():
    assert ap.parse_criticality_choice("3") == "high"


def test_parse_criticality_rejects_unknown_key():
    with pytest.raises(ValueError, match="無効な選択"):
        ap.parse_criticality_choice("5")


# ---------------------------------------------------------------------------
# format_annotation
# ---------------------------------------------------------------------------


def test_format_annotation_has_required_keys():
    record = ap.format_annotation(
        sample_id="pilot-001",
        human_annotation="Preserved",
        risk_flags=[],
        criticality="low",
        explanation="問題なし。",
        annotator="tester",
    )
    assert record["id"] == "pilot-001"
    assert record["human_annotation"] == "Preserved"
    assert record["risk_flags"] == []
    assert record["criticality"] == "low"
    assert record["explanation"] == "問題なし。"
    assert record["annotator"] == "tester"
    assert "annotated_at" in record


def test_format_annotation_canonical_values_only():
    record = ap.format_annotation(
        sample_id="pilot-002",
        human_annotation="Critical Distortion",
        risk_flags=["claim_strength_inflation", "uncertainty_loss"],
        criticality="high",
        explanation="意味が逆転している。",
        annotator="tester",
    )
    assert record["human_annotation"] == "Critical Distortion"
    assert "claim_strength_inflation" in record["risk_flags"]
    assert record["criticality"] == "high"


def test_format_annotation_annotated_at_is_iso8601():
    from datetime import datetime

    record = ap.format_annotation(
        sample_id="x",
        human_annotation="Preserved",
        risk_flags=[],
        criticality="low",
        explanation="ok",
        annotator="tester",
    )
    # Must parse without error
    dt = datetime.fromisoformat(record["annotated_at"])
    assert dt.tzinfo is not None  # must be timezone-aware


# ---------------------------------------------------------------------------
# load_annotated_ids
# ---------------------------------------------------------------------------


def test_load_annotated_ids_empty_dir(tmp_path):
    ids = ap.load_annotated_ids(tmp_path)
    assert ids == set()


def test_load_annotated_ids_reads_single_file(tmp_path):
    f = tmp_path / "ann.jsonl"
    f.write_text(
        json.dumps({"id": "pilot-001", "human_annotation": "Preserved"}) + "\n"
        + json.dumps({"id": "pilot-002", "human_annotation": "Critical Distortion"}) + "\n"
    )
    ids = ap.load_annotated_ids(tmp_path)
    assert ids == {"pilot-001", "pilot-002"}


def test_load_annotated_ids_reads_multiple_files(tmp_path):
    (tmp_path / "a.jsonl").write_text(json.dumps({"id": "a-001"}) + "\n")
    (tmp_path / "b.jsonl").write_text(json.dumps({"id": "b-001"}) + "\n")
    ids = ap.load_annotated_ids(tmp_path)
    assert "a-001" in ids
    assert "b-001" in ids


def test_load_annotated_ids_ignores_non_jsonl_files(tmp_path):
    (tmp_path / "notes.txt").write_text("some notes\n")
    (tmp_path / "ann.jsonl").write_text(json.dumps({"id": "pilot-003"}) + "\n")
    ids = ap.load_annotated_ids(tmp_path)
    assert ids == {"pilot-003"}


def test_load_annotated_ids_skips_lines_without_id(tmp_path):
    f = tmp_path / "ann.jsonl"
    f.write_text(
        json.dumps({"human_annotation": "Preserved"}) + "\n"  # no id
        + json.dumps({"id": "pilot-004"}) + "\n"
    )
    ids = ap.load_annotated_ids(tmp_path)
    assert ids == {"pilot-004"}


# ---------------------------------------------------------------------------
# load_pilot_records
# ---------------------------------------------------------------------------


def test_load_pilot_records_returns_list(tmp_path):
    f = tmp_path / "pilot.jsonl"
    f.write_text(
        json.dumps({"id": "p-001", "source_ja": "テスト", "output_ja": "出力"}) + "\n"
        + json.dumps({"id": "p-002", "source_ja": "テスト2", "output_ja": "出力2"}) + "\n"
    )
    records = ap.load_pilot_records(f)
    assert len(records) == 2
    assert records[0]["id"] == "p-001"


def test_load_pilot_records_skips_blank_lines(tmp_path):
    f = tmp_path / "pilot.jsonl"
    f.write_text(
        json.dumps({"id": "p-001"}) + "\n"
        + "\n"
        + json.dumps({"id": "p-002"}) + "\n"
    )
    records = ap.load_pilot_records(f)
    assert len(records) == 2


# ---------------------------------------------------------------------------
# append_annotation
# ---------------------------------------------------------------------------


def test_append_annotation_creates_file_and_writes_jsonl(tmp_path):
    out_file = tmp_path / "ann.jsonl"
    record = {"id": "pilot-001", "human_annotation": "Preserved"}
    ap.append_annotation(out_file, record)
    lines = out_file.read_text().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["id"] == "pilot-001"


def test_append_annotation_appends_to_existing_file(tmp_path):
    out_file = tmp_path / "ann.jsonl"
    ap.append_annotation(out_file, {"id": "pilot-001"})
    ap.append_annotation(out_file, {"id": "pilot-002"})
    lines = out_file.read_text().splitlines()
    assert len(lines) == 2


# ---------------------------------------------------------------------------
# Resume behavior integration
# ---------------------------------------------------------------------------


def test_resume_skips_already_annotated_ids(tmp_path):
    """load_annotated_ids returns a set that callers use to filter records."""
    ann_dir = tmp_path / "annotations"
    ann_dir.mkdir()
    (ann_dir / "session1.jsonl").write_text(json.dumps({"id": "pilot-001"}) + "\n")

    pilot_file = tmp_path / "pilot.jsonl"
    pilot_file.write_text(
        json.dumps({"id": "pilot-001", "source_ja": "a", "output_ja": "b"}) + "\n"
        + json.dumps({"id": "pilot-002", "source_ja": "c", "output_ja": "d"}) + "\n"
    )

    already_done = ap.load_annotated_ids(ann_dir)
    records = ap.load_pilot_records(pilot_file)
    pending = [r for r in records if r["id"] not in already_done]

    assert len(pending) == 1
    assert pending[0]["id"] == "pilot-002"
