"""Tests for ``scripts/compare_annotations``."""

from __future__ import annotations

from compare_annotations import (
    candidate_is_normalized,
    compare_annotations,
    format_comparison_summary,
)


def test_candidate_is_normalized_legacy_rows() -> None:
    assert candidate_is_normalized({"id": "x", "llm_annotation": "Preserved"})


def test_candidate_is_normalized_failed_row() -> None:
    assert not candidate_is_normalized(
        {"id": "x", "normalization_status": "failed", "error_type": "api_error"}
    )



def test_compare_label_uses_human_on_reference_llm_on_candidate_only() -> None:
    ref = [
        {
            "id": "mix",
            "llm_annotation": "Preserved",
            "human_annotation": "Critical Distortion",
            "risk_flags": [],
            "criticality": "high",
        },
    ]
    cand = [
        {
            "id": "mix",
            "human_annotation": "Preserved",
            "llm_annotation": "Critical Distortion",
            "risk_flags": [],
            "criticality": "high",
        },
    ]
    result = compare_annotations(ref, cand)
    assert result["comparable"] == 1
    assert result["label_agreement"] == 1.0


def test_compare_candidate_without_llm_label_counts_mismatch() -> None:
    ref = [{"id": "a", "human_annotation": "Preserved", "risk_flags": [], "criticality": "low"}]
    cand = [{"id": "a", "human_annotation": "Preserved", "risk_flags": [], "criticality": "low"}]
    result = compare_annotations(ref, cand)
    assert result["label_agreement"] == 0.0


def test_compare_source_coverage_missing_union_id() -> None:
    ref = [{"id": "a", "human_annotation": "Preserved", "risk_flags": [], "criticality": "low"}]
    cand = [{"id": "a", "llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"}]
    result = compare_annotations(ref, cand, source_ids=set())
    cov = result.get("source_id_coverage")
    assert cov is not None
    assert cov["missing_in_source"] == ["a"]


def test_format_comparison_summary_with_source_warnings() -> None:
    result = {
        "total": 2,
        "comparable": 1,
        "label_agreement": 0.5,
        "criticality_agreement": 1.0,
        "risk_flag_exact_agreement": 1.0,
        "risk_flag_precision": 1.0,
        "risk_flag_recall": 1.0,
        "risk_flag_f1": 1.0,
        "disagreements": [{}],
        "candidate_normalization_failed": [],
        "source_id_coverage": {"missing_in_source": ["z"], "extra_in_source_only": ["y"]},
    }
    text = format_comparison_summary(result)
    assert "Source ID mismatches" in text


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


def test_format_comparison_summary_includes_key_metrics() -> None:
    result = {
        "total": 3,
        "comparable": 0,
        "label_agreement": 0.0,
        "criticality_agreement": 0.0,
        "risk_flag_exact_agreement": 0.0,
        "risk_flag_precision": 0.0,
        "risk_flag_recall": 0.0,
        "risk_flag_f1": 0.0,
        "disagreements": [],
        "candidate_normalization_failed": ["b"],
    }
    text = format_comparison_summary(result)
    assert "RDE annotation comparison summary" in text
    assert "Comparable pairs:               0" in text
    assert "Candidate normalization failed: 1" in text
    assert "100.0%" not in text
