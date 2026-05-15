"""Tests for Milestone 2 prompt evaluator normalization (``rde_eval.prompt_eval``)."""

from __future__ import annotations

import json

import pytest

from rde_eval.prompt_eval import (
    build_failure_record,
    build_success_record,
    extract_prompt_input,
    normalize_model_output,
    parse_raw_model_output,
    stub_model_raw_output,
    validate_llm_payload,
)


def _prov() -> dict[str, str]:
    return {
        "annotator_type": "llm",
        "annotator_id": "test",
        "model": "m1",
        "prompt_version": "pv1",
        "annotation_run_id": "run-1",
    }


def test_extract_prompt_input_includes_canonical_and_ja() -> None:
    row = {
        "id": "p-1",
        "task": "summarization",
        "risk_context": "x",
        "source": "en s",
        "output": "en o",
        "task_intent": "ti",
        "source_ja": "日ソース",
        "noise": "ignored",
    }
    got = extract_prompt_input(row)
    assert got["id"] == "p-1"
    assert got["task"] == "summarization"
    assert got["source_ja"] == "日ソース"
    assert "noise" not in got


def test_parse_raw_model_output_invalid_json() -> None:
    parsed, err = parse_raw_model_output("{not json")
    assert parsed is None
    assert err is not None


def test_parse_raw_model_output_non_object() -> None:
    parsed, err = parse_raw_model_output("[1,2]")
    assert parsed is None
    assert err is not None


def test_validate_llm_payload_unknown_label() -> None:
    ok, et, _ = validate_llm_payload(
        {
            "llm_annotation": "Nope",
            "risk_flags": [],
            "criticality": "low",
        }
    )
    assert not ok
    assert et == "invalid_label"


def test_validate_llm_payload_unknown_flag() -> None:
    ok, et, _ = validate_llm_payload(
        {
            "llm_annotation": "Preserved",
            "risk_flags": ["not_a_flag"],
            "criticality": "low",
        }
    )
    assert not ok
    assert et == "invalid_risk_flag"


def test_normalize_model_output_success() -> None:
    raw = json.dumps(
        {
            "llm_annotation": "Suspicious Drift",
            "risk_flags": ["uncertainty_loss"],
            "criticality": "medium",
            "explanation": "x",
            "explanation_ja": "あ",
        }
    )
    rec = normalize_model_output("id-1", _prov(), raw)
    assert rec["normalization_status"] == "ok"
    assert rec["llm_annotation"] == "Suspicious Drift"
    assert rec["risk_flags"] == ["uncertainty_loss"]
    assert rec["criticality"] == "medium"
    assert rec["raw_output"] == raw
    assert rec["annotator_id"] == "test"


def test_normalize_model_output_failed_json() -> None:
    rec = normalize_model_output("id-1", _prov(), "not json")
    assert rec["normalization_status"] == "failed"
    assert rec["error_type"] == "invalid_json"
    assert "raw_output" in rec


def test_build_failure_record_requires_provenance() -> None:
    with pytest.raises(ValueError, match="Missing provenance"):
        build_failure_record(
            "x",
            {"annotator_type": "llm"},
            error_type="x",
            error_message="m",
            raw_output="{}",
        )


def test_stub_model_raw_output_normalizes_ok() -> None:
    raw = stub_model_raw_output()
    rec = normalize_model_output("any-id", _prov(), raw)
    assert rec["normalization_status"] == "ok"
    assert rec["llm_annotation"] == "Preserved"


def test_build_success_record_omits_blank_explanations() -> None:
    rec = build_success_record(
        "z",
        _prov(),
        {"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
        "{}",
    )
    assert "explanation" not in rec
    assert "explanation_ja" not in rec
