from __future__ import annotations

import pytest

from rde_eval.schema import EvaluationResult, RdeLabel, RdeSample


def test_sample_from_dict_accepts_required_fields() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "sample-001",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "This policy may reduce risk.",
            "output": "This policy reduces risk.",
        }
    )

    assert sample.id == "sample-001"
    assert sample.task == "summarization"


def test_sample_from_dict_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError):
        RdeSample.from_dict({"id": "sample-001"})


def test_evaluation_result_matches_expected() -> None:
    result = EvaluationResult(
        id="sample-001",
        primary_label=RdeLabel.SUSPICIOUS_DRIFT,
        risk_flags=["uncertainty_loss"],
        criticality="medium",  # type: ignore[arg-type]
        explanation="test",
        expected_label="Suspicious Drift",
    )

    assert result.matches_expected is True
    assert result.to_dict()["matches_expected"] is True
