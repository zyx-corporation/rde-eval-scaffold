"""Tests for ``scripts/compare_annotations``."""

from __future__ import annotations

from compare_annotations import candidate_is_normalized, compare_annotations


def test_candidate_is_normalized_legacy_rows() -> None:
    assert candidate_is_normalized({"id": "x", "llm_annotation": "Preserved"})


def test_candidate_is_normalized_failed_row() -> None:
    assert not candidate_is_normalized(
        {"id": "x", "normalization_status": "failed", "error_type": "api_error"}
    )


def test_compare_skips_failed_candidate_normalization() -> None:
    ref = [
        {"id": "a", "human_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
        {
            "id": "b",
            "human_annotation": "Suspicious Drift",
            "risk_flags": [],
            "criticality": "high",
        },
    ]
    cand = [
        {"id": "a", "llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
        {
            "id": "b",
            "normalization_status": "failed",
            "error_type": "invalid_json",
            "raw_output": "not json",
        },
    ]
    result = compare_annotations(ref, cand)
    assert result["comparable"] == 1
    assert result["candidate_normalization_failed"] == ["b"]
    assert result["label_agreement"] == 1.0
