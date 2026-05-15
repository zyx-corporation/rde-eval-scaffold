"""Unit tests for ``rde_eval.baselines``."""

from __future__ import annotations

from rde_eval.baselines import (
    M3_LEXICAL_METHOD,
    lexical_sequence_ratio,
    merge_milestone3_baseline,
    milestone3_lexical_scores,
)


def test_lexical_sequence_ratio_identity() -> None:
    assert lexical_sequence_ratio("same", "same") == 1.0


def test_lexical_sequence_ratio_range() -> None:
    r = lexical_sequence_ratio("abc", "xyz")
    assert 0.0 <= r <= 1.0


def test_milestone3_lexical_scores_shape() -> None:
    got = milestone3_lexical_scores("a", "b")
    assert got["method"] == M3_LEXICAL_METHOD
    assert isinstance(got["sequence_ratio"], float)


def test_merge_preserves_non_m3_keys() -> None:
    existing = {"bertscore": {"f1": 0.5}}
    merged = merge_milestone3_baseline(existing, source="hello", output="hello")
    assert merged["bertscore"] == {"f1": 0.5}
    assert merged["m3"]["version"] == "1"
    assert merged["m3"]["lexical"]["sequence_ratio"] == 1.0


def test_merge_overwrites_m3_lexical() -> None:
    existing = {
        "m3": {"version": "1", "lexical": {"sequence_ratio": 0.1, "method": M3_LEXICAL_METHOD}}
    }
    merged = merge_milestone3_baseline(existing, source="x", output="x")
    assert merged["m3"]["lexical"]["sequence_ratio"] == 1.0


def test_merge_with_bertscore_bumps_version() -> None:
    merged = merge_milestone3_baseline(
        {},
        source="a",
        output="b",
        bertscore={
            "f1": 0.5,
            "precision": 0.4,
            "recall": 0.6,
            "lang": "en",
            "method": "bert-score",
        },
    )
    assert merged["m3"]["version"] == "2"
    assert merged["m3"]["bertscore"]["f1"] == 0.5


def test_merge_nli_bumps_version_and_keeps_bertscore() -> None:
    bert = {
        "f1": 0.8,
        "precision": 0.8,
        "recall": 0.8,
        "lang": "en",
        "method": "bert-score",
    }
    with_bs = merge_milestone3_baseline({}, source="s", output="o", bertscore=bert)
    nli_block = {
        "method": "transformers-sequence-classification",
        "model_id": "test-model",
        "premise": "source",
        "hypothesis": "output",
        "label": "neutral",
        "scores": {"entailment": 0.1, "neutral": 0.7, "contradiction": 0.2},
    }
    merged = merge_milestone3_baseline(with_bs, source="s", output="o", nli=nli_block)
    assert merged["m3"]["version"] == "3"
    assert merged["m3"]["bertscore"]["f1"] == 0.8
    assert merged["m3"]["nli"]["label"] == "neutral"


def test_merge_nli_only_version_three() -> None:
    nli_block = {
        "method": "transformers-sequence-classification",
        "model_id": "m",
        "premise": "source",
        "hypothesis": "output",
        "label": "entailment",
        "scores": {"entailment": 0.9},
    }
    merged = merge_milestone3_baseline({}, source="a", output="b", nli=nli_block)
    assert merged["m3"]["version"] == "3"
    assert "bertscore" not in merged["m3"]
